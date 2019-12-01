"""Utility file to seed ratings database from Goodbooks-10K data in seed_data/"""

import csv
from sqlalchemy import func
from model import User
from model import Rating
from model import Book

from model import connect_to_db, db
from server import app


def load_users():
    """Load users from ratings.csv into database."""

    print("Users")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()


    for num in range(53425): #this is particular to this data-set, where our only user_id info is coming from the ratings file which 
        user_id = num

        user = User(user_id=user_id)



        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_books():
    """Load books from books.csv into database."""

    print("Books")

    #Delete all rows in table
    Book.query.delete()

    #Read books file and insert data
    with open("seed_data/books_in_eng.csv") as csvfile:
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

                #add every book
                db.session.add(book)

              

        # commit
        db.session.commit()


def load_ratings():
    """Load ratings from ratings.csv into database."""

    print("Ratings")

    Rating.query.delete()

    filename_prefix = 'seed_data/splitfile_'
    filename_num = 1
    filename_suffix = '.csv'

    while filename_num <= 2:
        print("Starting file #", filename_num)
        filename = filename_prefix + str(filename_num) + filename_suffix

        with open(filename, encoding='utf-16') as csvfile:
            try:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
            except:
                dialect = 'excel'

            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect)
            next(csvfile) #skips first row of the csv file

            counter = 0
            how_many = 1
            for row in reader:
                book_id = row[1]
                user_id = row[0]
                score = row[2]
                    
                user_id = int(user_id)
                book_id = int(book_id)
                score = int(score)

                rating = Rating(user_id=user_id,
                                book_id=book_id,
                                score=score)

                #We need to add to the session or it won't ever be stored

                book_in_db = Book.query.get(book_id)
                user_in_db = User.query.get(user_id)
                if book_in_db and user_in_db:
                    db.session.add(rating)
                    print("Rating for " + str(rating.book_id) + " added to database")
                    counter += 1

                if counter > 999 and counter % 1000 == 0:
                    print("Committing new objects")
                    print("Committed", how_many, "times")
                    db.session.commit()
                    how_many +=1
                    
            db.session.commit()
            print("Finished with file #" + filename_num)
            filename_num += 1
           




def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

def set_val_rating_id():
    """Set value for the next rating_id after seeding database"""

    #Get the Max rating_id in the database
    result = db.session.query(func.max(Rating.rating_id)).one()
    max_id = int(result[0])

    #Set the value for the next rating_id to be max_id +1
    query = "SELECT setval('ratings_rating_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()



    # Import different types of data
    load_users()
    load_books()
    load_ratings()
    set_val_user_id()
    set_val_rating_id()