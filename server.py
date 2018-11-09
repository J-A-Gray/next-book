"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Book, Rating
from outward import write_rating_data
from ml import get_nearest_neighbors


from database_functions import add_anon_user, get_last_user_id, get_last_rating_id, get_book_id, add_rating


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

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
        new_user = User(email=email, password=password)

        db.session.add(new_user)
    db.session.commit()

    return redirect('/')

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

    if user.password != password:
        flash("That's not the right password. Try again?")
        return redirect('/login')

    else:
        session['user_id'] = user.user_id

    flash('Welcome!')
    return redirect(f'/users/{user.user_id}')

@app.route('/logout')
def logout():
    """Log user out."""
    del session['user_id']
    flash("Bye! Happy Reading!")
    return redirect('/')

@app.route('/users')
def user_list():
    """Show list of users"""

    users = User.query.all()
    return render_template('user_list.html', users=users)

@app.route('/users/<int:user_id>')
def user_detail(user_id):

    user = User.query.get(user_id)
    return render_template('user.html', user=user)

@app.route('/books')
def show_books():
    """Show a book list."""

    books = Book.query.order_by('title').all()

    return render_template('book_list.html', books=books)

@app.route('/books/<int:book_id>', methods=['GET'])
def show_book_details(book_id):

    book = Book.query.get(book_id)

    user_id = session.get('user_id')

    if user_id:
        #get user rating
        user_rating = Rating.query.filter_by(book_id=book_id, user_id=user_id).first()
    else:
        user_rating = None

    #Get avg rating of book

    rating_scores = [r.score for r in book.ratings]
    if len(rating_scores) > 0:
        avg_rating = float(sum(rating_scores))/len(rating_scores) #need to format
    else:
        avg_rating = None


    return render_template('book.html', book=book, user_rating=user_rating, user_id=user_id, avg_rating=avg_rating)

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
        db.session.commit()

    
    else:# if the rating object does not exist yet
        user_rating = Rating(user_id=user_id, book_id=book_id, score=score)
        flash("Thank you for rating!")

        db.session.add(user_rating)

        db.session.commit()

    return redirect(f'/books/{book_id}')

@app.route('/lovedbooks', methods=['GET'])
def book_form():

    return render_template('reference_books.html')

@app.route('/lovedbooks', methods=['POST'])
def process_books():

    b1 = request.form['book1']
    b2 = request.form['book2']
    b3 = request.form['book3']
    b4 = request.form['book4']
    b5 = request.form['book5']

    # create a user to hold ratings
    anon_user = add_anon_user()

    # query db to get user id
    anon_id = get_last_user_id()

    # query db to get book_ids
    book1_id = get_book_id(str(b1))
    book2_id = get_book_id(str(b2))
    book3_id = get_book_id(str(b3))
    book4_id = get_book_id(str(b4))
    book5_id = get_book_id(str(b5))

    #add ratings to db
    add_rating(anon_id, book1_id)
    add_rating(anon_id, book2_id)
    add_rating(anon_id, book3_id)
    add_rating(anon_id, book4_id)
    add_rating(anon_id, book5_id)

    #write csv file to send to Surprise library
    write_rating_data()

    #set user_id in session
    session['user_id'] = anon_id


    return redirect('/lovedbooksresults')

@app.route('/lovedbooksresults', methods=['GET'])
def display_favorite_books():

    user_id = session.get('user_id')
    neighbors = get_nearest_neighbors(user_id)
    

    return render_template('loved_books_result.html')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')