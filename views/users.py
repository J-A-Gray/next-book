from flask import Blueprint

users_bp = Blueprint('users', __name__, template_folder='templates/users')


@users_bp.route('/users')
def user_list():
    """Show list of users"""

    users = User.query.all()
    return render_template('user_list.html', users=users)


@users_bp.route('/users/<int:user_id>')
def user_detail(user_id):

    user = User.query.get(user_id)
    return render_template('user.html', user=user)
