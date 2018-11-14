"""Utility file to export cleaned data to Surprise"""

import csv
from sqlalchemy import func
from model import Book, User, Rating



def write_rating_data():
    """Use a query to create a csv file"""
    with open('outward.csv', 'w') as f:
        out = csv.writer(f)

        for item in Rating.query.filter(Rating.score != None).all():
            out.writerow([item.user_id, item.book_id, item.score])


