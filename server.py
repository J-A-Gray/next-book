"""Book Recommendations"""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, request, flash, redirect, session,
                   jsonify)

from flask_debugtoolbar import DebugToolbarExtension

import os
import requests
import urllib3

from werkzeug.security import generate_password_hash, check_password_hash
from pyisbn import convert as convert_isbn
from twilio.rest import Client


from model import connect_to_db, db, User, Book, Rating
from outward import write_rating_data
from ml import get_nearest_neighbors
from database_functions import (add_anon_user, get_last_user_id,
                                get_last_rating_id, get_book_id, add_rating,
                                create_user_set, create_neighbors_book_dict,
                                get_recommendations_lst, get_book_by_title,
                                get_books_by_author, get_book_by_book_id,
                                create_authors_dict, get_n_popular_books)

from utils import (convert_row_to_dict, get_info_google_books,
                   get_info_open_library, create_combined_book_info_dict,
                   send_message, create_rec_message)


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ.get("APPSECRET_KEY")


# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
messaging_service_sid = os.environ.get('TWILIO_MESSAGING_SERVICE_SID')

twilio_client = Client(twilio_account_sid, twilio_auth_token)


GBOOKS_KEY = os.environ.get("GBOOKS")

@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/register', methods=['GET'])
def register_form():
    """Display form for user signup."""

    return render_template("registration_form.html")

@app.route('/register', methods=['POST'])
def register_for_site():
    """Collects and sends new user info for registration"""

    email = request.form['email']
    password = request.form['password']

    if email in User.query.all():
        flash("You already have an account. Please log in.")

    else:
        next_id = get_last_user_id() + 1
        password = generate_password_hash(password)
        new_user = User(user_id=next_id, email=email, password=password)

        db.session.add(new_user)
        db.session.commit()

    return redirect('/login')

@app.route('/login', methods=['GET'])
def login_form():
    """Display login form."""

    return render_template("login_form.html")

@app.route('/login', methods=['POST'])
def login_process():
    """Collect and send info for user to login."""

    email = request.form['email']
    password = request.form['password']

    user = User.query.filter(User.email == email).first()

    if not user:
        flash("You are not yet registered!")
        return redirect('/register')

    elif not check_password_hash(user.password, password):
        flash("That's not the right password. Try again?")
        return redirect('/login')

    elif user and check_password_hash(user.password, password):
        session['user_id'] = user.user_id
        return redirect(f'/users/{user.user_id}')

    else:
        flash("Try Again")
        return redirect('/login')


@app.route('/logout')
def logout():
    """Log user out."""
    del session['user_id']
    flash("Bye! Happy Reading!")
    return redirect('/')


@app.route('/users/<int:user_id>')
def user_detail(user_id):

    user = User.query.get(user_id)
    return render_template('user.html', user=user)

# @app.route('/books')
# def show_books():
#     """Show a book list."""

#     books = Book.query.order_by('title').all()

#     return render_template('book_list.html', books=books)

@app.route('/books/<int:book_id>/info.json')
def get_info_by_book_id(book_id):

    if book_id:

        book = get_book_by_book_id(book_id)

        book_dict = convert_row_to_dict(book)

        #get info from Open Library
        open_lib_info = get_info_open_library(book)

        #get book info from Google Books
        google_books_info = get_info_google_books(book, GBOOKS_KEY)


        rating_scores = [r.score for r in book.ratings]
        if len(rating_scores) > 0:
            avg_rating = float(sum(rating_scores))/len(rating_scores)
            avg_rating = f"{avg_rating:.1f}"
        else:
            avg_rating = None

        book_dict = create_combined_book_info_dict(open_lib_info, 
                                                   google_books_info, book_dict, 
                                                   avg_rating, book)

        return jsonify(book_dict)

    else:
        return "No books found."

@app.route('/api/books/<int:book_id>')
def serve_info_by_book_id(book_id):

    if book_id:

        book = get_book_by_book_id(book_id)

        book_dict = convert_row_to_dict(book)

        #get info from Open Library
        open_lib_info = get_info_open_library(book)

        #get book info from Google Books
        google_books_info = get_info_google_books(book, GBOOKS_KEY)


        rating_scores = [r.score for r in book.ratings]
        if len(rating_scores) > 0:
            avg_rating = float(sum(rating_scores))/len(rating_scores)
            avg_rating = f"{avg_rating:.1f}"
        else:
            avg_rating = None

        book_dict = create_combined_book_info_dict(open_lib_info, 
                                                   google_books_info, book_dict, 
                                                   avg_rating, book)

        return jsonify(book_dict)

    else:
        return "No books found."


@app.route('/books/<int:book_id>', methods=['GET'])
def show_book_details(book_id):

    return render_template('book-react.html')

@app.route('/books/<int:book_id>', methods=['POST'])
def set_rating(book_id):

    score = int(request.form.get('submitted_rating'))
    user_id = session.get('user_id')
    if not user_id:
        raise Exception("You aren't logged in!")

    #check for existing rating    
    user_rating = Rating.query.filter_by(user_id=user_id, book_id=book_id).first()
    

    if user_rating: #if the rating object exists in the database
        user_rating.score = score #then update the score
        flash("You've updated your rating!")
        db.session.add(user_rating)
        print(user_rating)

    
    else:# if the rating object does not exist yet
        next_id = get_last_rating_id() + 1
        user_rating = Rating(rating_id=next_id, user_id=user_id, book_id=book_id, score=score)
        flash("Thank you for rating!")

        db.session.add(user_rating)
        print(user_rating)

    db.session.commit()

    return redirect(f'/books/{book_id}')


@app.route('/authors')
def show_authors():
    """Display a list of all authors and the books they've written from the database."""

    author_dict = create_authors_dict()


    return render_template('author_list.html', author_dict=author_dict)


@app.route('/authors/<author>', methods=['GET'])
def show_author_details(author):

    book_lst = Book.query.filter_by(author=author).all()


    return render_template('author.html', author=author, book_lst=book_lst)

@app.route('/search', methods=['GET'])
def search_books():
    """Searches for books to add to ratings list"""


    return render_template('search.html')


@app.route('/search', methods=['POST'])
def gather_books():
   
   #get MultiDict from client side
   books = request.form
   print(books)
   book_id_dict={}

   for key, value in books.items():
    book_id_dict[key] = value
 


   user_id = session.get('user_id')

   if user_id == None:
   # create a user to hold ratings
       anon_user = add_anon_user()
       
       # query db to get user id
       user_id = get_last_user_id()

   #add ratings to db
   for key, value in book_id_dict.items():
    rating = add_rating(user_id, key, score=value)
    print(rating)

   #write csv file to send to Surprise library
   write_rating_data()

   #set user_id in session
   session['user_id'] = user_id
   

   return redirect('/recommendations')

@app.route('/search-by-title.json') 
def search_books_by_title(): # pragma: no cover

    title = request.args.get("title")
 

    if title:
        books_by_title = get_book_by_title(title)
        books_by_title_serialized = Book.serialize_list(books_by_title)
        for book in books_by_title_serialized:
           del book['ratings']

        return jsonify(books_by_title_serialized)

        # return jsonify({"books": books_by_title})

    else:
        return "No books found."

@app.route('/search-by-author.json')
def search_books_by_author(): # pragma: no cover

    author = request.args.get("author")

    if author:
        books_by_author = get_books_by_author(author)
        books_by_author_serialized = Book.serialize_list(books_by_author)
        for book in books_by_author_serialized:
           del book['ratings']

        return jsonify(books_by_author_serialized)

    else:
        return "No books found."

@app.route('/search-by-book-id.json')
def search_books_by_book_id(): # pragma: no cover

    book_id = int(request.args.get("book_id"))
    print(book_id)

    if book_id:
        book_by_book_id = get_book_by_book_id(book_id)
        book_by_book_id_serialized = Book.serialize(book_by_book_id)
        del book_by_book_id_serialized['ratings']


        return jsonify(book_by_book_id_serialized)

        # return jsonify({"books": books_by_title})

    else:
        return "No books found."

@app.route('/api/popular') 
def get_top_books_info():

    popular_books = get_n_popular_books(n=20)
 

    books_serialized = Book.serialize_list(popular_books)
    for book in books_serialized:
       del book['ratings']

    return jsonify(books_serialized)

@app.route('/popular')
def display_top_books():

    return render_template('top_books.html')


@app.route('/recommendations', methods=['GET'])
def display_recommended_books():

    user_id = session.get('user_id')
    # neighbors_lst = get_nearest_neighbors(int(user_id)) #from ml.py
    
    # #from database_functions.py
    # user_book_lst = create_user_set(int(user_id))
    # neighbors_dict = create_neighbors_book_dict(neighbors_lst, user_book_lst, 5)
    # recommendation_lst = get_recommendations_lst(neighbors_dict)
    # print(recommendation_lst)

    # recommendation_info_dict = {}
    # recommendation_link_dict = {}
    
    # for book in recommendation_lst: # pragma: no cover
        
    #     #library.link requires isbn-13, so convert book.isbn to isbn-13
    #     isbn13 = convert_isbn(book.isbn)

    #     #use isbn-13 to get url for nearby library search
    #     library_link_url = "https://labs.library.link/services/borrow/"
    #     payload = {"isbn": "{}".format(isbn13), "embed": "true"}

    #     response = requests.get(library_link_url, params=payload)
        
    #     #Add book_id and url to a link dictionary
    #     recommendation_link_dict[book.book_id] = response.url
        

    #     #get summary, genres and cover image from Google Books
    #     url = "https://www.googleapis.com/books/v1/volumes"
    #     payload = {"q": "isbn:{}".format(book.isbn), "key": GBOOKS_KEY}
        

    #     response = requests.get("https://www.googleapis.com/books/v1/volumes", params=payload)

    #     #convert to json
    #     book_json = response.json()

    #     #if there were results from the Google Books call
    #     #add to book_id and the json to a dictionary
    #     if book_json["totalItems"] > 0: 
    #         recommendation_info_dict[book.book_id] = book_json

    #     #begin Open Library API call
    #     open_library_url = "https://openlibrary.org/api/books"
    #     payload = {"bibkeys" : "ISBN:{}".format(isbn13), "format" : "json", "jscmd" : "data"}

    #     response_ol = requests.get(open_library_url, params=payload)
    #     if response_ol:
    #         rec_excerpt_dict = {}
    #         response_ol_json = response_ol.json()
    #         isbnstring = "ISBN:{}".format(isbn13)
    #         if 'excerpts' in response_ol_json[isbnstring]:
    #             excerpt = response_ol_json[isbnstring]['excerpts'][0]['text']
    #             rec_excerpt_dict[book.book_id] = excerpt
    #     # else:
        
    #     #     #use isbn-13 to get url for nearby library search
    #     #     open_library_url = "https://openlibrary.org/api/books"
    #     #     payload = {"bibkeys" : "ISBN:{}".format(isbn13), "format" : "json", "jscmd" : "data"}

    #     #     response_ol = requests.get(open_library_url, params=payload)
    #     #     if response_ol:
    #     #         response_ol_json = response_ol.json()
    #     #         print(response_ol_json)

    #     #         recommendation_info_dict[book.book_id] = response_ol_json

    user = User.query.get(user_id)
    if user.email == None: #only registered users have emails, so we want to logout the anon user
        del session['user_id']

    #mock section for developement
    recommendation_lst =[Book.query.get(2555), Book.query.get(236), Book.query.get(7), Book.query.get(155), Book.query.get(55)]    
    recommendation_info_dict = {2555: {'kind': 'books#volumes', 'totalItems': 1, 'items': [{'kind': 'books#volume', 'id': '89-2ZXYsuAQC', 'etag': 'Tf1jPhK65Fc', 'selfLink': 'https://www.googleapis.com/books/v1/volumes/89-2ZXYsuAQC', 'volumeInfo': {'title': 'Kindred', 'authors': ['Octavia E. Butler'],'publisher': 'Beacon Press', 'publishedDate': '1988', 'description': "Dana, a black woman, finds herself repeatedly transported to the antebellum South, where she must make sure that Rufus, the plantation owner's son, survives to father Dana's ancestor.", 'industryIdentifiers': [{'type': 'ISBN_10', 'identifier': '0807083690'}, {'type': 'ISBN_13', 'identifier': '9780807083697'}], 'readingModes': {'text': True, 'image': False}, 'pageCount': 287, 'printType': 'BOOK', 'categories': ['Fiction'], 'averageRating': 4, 'ratingsCount': 175, 'maturityRating': 'NOT_MATURE', 'allowAnonLogging': True, 'contentVersion': '1.7.5.0.preview.2', 'panelizationSummary': {'containsEpubBubbles': False, 'containsImageBubbles': False}, 'imageLinks': {'smallThumbnail': 'http://books.google.com/books/content?id=89-2ZXYsuAQC&printsec=frontcover&img=1&zoom=5&edge=curl&source=gbs_api', 'thumbnail': 'http://books.google.com/books/content?id=89-2ZXYsuAQC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api'}, 'language': 'en', 'previewLink': 'http://books.google.com/books?id=89-2ZXYsuAQC&printsec=frontcover&dq=isbn:0807083690&hl=&cd=1&source=gbs_api', 'infoLink': 'http://books.google.com/books?id=89-2ZXYsuAQC&dq=isbn:0807083690&hl=&source=gbs_api', 'canonicalVolumeLink': 'https://books.google.com/books/about/Kindred.html?hl=&id=89-2ZXYsuAQC'}, 'saleInfo': {'country': 'US', 'saleability': 'NOT_FOR_SALE', 'isEbook': False}, 'accessInfo': {'country': 'US', 'viewability': 'PARTIAL', 'embeddable': True, 'publicDomain': False, 'textToSpeechPermission': 'ALLOWED', 'epub': {'isAvailable': True, 'acsTokenLink': 'http://books.google.com/books/download/Kindred-sample-epub.acsm?id=89-2ZXYsuAQC&format=epub&output=acs4_fulfillment_token&dl_type=sample&source=gbs_api'}, 'pdf': {'isAvailable': False}, 'webReaderLink': 'http://play.google.com/books/reader?id=89-2ZXYsuAQC&hl=&printsec=frontcover&source=gbs_api', 'accessViewStatus': 'SAMPLE', 'quoteSharingAllowed': False}, 'searchInfo': {'textSnippet': 'Dana, a black woman, finds herself repeatedly transported to the antebellum South, where she must make sure that Rufus, the plantation owner&#39;s son, survives to father Dana&#39;s ancestor.'}}]}, 236: {'kind': 'books#volumes', 'totalItems': 1, 'items': [{'kind': 'books#volume', 'id': 'lI_2H3GUulEC', 'etag': 'Y8AyhwldVOw', 'selfLink': 'https://www.googleapis.com/books/v1/volumes/lI_2H3GUulEC', 'volumeInfo': {'title': 'Into Thin Air', 'subtitle': 'A Personal Account of the Mount Everest Disaster', 'authors': ['Jon Krakauer'], 'publisher': 'Anchor Books', 'publishedDate': '1999', 'description': 'The author describes his spring 1996 trek to Mt. Everest, a disastrous expedition that claimed the lives of eight climbers, and explains why he survived', 'industryIdentifiers': [{'type': 'ISBN_10', 'identifier': '0385494785'}, {'type': 'ISBN_13', 'identifier': '9780385494786'}], 'readingModes': {'text': False, 'image': False}, 'pageCount': 332, 'printType': 'BOOK', 'categories': ['Biography & Autobiography'], 'averageRating': 4, 'ratingsCount': 217, 'maturityRating': 'NOT_MATURE', 'allowAnonLogging': False, 'contentVersion': '0.0.1.0.preview.0', 'imageLinks': {'smallThumbnail': 'http://books.google.com/books/content?id=lI_2H3GUulEC&printsec=frontcover&img=1&zoom=5&source=gbs_api', 'thumbnail': 'http://books.google.com/books/content?id=lI_2H3GUulEC&printsec=frontcover&img=1&zoom=1&source=gbs_api'}, 'language': 'en', 'previewLink': 'http://books.google.com/books?id=lI_2H3GUulEC&dq=isbn:0385494785&hl=&cd=1&source=gbs_api', 'infoLink': 'http://books.google.com/books?id=lI_2H3GUulEC&dq=isbn:0385494785&hl=&source=gbs_api', 'canonicalVolumeLink': 'https://books.google.com/books/about/Into_Thin_Air.html?hl=&id=lI_2H3GUulEC'}, 'saleInfo': {'country': 'US', 'saleability': 'NOT_FOR_SALE', 'isEbook': False}, 'accessInfo': {'country': 'US', 'viewability': 'NO_PAGES', 'embeddable': False, 'publicDomain': False, 'textToSpeechPermission': 'ALLOWED', 'epub': {'isAvailable': False}, 'pdf': {'isAvailable': False}, 'webReaderLink': 'http://play.google.com/books/reader?id=lI_2H3GUulEC&hl=&printsec=frontcover&source=gbs_api', 'accessViewStatus': 'NONE', 'quoteSharingAllowed': False}, 'searchInfo': {'textSnippet': 'The author describes his spring 1996 trek to Mt. Everest, a disastrous expedition that claimed the lives of eight climbers, and explains why he survived'}}]}, 7: {'kind': 'books#volumes', 'totalItems': 2, 'items': [{'kind': 'books#volume', 'id': 'dPQetAEACAAJ', 'etag': 'QPcoFunpa88', 'selfLink': 'https://www.googleapis.com/books/v1/volumes/dPQetAEACAAJ', 'volumeInfo': {'title': 'The Hobbit', 'authors': ['John Ronald Reuel Tolkien'], 'publishedDate': '1937', 'description': 'Bilbo Baggins, a respectable, well-to-do hobbit, lives comfortably in his hobbit-hole until the day the wandering wizard Gandalf chooses him to share in an adventure from which he may never return.', 'industryIdentifiers': [{'type': 'ISBN_10', 'identifier': '0618260307'}, {'type': 'ISBN_13', 'identifier': '9780618260300'}], 'readingModes': {'text': False, 'image': False}, 'pageCount': 365, 'printType': 'BOOK', 'categories': ['Baggins, Bilbo (Fictitious character)'], 'averageRating': 4, 'ratingsCount': 2535, 'maturityRating': 'NOT_MATURE', 'allowAnonLogging': False, 'contentVersion': 'preview-1.0.0', 'panelizationSummary': {'containsEpubBubbles': False, 'containsImageBubbles': False}, 'language': 'en', 'previewLink': 'http://books.google.com/books?id=dPQetAEACAAJ&dq=isbn:0618260307&hl=&cd=1&source=gbs_api', 'infoLink': 'http://books.google.com/books?id=dPQetAEACAAJ&dq=isbn:0618260307&hl=&source=gbs_api', 'canonicalVolumeLink': 'https://books.google.com/books/about/The_Hobbit.html?hl=&id=dPQetAEACAAJ'}, 'saleInfo': {'country': 'US', 'saleability': 'NOT_FOR_SALE', 'isEbook': False}, 'accessInfo': {'country': 'US', 'viewability': 'NO_PAGES', 'embeddable': False, 'publicDomain': False, 'textToSpeechPermission': 'ALLOWED', 'epub': {'isAvailable': False},'pdf': {'isAvailable': False}, 'webReaderLink': 'http://play.google.com/books/reader?id=dPQetAEACAAJ&hl=&printsec=frontcover&source=gbs_api', 'accessViewStatus': 'NONE', 'quoteSharingAllowed': False}, 'searchInfo': {'textSnippet': 'Bilbo Baggins, a respectable, well-to-do hobbit, lives comfortably in his hobbit-hole until the day the wandering wizard Gandalf chooses him to share in an adventure from which he may never return.'}}, {'kind': 'books#volume', 'id': 'ljWL5A7D2JAC', 'etag': 'lGoaIq3h9LU', 'selfLink': 'https://www.googleapis.com/books/v1/volumes/ljWL5A7D2JAC', 'volumeInfo': {'title': 'The Hobbit, Or, There and Back Again', 'authors': ['John Ronald Reuel Tolkien'], 'publisher': 'Houghton Mifflin Harcourt', 'publishedDate': '2001', 'description': 'A newly rejacketed edition of the classic tale chronicles the adventures of the inhabitants of Middle-earth and of Bilbo Baggins, the hobbit who brought home to The Shire the One Ring of Power.', 'industryIdentifiers': [{'type': 'ISBN_10', 'identifier': '0618260307'}, {'type': 'ISBN_13', 'identifier': '9780618260300'}], 'readingModes': {'text': False, 'image': False}, 'pageCount': 365, 'printType': 'BOOK', 'categories': ['Juvenile Fiction'], 'averageRating': 4, 'ratingsCount': 2629, 'maturityRating': 'NOT_MATURE', 'allowAnonLogging': False, 'contentVersion': '2.1.1.0.preview.0', 'imageLinks': {'smallThumbnail': 'http://books.google.com/books/content?id=ljWL5A7D2JAC&printsec=frontcover&img=1&zoom=5&source=gbs_api', 'thumbnail': 'http://books.google.com/books/content?id=ljWL5A7D2JAC&printsec=frontcover&img=1&zoom=1&source=gbs_api'}, 'language': 'en','previewLink': 'http://books.google.com/books?id=ljWL5A7D2JAC&pg=PP1&dq=isbn:0618260307&hl=&cd=2&source=gbs_api', 'infoLink': 'http://books.google.com/books?id=ljWL5A7D2JAC&dq=isbn:0618260307&hl=&source=gbs_api', 'canonicalVolumeLink': 'https://books.google.com/books/about/The_Hobbit_Or_There_and_Back_Again.html?hl=&id=ljWL5A7D2JAC'}, 'saleInfo': {'country': 'US', 'saleability': 'NOT_FOR_SALE', 'isEbook': False}, 'accessInfo': {'country': 'US', 'viewability': 'NO_PAGES', 'embeddable': False, 'publicDomain': False, 'textToSpeechPermission': 'ALLOWED', 'epub': {'isAvailable': False}, 'pdf': {'isAvailable': False}, 'webReaderLink': 'http://play.google.com/books/reader?id=ljWL5A7D2JAC&hl=&printsec=frontcover&source=gbs_api', 'accessViewStatus': 'NONE', 'quoteSharingAllowed': False}}]}, 155: {'kind': 'books#volumes', 'totalItems': 1, 'items': [{'kind': 'books#volume', 'id': 'lC_E8Hz-8rIC', 'etag': 'g6cbWymQPGo', 'selfLink': 'https://www.googleapis.com/books/v1/volumes/lC_E8Hz-8rIC', 'volumeInfo': {'title': 'The Two Towers', 'authors': ['John Ronald Reuel Tolkien'], 'publisher': 'Mariner Books', 'publishedDate': '2003', 'description': 'After losing Gandalf and being divided from their other companions during an Orc attack, Frodo and Sam continue towards Mordor, Land of the Enemy, to destroy the Ring, accompanied only by a mysterious figure that follows them.', 'industryIdentifiers': [{'type': 'ISBN_10', 'identifier': '0618346260'}, {'type': 'ISBN_13', 'identifier': '9780618346264'}], 'readingModes': {'text': False, 'image': False}, 'pageCount': 725, 'printType': 'BOOK', 'categories': ['Fiction'], 'averageRating': 4, 'ratingsCount': 1219, 'maturityRating': 'NOT_MATURE', 'allowAnonLogging': False, 'contentVersion': '0.1.2.0.preview.0', 'panelizationSummary': {'containsEpubBubbles': False, 'containsImageBubbles': False}, 'imageLinks': {'smallThumbnail': 'http://books.google.com/books/content?id=lC_E8Hz-8rIC&printsec=frontcover&img=1&zoom=5&source=gbs_api', 'thumbnail': 'http://books.google.com/books/content?id=lC_E8Hz-8rIC&printsec=frontcover&img=1&zoom=1&source=gbs_api'}, 'language': 'en', 'previewLink': 'http://books.google.com/books?id=lC_E8Hz-8rIC&dq=isbn:0618346260&hl=&cd=1&source=gbs_api', 'infoLink': 'http://books.google.com/books?id=lC_E8Hz-8rIC&dq=isbn:0618346260&hl=&source=gbs_api', 'canonicalVolumeLink': 'https://books.google.com/books/about/The_Two_Towers.html?hl=&id=lC_E8Hz-8rIC'}, 'saleInfo': {'country': 'US', 'saleability': 'NOT_FOR_SALE', 'isEbook': False}, 'accessInfo': {'country': 'US', 'viewability': 'NO_PAGES', 'embeddable': False, 'publicDomain': False, 'textToSpeechPermission': 'ALLOWED', 'epub': {'isAvailable': False}, 'pdf': {'isAvailable': False}, 'webReaderLink': 'http://play.google.com/books/reader?id=lC_E8Hz-8rIC&hl=&printsec=frontcover&source=gbs_api', 'accessViewStatus': 'NONE', 'quoteSharingAllowed': False}, 'searchInfo': {'textSnippet': 'After losing Gandalf and being divided from their other companions during an Orc attack, Frodo and Sam continue towards Mordor, Land of the Enemy, to destroy the Ring, accompanied only by a mysterious figure that follows them.'}}]}, 55: {'kind': 'books#volumes', 'totalItems': 1, 'items': [{'kind': 'books#volume', 'id': '5H46PcnDCYMC', 'etag': 'wiAfjfjSG4U', 'selfLink': 'https://www.googleapis.com/books/v1/volumes/5H46PcnDCYMC', 'volumeInfo': {'title': 'Brave New World', 'authors': ['Aldous Huxley'], 'publisher': 'Harper Collins', 'publishedDate': '1998-09', 'description': "Huxley's classic prophetic novel describes the socialized horrors of a futuristic utopia devoid of individual freedom", 'industryIdentifiers': [{'type': 'ISBN_13', 'identifier': '9780060929879'}, {'type': 'ISBN_10', 'identifier': '0060929871'}], 'readingModes': {'text': False, 'image': False}, 'pageCount': 268, 'printType': 'BOOK', 'categories': ['Fiction'], 'averageRating': 3.5, 'ratingsCount': 2983, 'maturityRating': 'NOT_MATURE', 'allowAnonLogging': False, 'contentVersion': 'preview-1.0.0', 'panelizationSummary': {'containsEpubBubbles': False, 'containsImageBubbles': False}, 'imageLinks': {'smallThumbnail': 'http://books.google.com/books/content?id=5H46PcnDCYMC&printsec=frontcover&img=1&zoom=5&edge=curl&source=gbs_api', 'thumbnail': 'http://books.google.com/books/content?id=5H46PcnDCYMC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api'}, 'language': 'en', 'previewLink': 'http://books.google.com/books?id=5H46PcnDCYMC&printsec=frontcover&dq=isbn:0060929871&hl=&cd=1&source=gbs_api', 'infoLink': 'http://books.google.com/books?id=5H46PcnDCYMC&dq=isbn:0060929871&hl=&source=gbs_api', 'canonicalVolumeLink': 'https://books.google.com/books/about/Brave_New_World.html?hl=&id=5H46PcnDCYMC'}, 'saleInfo': {'country': 'US', 'saleability': 'NOT_FOR_SALE', 'isEbook': False}, 'accessInfo': {'country': 'US', 'viewability': 'PARTIAL', 'embeddable': True, 'publicDomain':False, 'textToSpeechPermission': 'ALLOWED_FOR_ACCESSIBILITY', 'epub': {'isAvailable': False}, 'pdf': {'isAvailable': False}, 'webReaderLink': 'http://play.google.com/books/reader?id=5H46PcnDCYMC&hl=&printsec=frontcover&source=gbs_api', 'accessViewStatus': 'SAMPLE', 'quoteSharingAllowed': False}, 'searchInfo': {'textSnippet': 'Huxley&#39;s classic prophetic novel describes the socialized horrors of a futuristic utopia devoid of individual freedom'}}]}}
    recommendation_link_dict = {2555: 'https://labs.library.link/services/borrow/?isbn=9780807083697&embed=true', 236: 'https://labs.library.link/services/borrow/?isbn=9780385494786&embed=true', 7: 'https://labs.library.link/services/borrow/?isbn=9780618260300&embed=true', 155: 'https://labs.library.link/services/borrow/?isbn=9780618346264&embed=true', 55: 'https://labs.library.link/services/borrow/?isbn=9780060929879&embed=true'}
    rec_excerpt_dict = {}

    return render_template('recommendations.html', 
                            recommendation_lst=recommendation_lst,
                            recommendation_info_dict=recommendation_info_dict,
                            recommendation_link_dict=recommendation_link_dict,
                            rec_excerpt_dict=rec_excerpt_dict)

@app.route('/test', methods=['GET', 'POST'])
def send_test_message():
    if request.method == 'POST':
        print(request.form)

        message = create_rec_message(books=request.form.get("book-id").split(", "))

        send_message(twilio_client, 
                     phone_num=request.form.get("phone-num"), 
                     messaging_service_sid=messaging_service_sid, 
                     body=message)

    return render_template('message_sent.html')

if __name__ == "__main__": # pragma: no cover
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.debug = True
    # # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug
    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5001, host='0.0.0.0')
