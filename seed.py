"""Utility file to seed ratings database from MovieLens data in seed_data/"""

import datetime
import csv
from sqlalchemy import func
from model import User
from model import Rating
from model import Book

from model import connect_to_db, db
from server import app


# def load_users():
#     """Load users from ratings.csv into database."""

#     print("Users")

#     # Delete all rows in table, so if we need to run this a second time,
#     # we won't be trying to add duplicate users
#     User.query.delete()

#     # Read u.user file and insert data
#     for row in open("seed_data/u.user"):
#         row = row.rstrip()
#         user_id, age, gender, occupation, zipcode = row.split("|")

#         user = User(user_id=user_id,
#                     age=age,
#                     zipcode=zipcode)

#         # We need to add to the session or it won't ever be stored
#         db.session.add(user)

#     # Once we're done, we should commit our work
#     db.session.commit()


def load_books():
    """Load books from books.csv into database."""

    print("Books")

    #Delete all rows in table
    Book.query.delete()

    #Read books file and insert data
    with open("seed_data/bookssorted.csv") as csvfile:
        try:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
        except:
            dialect = 'excel'

        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)
        next(csvfile) #skips first row of the csv file
        for row in reader:
                book_id = row[0]
                work_id = row[3]
                isbn = row[5]
                author = row[7]
                title = row[10]
                
                if len(author) > 600:
                    author = author[:600]


            # create each book object
                book = Book(book_id=book_id,
                            work_id=work_id,
                            isbn=isbn,
                            title=title,
                            author=author)

                #add every movie
                db.session.add(book)

              

        # commit
        db.session.commit()





# def load_ratings():
#     """Load ratings from u.data into database."""

#     print("Ratings")

#     Rating.query.delete()

#     with open("seed_data/u.data") as file:
#         for row in file:
#             row = row.rstrip()
#             (user_id, movie_id, score, timestamp) = row.split("\t")

#             user_id = int(user_id)
#             movie_id = int(movie_id)
#             score = int(score)

#             rating = Rating(user_id=user_id,
#                             movie_id=movie_id,
#                             score=score)

#             #We need to add to the session or it won't ever be store
#             db.session.add(rating)

#         db.session.commit()



# def set_val_user_id():
#     """Set value for the next user_id after seeding database"""

#     # Get the Max user_id in the database
#     result = db.session.query(func.max(User.user_id)).one()
#     max_id = int(result[0])

#     # Set the value for the next user_id to be max_id + 1
#     query = "SELECT setval('users_user_id_seq', :new_id)"
#     db.session.execute(query, {'new_id': max_id + 1})
#     db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()


    # sniff_dialect()
    # Import different types of data
    # load_users()
    load_books()
    # load_ratings()
    # set_val_user_id()