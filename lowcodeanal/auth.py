# -*- coding = utf-8 -*-
# @Time: 2023/2/26 10:43
# @File: user.PY
"""User System. Handle operations including signin, signup and sign out. Get and update user state"""
import functools
from random import randint
from datetime import datetime, timedelta

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
# from lowcodeanal.app import mail
from models import User

from flask_mail import Message

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
        elif password != password_confirm:  # the two passwords are not the same
            error = 'The passwords you have entered do not match.'

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

# password reset
# route to render the forgot password page
@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Email address not found.')
            return redirect(url_for('auth.forgot_password'))
        else:
            # generate an OTP and save it to user's data
            otp = randint(100000, 999999)
            user.otp = otp
            user.otp_expiry = datetime.utcnow() + timedelta(minutes=5) # OTP will expire in 5 minutes
            db_session.commit()

            # send the OTP to user's email
            msg = Message('Reset Password - OTP Verification', recipients=[email])
            msg.body = f"Hello {user.username},\n\nYour OTP for resetting your password is {otp}. This OTP will expire in 5 minutes. Please use this OTP to reset your password.\n\nThank you,\nExample Company"
            from lowcodeanal.app import mail
            mail.send(msg) # assuming you have a Flask-Mail instance named mail

            session['reset_email'] = email # store the email in session for verification in reset_password() view
            session['otp'] = otp # store the OTP in session for verification in reset_password() view
            session['otp_expiry'] = user.otp_expiry # store the OTP expiry in session for verification in reset_password() view
            flash('An OTP has been sent to your email address.')
            return redirect(url_for('auth.reset_password'))

    return render_template('auth/forgot_password.html')

# route to render the reset password page
@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        otp = request.form['otp']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        email = session.get('reset_email')
        otp_session = session.get('otp')
        otp_expiry= session.get('otp_expiry')
        if not email:
            flash('Invalid request.')
            return redirect(url_for('auth.forgot_password'))
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Invalid request.')
            return redirect(url_for('auth.forgot_password'))
            if not otp_session or otp_session != int(otp) or otp_expiry.replace(
                    tzinfo=timezone.utc) < datetime.utcnow().replace(tzinfo=timezone.utc):
                flash('Invalid OTP.')
            return redirect(url_for('auth.reset_password'))
        elif password != password_confirm:
            flash('The two passwords you entered are not the same.')
            return redirect(url_for('auth.reset_password'))
        else:
            # reset the password and clear the OTP
            user.password = generate_password_hash(password, salt_length=128)
            db_session.commit()

            session.pop('reset_email', None)
            flash('Your password has been reset successfully. Please log in with your new password.')
            return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')

#
# @bp.route('/user', methods=['GET'])
# def show_user(id=None):
#     ...
