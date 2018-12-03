"""Models and database functions for NextBook project."""

from flask_sqlalchemy import SQLAlchemy

# Already installed with Flask: 
# http://werkzeug.pocoo.org/docs/0.14/utils/#module-werkzeug.security
from werkzeug.security import generate_password_hash, check_password_hash 

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of NextBook website."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=True)
    password = db.Column(db.String(64), nullable=True)
    
    def __repr__(self):
        return f"<User user_id={self.user_id} email={self.email}>"


class Book(db.Model):
    """Books of NextBook website."""
    
    __tablename__ = "books"
    
    id = db.Column(db.Integer, primary_key=True) #book id from data set
    work_id = db.Column(db.Integer, unique=True) #maps to work_id in books.csv, but to book_id in ratings.csv
    isbn = db.Column(db.String(13), unique=True) #platform and dataset agnostic, generally all books post-1970 have one
    title = db.Column(db.String(600))
    author = db.Column(db.String(600))
    

    def __repr__(self):

        return f"<Book {self.book_id} | {self.title[:12]}, by {self.author}>"


class Rating(db.Model):
    """Rating of NextBook website."""

    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    score = db.Column(db.Integer)

    book = db.relationship('Book',
                            backref=db.backref('rating'))

    user = db.relationship('User', 
                            backref=db.backref('ratings'))

    def __repr__(self):

        return f"<Rating rating_id={self.rating_id} book_id={self.book_id} user_id={self.user_id} score={self.score}>"

##############################################################################
# Helper functions

def connect_to_db(app, dbname='nextbook'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql:///{dbname}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB.")


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")