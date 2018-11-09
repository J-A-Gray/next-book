"""Models and database functions for NextBook project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of NextBook website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    
    def __repr__(self):
        return f"<User user_id={self.user_id} email={self.email}>"

class Book(db.Model):
    """Books of NextBook website."""
    
    __tablename__ = "books"
    
    book_id = db.Column(db.Integer, primary_key=True) #book id from data set
    work_id = db.Column(db.Integer, unique=True) #maps to work_id in books.csv, but to book_id in ratings.csv
    isbn = db.Column(db.String(13), unique=True) #platform and dataset agnostic, generally all books post-1970 have one
    title = db.Column(db.String(600))
    author = db.Column(db.String(600))
    

    def __repr__(self):

        return f"<Book book_id={self.book_id} title={self.title} author={self.author}>"

class Rating(db.Model):
    """Rating of NextBook website."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer)

    book = db.relationship('Book',
                            backref=db.backref('ratings', order_by=rating_id))

    user = db.relationship('User', 
                            backref=db.backref('ratings', order_by=rating_id))

    def __repr__(self):

        return f"<Rating rating_id={self.rating_id} book_id={self.book_id} user_id={self.user_id} score={self.score}>"

##############################################################################
# Helper functions

def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB.")

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nextbook'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

   init_app()