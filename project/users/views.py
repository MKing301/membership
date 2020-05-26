import os
import logging

from datetime import datetime
from flask_login import login_user, current_user, logout_user, login_required
from project import db, mail
from project.models import User, Member
from flask_mail import Message
from passlib.hash import sha256_crypt
from project.users.forms import (RegisterForm, LoginForm, MemberForm, SearchForm,
                                 ResetRequestForm, ResetPasswordForm)
from flask import render_template, flash, redirect, url_for,request, Blueprint
from logging.handlers import TimedRotatingFileHandler


users = Blueprint('users', __name__)


# Set Logger
logger = logging.getLogger(__name__)

# Set logging level
logger.setLevel(logging.DEBUG)

# Define logging formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create file handler to rotate based on time
file_handler = TimedRotatingFileHandler(
    '/home/mfsd1809/Dev/FullStackWebDeveloper/GitRepos/membership/project/log_dir/users_log.log',
    when='m',
    interval=1,
    backupCount=6)

# Here we set our logHandler's formatter
file_handler.setFormatter(formatter)

# Add handler
logger.addHandler(file_handler)


STATES = [("", ""), ("AL", "AL"), ("AK", "AK"), ("AZ", "AZ"), ("AR","AR"),
          ("CA", "CA"), ("CO", "CO"), ("CT", "CT"), ("DC", "DC"), ("DE", "DE"),
          ("FL", "FL"), ("GA", "GA"), ("HI", "HI"), ("ID", "ID"), ("IL", "IL"),
          ("IN", "IN"), ("IA", "IA"), ("KS", "KS"), ("KY", "KY"), ("LA", "LA"),
          ("ME", "ME"), ("MD", "MD"), ("MA", "MA"), ("MI", "MI"), ("MN", "MN"),
          ("MS", "MS"), ("MO", "MO"), ("MT", "MT"), ("NE", "NE"), ("NV", "NV"),
          ("NH", "NH"), ("NJ", "NJ"), ("NM", "NM"), ("NY", "NY"), ("NC", "NC"),
          ("ND", "ND"), ("OH", "OH"), ("OK", "OK"), ("OR", "OR"), ("PA", "PA"),
          ("RI", "RI"), ("SC", "SC"), ("SD", "SD"), ("TN", "TN"), ("TX", "TX"),
          ("UT","UT"), ("VT", "VT"), ("VA", "VA"), ("WA", "WA"), ("WV","WV"),
          ("WI", "WI"), ("WY","WY")]


# User register
@users.route('/register', methods=['GET', 'POST'])
def register():
    """The route for the register screen.

    This routes a user to a form to register for access to the application.

    Decorators:
        app.route

    Returns:
        Renders template for registration page upon get request
        Renders template for login page upon successful post request
    """
    if current_user.is_authenticated:
            flash(f'You are already logged in as {current_user.username}. You must log out to register another user.', 'info')
            return redirect(url_for('main.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = sha256_crypt.hash(form.password.data)
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    username=form.username.data,
                    email=form.email.data,
                    password=hashed_password,
                    role='locked',
                    registered_date=datetime.now().strftime("%Y %m %d %H:%M:%S"))
        db.session.add(user)
        db.session.commit()

        flash("You are now registered, but your account is 'pending' authorization. You will receive an email once your account is approved.", 'info')
        logger.info(f'{user.first_name} {user.last_name} - Username: {user.username} registered.')
        return redirect(url_for('main.index'))

    else:
        return render_template('register.html', Title="Register", form=form)


# User login
@users.route('/login', methods=['GET', 'POST'])
def login():
    """The route for the login screen.

    This routes a user to a form to login the application.

    Decorators:
        app.route

    Returns:
        Renders template for login page upon get request are unsuccesful post
        request

        Renders template for dashboard page upon successful post request
    """
    if current_user.is_authenticated:
            flash(f'You are already logged in as {current_user.username}. You must log out to login as another user.', 'info')
            return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and sha256_crypt.verify(form.password.data, user.password):
            if user.role == 'admin':
                user.authenticate = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                next_page = request.args.get('next')
                flash('You are now logged in', 'success')
                logger.info(f'{user.username} logged into app.')
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
            else:
                flash('Invalid username and/or password!', 'danger')
                return render_template('login.html', Title="Login", form=form)
        else:
            flash('Please contact the Database Administrator.',
                        'danger')
            return render_template(
                        'login.html', Title="Login", form=form)

    return render_template('login.html', Title="Login", form=form)



# Reset Request Form
@users.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    """The route for the password reset request screen.

    This function first checks to see if a user is logged in the application.
    It routes a user to a form to enter email to submit a request to reset
    their password. If the user exist, it will send the user an email with a
    link to rest their passord.

    Decorators:
        app.route

    Returns:
        Renders template for password reset request on get request
        Renders template for dashboard if user logged in
        Renders login screen if email successfully sent to user
    """
    if current_user.is_authenticated:
            flash(f'You are already logged in as {user.username}. You must log out to reset password.', 'info')
            return redirect(url_for('main.dashboard'))
    else:
        form = ResetRequestForm()
        if form.validate_on_submit():
            # Get form field
            email = request.form['email'].lower()

            try:
                # Check to see if email exist
                data = db.session.query(User).filter(User.email==email).first()
                user = data.email
                user_id = data.id

                if not user:
                    flash('There is no account with that email.',
                          'warning')
                    return render_template('reset_request.html',
                                           Title="Request Password Reset",
                                           form=form)

                else:
                    # Obtain a token
                    token = data.get_reset_token()

                    # Create and send an email to send user with link
                    # containing generated token
                    msg = Message(subject='Reset Password ',
                                  sender=os.environ.get('MAIL_USERNAME'),
                                  recipients=[user])
                    msg.body = f'''To reset your password, visit the following
link: {url_for('users.reset_password', token=token, _external=True)}

If you did not make this request, then simply ignore this email and
no changes will be made.
'''
                    mail.send(msg)
                    flash('''An email has been sent with instructions to reset
                          your password''', 'info')
                    logging.info(f'Email sent to {user} to reset password.')
                    return redirect(url_for('users.login'))

            except Exception as e:
                logger.exception(f'Exception: {e}')
                flash('There is no account with that email.', 'warning')


    return render_template('reset_request.html',
                           Title="Request Password Reset",
                           form=form)


# Reset Password Form
@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """The route for the password reset request screen.

    This function first checks to see if a user is logged in the application.
    It verifies the user of the provided token from url in the email sent to
    the user.  It routes a user to a form to enter new password, hash the
    password and updates the user's password in the datebase on successful post
    request.

    Decorators:
        app.route

    Returns:
        Renders template to reset password on get requests
        Renders template for dashboard if user logged in
        Renders login screen after database updated with new password
    """
    if current_user.is_authenticated:
            flash(f'You are already logged in as {current_user.username}. You must log out to register another user.', 'info')
            return redirect(url_for('main.dashboard'))
    else:
        # Obtain user of token
        user = User.verify_reset_token(token)
        if user is None:
            flash('That is an invalid or expired token.', 'warning')
            return redirect(url_for('users.reset_request'))

        form = ResetPasswordForm()
        if form.validate_on_submit():

            # Get form field
            password = request.form['password']
            confirm = request.form['confirm']

            # Hash user password
            new_password = sha256_crypt.hash(str(password))

            user.password = new_password
            db.session.commit()

            flash('Your password has been updated.', 'success')
            logger.info(f'{user.first_name} {user.last_name} changed password.')
            return redirect(url_for('users.login'))
        else:
            return render_template('reset_password.html',
                                    Title='Reset Password',
                                    form=form)


@users.route("/logout")
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    flash('Signed out!', 'success')
    return redirect(url_for('main.index'))