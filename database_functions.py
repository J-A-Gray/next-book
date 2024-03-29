from model import *
from sqlalchemy import func



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
    """Get a list of book objects by a particular author"""

    author = str(author).title()
    books = Book.query.filter(Book.author.ilike("%" + str(author) + "%")).all()

    return books

def get_book_by_title(title):
    """Get a book object by title"""
   
    books = Book.query.filter(Book.title.ilike("%" + str(title) + "%")).all()

    return books

def get_book_by_book_id(book_id):
    """Get a book object by book_id"""

    book = Book.query.filter(Book.book_id==str(book_id)).first()

    return book

def add_rating(user_id, book_id, score=5):

    next_rating_id = get_last_rating_id() + 1
    rating = Rating(rating_id=next_rating_id, user_id=user_id, book_id=book_id, score=score)
    db.session.add(rating)
    db.session.commit()

    return rating

def create_authors_dict():
    """Create a dictionary of all authors in db as keys and all books written by 
    author as values"""

    books = Book.query.order_by('author').all()
    author_dict = {}
    for book in books:
        if author_dict.get(book.author):
            author_dict[book.author].append(book)
        else:
            author_dict[book.author] = []
            author_dict[book.author].append(book)

    return author_dict


def create_user_set(user_id):
    """Create a list of books rated by the user"""
    user_book_set = set()
    ratings = Rating.query.filter_by(user_id=user_id).all()
    
    for rating in ratings:
        user_book_set.add(rating.book)

    return user_book_set

def create_neighbors_book_dict(neighbors_user_id_lst, user_book_set, score):
    """Create a dictionary of Book objects rated by neighbors of user but not in users input"""

    neighbors_book_dict = {}

    #for each user in most similar user list
    for neighbor in neighbors_user_id_lst:
        user = User.query.get(int(neighbor))

        ratings = Rating.query.filter_by(user_id=user.user_id).all()

        books_by_score = set()

        #add books from neighbors with same score to a set
        for rating in ratings:
            if rating.score == score:
                books_by_score.add(rating.book)

        #all the books the current user hasn't rated with the same rating as given
        neighbor_books = books_by_score - user_book_set


        for book in neighbor_books:
            if neighbors_book_dict.get(book):
                neighbors_book_dict[book] += 1
            else:
                neighbors_book_dict[book] = 1

    
    print("There are", len(neighbors_book_dict), "books in the k-neighbors dictionary")

    return neighbors_book_dict


def get_n_popular_books(n=15):
    """Return a list of the n-most highly rated books."""

    books_by_rating = (db.session.query(func.count(Rating.score), Book)
        .join(Book)
        .filter(Rating.score == 5)
        .group_by(Book)
        .order_by(func.count(Rating.score).desc())
        .limit(n)
        .all())


    return [book_tuple[1] for book_tuple in books_by_rating]


def get_recommendations_lst(neighbors_book_dict, num_neighbors=10, recs=5):

    times_recomended = {}
    for num in range(num_neighbors, 0, -1):
        times_recomended[num] = list()

    tuples = neighbors_book_dict.items()
    for item in tuples:
        if item[1] in times_recomended:
            times_recomended[item[1]].append(item[0])


    recommendation_lst = []

    while len(recommendation_lst) < recs:

        for num in range(num_neighbors, 0, -1): #range goes from length of neighbors to zero, counting backwards
            if len(times_recomended[num]) > 0: #non empty nested lists
                for book in times_recomended[num]:
                    if book not in recommendation_lst and len(recommendation_lst) < recs:
                        recommendation_lst.append(book)


    return recommendation_lst
    
