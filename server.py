"""Book Recommendations"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import os
import requests
import urllib3

from werkzeug.security import generate_password_hash, check_password_hash
from pyisbn import convert as convert_isbn


from model import connect_to_db, db, User, Book, Rating
from outward import write_rating_data
from ml import get_nearest_neighbors
from database_functions import add_anon_user, get_last_user_id, get_last_rating_id, get_book_id, add_rating, create_user_set, create_neighbors_book_dict, get_recommendations_lst, get_book_by_title, get_books_by_author, get_book_by_book_id, create_authors_dict, get_n_popular_books
from utils import convert_row_to_dict, get_info_google_books, get_info_open_library, create_combined_book_info_dict


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

GBOOKS_KEY = os.environ.get("GBOOKS")


# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ.get("APPSECRET_KEY")


# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


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

        book_dict = create_combined_book_info_dict(open_lib_info, google_books_info, book_dict, avg_rating, book)

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

        book_dict = create_combined_book_info_dict(open_lib_info, google_books_info, book_dict, avg_rating, book)

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
    neighbors_lst = get_nearest_neighbors(int(user_id)) #from ml.py
    
    #from database_functions.py
    user_book_lst = create_user_set(int(user_id))
    neighbors_dict = create_neighbors_book_dict(neighbors_lst, user_book_lst, 5)
    recommendation_lst = get_recommendations_lst(neighbors_dict)
    print(recommendation_lst)

    recommendation_info_dict = {}
    recommendation_link_dict = {}
    
    for book in recommendation_lst: # pragma: no cover
        
        #library.link requires isbn-13, so convert book.isbn to isbn-13
        isbn13 = convert_isbn(book.isbn)

        #use isbn-13 to get url for nearby library search
        library_link_url = "https://labs.library.link/services/borrow/"
        payload = {"isbn": "{}".format(isbn13), "embed": "true"}

        response = requests.get(library_link_url, params=payload)
        
        #Add book_id and url to a link dictionary
        recommendation_link_dict[book.book_id] = response.url
        

        #get summary, genres and cover image from Google Books
        url = "https://www.googleapis.com/books/v1/volumes"
        payload = {"q": "isbn:{}".format(book.isbn), "key": GBOOKS_KEY}
        

        response = requests.get("https://www.googleapis.com/books/v1/volumes", params=payload)

        #convert to json
        book_json = response.json()

        #if there were results from the Google Books call
        #add to book_id and the json to a dictionary
        if book_json["totalItems"] > 0: 
            recommendation_info_dict[book.book_id] = book_json

        #begin Open Library API call
        open_library_url = "https://openlibrary.org/api/books"
        payload = {"bibkeys" : "ISBN:{}".format(isbn13), "format" : "json", "jscmd" : "data"}

        response_ol = requests.get(open_library_url, params=payload)
        if response_ol:
            rec_excerpt_dict = {}
            response_ol_json = response_ol.json()
            isbnstring = "ISBN:{}".format(isbn13)
            if 'excerpts' in response_ol_json[isbnstring]:
                excerpt = response_ol_json[isbnstring]['excerpts'][0]['text']
                rec_excerpt_dict[book.book_id] = excerpt
        # else:
        
        #     #use isbn-13 to get url for nearby library search
        #     open_library_url = "https://openlibrary.org/api/books"
        #     payload = {"bibkeys" : "ISBN:{}".format(isbn13), "format" : "json", "jscmd" : "data"}

        #     response_ol = requests.get(open_library_url, params=payload)
        #     if response_ol:
        #         response_ol_json = response_ol.json()
        #         print(response_ol_json)

        #         recommendation_info_dict[book.book_id] = response_ol_json

    user = User.query.get(user_id)
    if user.email == None: #only registered users have emails, so we want to logout the anon user
        del session['user_id']
   


    return render_template('recommendations.html', recommendation_lst=recommendation_lst, recommendation_info_dict=recommendation_info_dict, recommendation_link_dict=recommendation_link_dict, rec_excerpt_dict=rec_excerpt_dict)



if __name__ == "__main__": # pragma: no cover

    connect_to_db(app)

    app.run()
