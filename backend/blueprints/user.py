# -*- coding = utf-8 -*-
# @Time: 2023/2/26 10:43
# @File: user.PY
"""User System. Handle operations including signin, signup and sign out. Get and update user state"""

from flask import Blueprint, request, render_template, session, redirect

user_view = Blueprint('user_routes', __name__, template_folder='Backend/templates')


@user_view.route('/')
def home():
    if 'username' in session:
        username = session['username']
        # return index template
        return 'Logged in as ' + username + '<br>' + \
         "<b><a href = '/logout'>click here to log out</a></b>"
    return "You are not logged in <br><a href = '/signin'></b>" + \
      "click here to log in</b></a>"


@user_view.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        _form = request.form
        username = str(_form["username"])
        # password = str(_form["password"])

        # if len(email) < 1 or len(password) < 1:
        #     return render_template('signin.html', error="Email and password are required")

        return redirect("/")

        # return render_template('signin.html', error="Email or password incorrect")

    return render_template("signin.html")


@user_view.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if len(username) < 1 or len(email) < 1 or len(password) < 1:
            return render_template('signup.html', error="All fields are required")

    #     # query if user already exist
    #     new_user = ''
    #
    #     if new_user:
    #         return render_template('signup.html', error="User already exists with this email")
    #
        # register completed.
        # todo redirect to a new page.
        return render_template('signup.html', msg="You've been registered!")

    return render_template('signup.html')


@user_view.route('/signout', methods=['GET'])
def signout():
    ...


@user_view.route('/user', methods=['GET'])
def show_user(id=None):
    ...

