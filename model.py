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
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB.")




def example_data():
    """Populate a databse with sample data for testing purposes."""

    db.create_all()


    #Empty out data from previous runs
    User.query.delete()
    Book.query.delete()
    Rating.query.delete()

    #Add sample users, books, and ratings

    #sample users
    user1 = User(user_id=1, email='123@test.com', password='password')
    user2 = User(user_id=2, email='456@test.com', password='password')
    user3 = User(user_id=3, email='789@test.com', password='password')
    user4 = User(user_id=4, email='987@test.com', password='password')
    user5 = User(user_id=5, email='654@test.com', password='password')

    #sample books
    book1 = Book(book_id=7627, work_id=16683183, isbn='7331789', title='Death of Kings (The Saxon Stories, #6)', author='Bernard Cornwell')
    book2 = Book(book_id=7695, work_id=16947613, isbn='7350430', title='The Time of My Life', author='Cecelia Ahern')
    book3 = Book(book_id=69, work_id=15524542, isbn='7442912', title='Insurgent (Divergent #2)', author='Veronica Roth')
    book4 = Book(book_id=3327, work_id=23906880, isbn='7491433', title='The Shock of the Fall', author='Nathan Filer')
    book5 = Book(book_id=8387, work_id=67116, isbn='99464691', title='The White Lioness (Kurt Wallander, #3)', author='Henning Mankell')


    #sample ratings
    rating1 = Rating(rating_id=1, book_id=7627, user_id=1, score=5)
    rating2 = Rating(rating_id=2, book_id=7627, user_id=2, score=5)
    rating3 = Rating(rating_id=3, book_id=7627, user_id=3, score=3)
    rating4 = Rating(rating_id=4, book_id=7627, user_id=4, score=3)
    rating5 = Rating(rating_id=5, book_id=7627, user_id=5, score=1)
    rating6 = Rating(rating_id=6, book_id=8387, user_id=1, score=5)
    rating7 = Rating(rating_id=7, book_id=8387, user_id=2, score=5)
    rating8 = Rating(rating_id=8, book_id=8387, user_id=3, score=3)
    rating9 = Rating(rating_id=9, book_id=8387, user_id=4, score=3)
    rating10 = Rating(rating_id=10, book_id=8387, user_id=5, score=1)

    #Add all to session and commit
    db.session.add_all([user1, user2, user3, user4, user5, book1, book2, book3, 
                        book4, book5, rating1, rating2, rating3, rating4, 
                        rating5, rating6, rating7, rating8, rating9, rating10])
    db.session.commit()

def connect_to_db(app, db_uri='postgresql:///nextbook'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    init_app()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
