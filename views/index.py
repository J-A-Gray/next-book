from flask import Blueprint

main_bp = Blueprint('home', __name__, template_folder='templates')


@main_bp.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@main_bp.route('/register', methods=['GET'])
def register_form():
    """Display form for user signup."""

    return render_template("registration_form.html")


@main_bp.route('/register', methods=['POST'])
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


@main_bp.route('/login', methods=['GET'])
def login_form():
    """Display login form."""

    return render_template("login_form.html")


@main_bp.route('/login', methods=['POST'])
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


@main_bp.route('/logout')
def logout():
    """Log user out."""
    del session['user_id']
    flash("Bye! Happy Reading!")
    return redirect('/')

