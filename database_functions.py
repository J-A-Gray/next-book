from model import *

def add_anon_user():
    """Adds a user_id for a non-logged in user from the landing page."""

    next_id = get_last_user_id() + 1
    anon_user = User(user_id = next_id)
    db.session.add(anon_user)
    db.session.commit()

    return anon_user

def get_last_user_id():
    """Query database for last created user id."""

    user = User.query.order_by(User.user_id.desc()).first()

    return user.user_id

def get_last_rating_id():
    """Query database for last created rating id."""

    rating = Rating.query.order_by(Rating.rating_id.desc()).first()

    return rating.rating_id

def get_book_id(isbn):
    """Gets a book id for database for a given ISBN"""

    book = Book.query.filter(Book.isbn==str(isbn)).first()

    return book.book_id

def get_books_by_author(author):
    """Gets a list of book objects by a particular author"""

    books = Book.query.filter(Book.author==author).all()

    return books

def add_rating(user_id, book_id, score=5):

    next_rating_id = get_last_rating_id() + 1
    rating = Rating(rating_id=next_rating_id, user_id=user_id, book_id=book_id, score=score)
    db.session.add(rating)
    db.session.commit()

    return rating

def create_user_list(user_id):
    """Create a list of books rated by the user"""
    user_book_lst=[]
    ratings = Rating.query.filter_by(user_id=user_id).all()
    
    for rating in ratings:
        book_id = rating.book_id
        book = Book.query.filter(Book.book_id==book_id).first()
        user_book_lst.append(book)

    return user_book_lst

def create_neighbors_book_dict(neighbors_user_id_lst, user_book_lst, score):
    """Create a dictionary of Book objects rated by neighbors of user but not in users input"""

    neighbors_book_dict = {}
    for neighbor in neighbors_user_id_lst:
        user = User.query.get(int(neighbor))

        ratings = Rating.query.filter_by(user_id=user.user_id).all()

        for rating in ratings:
            if rating.score == score:
                book_id = rating.book_id
                book = Book.query.filter(Book.book_id==book_id).first()
                if book not in user_book_lst:
                    if neighbors_book_dict.get(book):
                        neighbors_book_dict[book] += 1
                    else:
                        neighbors_book_dict[book] = 1

    
    return neighbors_book_dict

def get_recommendations_lst(neighbors_book_dict, num_neighbors=10):

    times_recomended = {}
    for num in range(num_neighbors, 0, -1):
        times_recomended[num] = list()

    tuples = neighbors_book_dict.items()
    for item in tuples:
        if item[1] in times_recomended:
            times_recomended[item[1]].append(item[0])


    recommendation_lst = []

    while len(recommendation_lst) < 5:

        for num in range(num_neighbors, 0, -1): #range goes from length of neighbors to zero, counting backwards
            if len(times_recomended[num]) > 0: #non empty nested lists
                for book in times_recomended[num]:
                    if book not in recommendation_lst and len(recommendation_lst) < 5:
                        recommendation_lst.append(book)


    return recommendation_lst
    
