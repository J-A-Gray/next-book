from flask import Blueprint

books_bp = Blueprint('books', __name__, template_folder='templates/books')


@books_bp.route('/books')
def show_books():
    """Show a book list."""

    books = Book.query.order_by('title').all()

    return render_template('book_list.html', books=books)


@books_bp.route('/books/<int:book_id>', methods=['GET'])
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


@books_bp.route('/books/<int:book_id>', methods=['POST'])
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


@books_bp.route('/lovedbooks', methods=['GET'])
def book_form():

    return render_template('reference_books.html')


@books_bp.route('/lovedbooks', methods=['POST'])
def process_books():

    # see reference_books.html
    # returns a list of each book
    book_data = request.form.get('books').split()
    anon_user = add_anon_user()

    # Alternative: fetch THE pre-existing anon user. 
    # use session to track current user ratings data
    # anon_user = User.query.filter(username='anonymous')

    book_ids = [get_book_id(book) for book in book_data]
    for book_id in book_ids:
        add_rating(anon_user.id, book_id)

    #write csv file to send to Surprise library
    write_rating_data()

    #set user_id in session
    session['user_id'] = anon_user.id

    return redirect('/lovedbooksresults')


@books_bp.route('/lovedbooksresults', methods=['GET'])
def display_favorite_books():

    user_id = session.get('user_id')
    neighbors_lst = get_nearest_neighbors(int(user_id)) #from ml.py
    
    #from database_functions.py
    user_book_lst = create_user_list(int(user_id))
    neighbors_dict = create_neighbors_book_dict(neighbors_lst, user_book_lst, 5)
    recommendation_lst = get_recommendations_lst(neighbors_dict)
    print(recommendation_lst)


    return render_template('loved_books_result.html', recommendation_lst=recommendation_lst)
