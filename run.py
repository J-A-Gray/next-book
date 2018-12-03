from flask import Flask 

from views.users import users_bp
from views.books import books_bp
from views.index import main_bp


app = Flask(__name__)

app.register_blueprint(users_bp)
app.register_blueprint(books_bp)
app.register_blueprint(main_bp)


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
