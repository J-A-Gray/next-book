"""Utility file to export cleaned data to Surprise"""

import csv
from sqlalchemy import func
from model import User
from model import Rating
from model import Book

from model import connect_to_db, db
from server import app



def write_rating_data():
    """Use a query to create a csv file"""
    with open('outward.csv', 'w') as f:
        out = csv.writer(f)

        for item in Rating.query.filter(Rating.score != None).all():
            out.writerow([item.user_id, item.book_id, item.score])


if __name__ == "__main__":
    connect_to_db(app)

write_rating_data()