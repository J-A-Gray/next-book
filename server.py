"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Book, Rating


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

    user = User.query.filter_by(email = email).first()

    if not user:
        flash("You are not yet registered!")
        return redirect('/register')

    if user.password != password:
        flash("That's not the right password. Try again?")
        return redirect('/login')

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