# -*- coding = utf-8 -*-
# @Time: 2023/2/26 10:43
# @File: user.PY
"""User System. Handle operations including signin, signup and sign out. Get and update user state"""

from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash

from ..database import db_session  # Not runable
from ..models import User

user_view = Blueprint('user_routes', __name__, template_folder='Backend/templates')


@user_view.route('/')
def home():
    # if 'username' in session:
    #     username = session['username']
    #     # return index template
    #     return redirect('/my_data')
    return redirect('/my_data')


@user_view.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        _form = request.form
        username = str(_form["username"])
        password = str(_form["password"])

        # if len(email) < 1 or len(password) < 1:
        #     return render_template('signin.html', error="Email and password are required")

        # todo verify via database

        # verification passed
        session['username'] = username
        return redirect("/")

        # return render_template('signin.html', error="Email or password incorrect")

    return render_template("signin.html")


@user_view.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'

        if error is None:
            try:
                user = User(username=username, email=email, password=generate_password_hash(password))
                db_session.add(user)
                db_session.commit()
            except db_session.IntegrityError:
                error = f'User {username} is already registered.'
            else:
                return redirect(url_for('user_routes.signin'))

        flash(error)
    return render_template('signup.html')
    # if len(username) < 1 or len(email) < 1 or len(password) < 1:
    #     return render_template('signup.html', error="All fields are required")
    #
    # # todo query if user already exist
    # #     new_user = ''
    # #
    # #     if new_user:
    # #         return render_template('signup.html', error="User already exists with this email")
    # #
    # # todo transmit data to database

    # register completed. redirect to a login page.
    #     return render_template('signin.html', username=username, msg="You've been registered!")
    #
    # return render_template('signup.html')


@user_view.route('/signout', methods=['GET'])
def signout():
    session.pop('username', None)
    return redirect('/')


@user_view.route('/user', methods=['GET'])
def show_user(id=None):
    ...
