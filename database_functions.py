from model_testing import *

init_app()

def add_anon_user():
    """Adds a user_id for a non-logged in user from the landing page."""

    next_id = get_last_user_id() + 1
    intake_user = User(user_id = next_id)
    db.session.add(intake_user)
    db.session.commit()

def get_last_user_id():
    """Queries database for last created user id."""

    user = User.query.order_by(User.user_id.desc()).first()

    return user.user_id

def get_last_rating_id():
    """Queries database for last created rating id."""

    rating = Rating.query.order_by(Rating.rating_id.desc()).first()

    return rating.rating_id

def get_book_id(isbn):
    """Gets a book id for database for a given ISBN"""

    book = Book.query.filter(Book.isbn==str(isbn)).first()

    return book.book_id


def add_rating(user_id, book_id, score=5):

    next_rating_id = get_last_rating_id() + 1
    rating = Rating(rating_id=next_rating_id, user_id=user_id, book_id=book_id, score=score)
    db.session.add(rating)
    db.session.commit()



# user = add_anon_user()
# print(user)

# user_id = get_last_user_id()
# print(user_id)
# print(type(user_id))


# book_id = get_book_id(isbn="375758771")
# print(book_id)
# print(type(book_id))

# rating_id = get_last_rating_id()
# print(rating_id)
# print(type(rating_id))

# rating = add_rating(user_id, book_id)
# print(rating)

"""
6161413
6178731
142407577
6513905
385349947

 385349947
 385350287
 385350813
 385350848
 385351232



"""

