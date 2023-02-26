# -*- coding = utf-8 -*-
# @Time: 2023/2/26 10:43
# @File: user.PY
"""User System. Handle operations including signin, signup and sign out. Get and update user state"""
import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from sqlalchemy import exc
from datetime import datetime

from database import db_session
from models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter(User.id == user_id).first()


# @bp.route('/') # maybe add in a new blueprint
# def home():
#     # if 'username' in session:
#     #     username = session['username']
#     #     # return index template
#     #     return redirect('/my_data')
#     return redirect('/my_data')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        user = User.query.filter(User.username == username).first()

        if user is None or not check_password_hash(user.password, password):
            error = 'Incorrect username or password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            user.last_login = datetime.utcnow()
            db_session.commit()
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

    #     # if len(email) < 1 or len(password) < 1:
    #     #     return render_template('login.html', error="Email and password are required")
    #
    #     # todo verify via database
    #
    #     # verification passed
    #     session['username'] = username
    #     return redirect("/")
    #
    #     # return render_template('login.html', error="Email or password incorrect")
    #
    # return render_template("login.html")


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        password_reminder = request.form['password_reminder']
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        ## the two passwords are not the same
        elif password != password_confirm:
            error = 'The two passwords you entered are not the same.'

        if error is None:
            try:
                user = User(email=email, username=username, password=generate_password_hash(password, salt_length=128),
                            password_reminder=password_reminder)
                db_session.add(user)
                db_session.commit()
            except exc.IntegrityError:
                error = f'User {username} is already registered.'
            else:
                return redirect(url_for("auth.login"))

        flash(error)
    return render_template('auth/register.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#
# @bp.route('/user', methods=['GET'])
# def show_user(id=None):
#     ...
