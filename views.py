"""The views module.

This module contain all of the routes for the application.
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from membersapp import app, mail
from helpers import (connect, get_age, get_reset_token,
                     verify_reset_token)
from forms import (RegisterForm, LoginForm, MemberForm, SearchForm,
                   ResetRequestForm, ResetPasswordForm)
from flask import render_template, flash, redirect, url_for, request, session
from flask_mail import Message
from passlib.hash import sha256_crypt
from functools import wraps


# Home Page
@app.route('/')
def index():
    """The route for the home screen.

    Decorators:
        app.route

    Returns:
    Renders template for home page
    """
    return render_template('index.html', Title="Home")


# User register
@app.route('/register', methods=['GET', 'POST'])
def register():
    """The route for the register screen.

    This routes a user to a form to register for access to the application.

    Decorators:
        app.route

    Returns:
        Renders template for registration page upon get request
        Renders template for login page upon successful post request
    """
    try:
        if session['username']:
            flash(f'You are already logged in as {session["username"]}', 'info')
            return redirect(url_for('dashboard'))
    except:
        form = RegisterForm()
        if form.validate_on_submit():
            first_name = request.form['first_name'].title()
            last_name = request.form['last_name'].title()
            username = request.form['username']
            email = request.form['email'].lower()
            password = sha256_crypt.hash(str(request.form['password']))

            values = (first_name,
                    last_name,
                    username,
                    email,
                    password,
                    'pending',
                    datetime.now())
            # Get a connection to database
            conn, cur = connect()

            # Get cursor and execute query
            with cur as cur:
                sql = '''INSERT INTO admins(
                            first_name,
                            last_name,
                            username,
                            email,
                            password,
                            role,
                            registered_date)
                        VALUES(%s, %s, %s, %s, %s, %s, %s)'''
                cur.execute(sql, values)

            # Commit
            conn.commit()

            # Close cursor
            cur.close()

            # Close connection
            conn.close()

            flash("You are now registered, but your account is 'pending' authorization. You will receive an email once your account is approved.", 'info')
            return redirect(url_for('index'))

        else:
            return render_template('register.html', Title="Register", form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
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
    try:
        if session['username']:
            flash(f'You are already logged in as {session["username"]}', 'info')
            return redirect(url_for('dashboard'))
    except:
        form = LoginForm()
        if form.validate_on_submit():
            # Get form field
            email = request.form['email'].lower()
            password_candidate = request.form['password']

            # Get a connection to database
            conn, cur = connect()

            # Get user by username
            cur.execute("SELECT * FROM admins WHERE email = %s",
                            [email])
            data = cur.fetchone()

            if data:
                if data['role'] != 'admin':
                    flash('Please contact the Database Administrator.',
                            'danger')
                    return render_template(
                            'login.html', Title="Login", form=form)
                else:
                    # Get stored hash
                    password = data['password']

                    # Compare passwords
                    if sha256_crypt.verify(password_candidate, password):
                        # Passed
                        session['email'] = email.lower()
                        session['username'] = data['username']
                        session['logged_in'] = True
                        flash('You are now logged in', 'success')
                        return redirect(url_for('dashboard'))
                    else:
                        flash('Invalid password.', 'warning')
                        return render_template(
                            'login.html', Title="Login", form=form)

            else:
                flash('Invalid username and/or password!', 'danger')
                return render_template('login.html', Title="Login", form=form)

            # Close dictionary cursor
            cur.close()

            # Close connection
            conn.close()

        return render_template('login.html', Title="Login", form=form)


# Reset Request Form
@app.route('/reset_request', methods=['GET', 'POST'])
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
    try:
        if session['email']:
            flash('You must log out before resetting password!', 'warning')
            return redirect(url_for('dashboard'))
    except:
        form = ResetRequestForm()
        if form.validate_on_submit():
            # Get form field
            email = request.form['email'].lower()
            # Get a connection to database
            conn, cur = connect()
            try:
                # Check to see if email exist
                cur.execute("SELECT * FROM admins WHERE email = %s",
                                 [email])
                data = cur.fetchone()
                user = data['email']
                user_id = data['admin_id']

                if data is None:
                    flash('There is no account with that email.',
                          'warning')
                    return render_template('reset_request.html',
                                           Title="Request Password Reset",
                                           form=form)

                else:
                    # Obtain a token
                    token = get_reset_token(user, user_id)

                    # Create and send an email to send user with link
                    # containing generated token
                    msg = Message(subject='Reset Password ',
                                  sender=os.environ.get('MAIL_USERNAME'),
                                  recipients=[user])
                    msg.body = f'''To reset your password, visit the following
link: {url_for('reset_password', token=token, _external=True)}

If you did not make this request, then simply ignore this email and
no changes will be made.
'''
                    mail.send(msg)
                    flash('''An email has been sent with instructions to reset
                          your password''', 'info')
                    return redirect(url_for('login'))

            except:
                flash('There is no account with that email.', 'warning')

            # Close dictionary cursor
            cur.close()

            # Close connection
            conn.close()

    return render_template('reset_request.html',
                           Title="Request Password Reset",
                           form=form)


# Reset Password Form
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
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
    try:
        if session['email']:
            flash('You must log out before resetting password!', 'warning')
            return redirect(url_for('dashboard'))
    except:
        # Obtain user of token
        user = verify_reset_token(token)
        if user is None:
            flash('That is an invalid or expired token.', 'warning')
            return redirect(url_for('reset_request'))
        else:
            form = ResetPasswordForm()
            if form.validate_on_submit():

                # Get form field
                password = request.form['password']
                confirm = request.form['confirm']

                # Hash user password
                new_password = sha256_crypt.hash(str(password))

                values = (new_password, user)
                # Get a connection to database
                conn, cur = connect()

                # Get cursor and execute query
                with cur as cur:
                    sql = ''' UPDATE admins
                              SET password = %s
                              WHERE email = %s'''
                    cur.execute(sql, values)

                # Commit
                conn.commit()

                # Close cursor
                cur.close()

                # Close connection
                conn.close()

                flash('Your password has been updated.', 'success')
                return redirect(url_for('login'))
            else:
                return render_template('reset_password.html',
                                       Title='Reset Password',
                                       form=form)


def is_logged_in(f):
    """Check if user logged in.

    The function checks to see if a user is logged in the application to
    prevent access to pages that requires a user to be logged in.

    Decorators:
        wraps

    Arguments:
        f

    Returns:
        wrap
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    """The route for application dashboard.

    This functions displays the user's dashboard.

    Decorators:
        app.route
        is_logged_in

    Returns:
        Renders dashboard html page
    """
    # Get a connection to database
    conn, cur = connect()


    # Get Members
    cur.execute("SELECT * FROM members ORDER BY last_name ASC")

    members = cur.fetchall()

    if members:
        return render_template('dashboard.html',
                               Title="Dashboard",
                               members=members)

    else:
        msg = 'No Members Found'
        return render_template('dashboard.html',
                               Title="Dashboard",
                               msg=msg)
    # Close dictionary cursor
    cur.close()

    # Close connection
    conn.close()


# Admin
@app.route('/admin')
@is_logged_in
def admin():
    """The route for admin page.

    This funtions displays the admin page..

    Decorators:
        app.route
        is_logged_in

    Returns:
        Renders admin html page
    """
    # Get a connection to database
    conn, cur = connect()

    # Get Members
    cur.execute("SELECT * FROM admins ORDER BY last_name ASC")

    admins = cur.fetchall()

    if admins:
        return render_template('admin.html',
                               Title="Admins",
                               admins=admins)

    else:
        msg = 'No Members Found'
        return render_template('admin.html',
                               Title="Admin",
                               msg=msg)
    # Close dictionary cursor
    cur.close()

    # Close connection
    conn.close()


# Update role
@app.route('/update_role/<string:admin_id>/role/<string:role>',
           methods=['GET', 'POST'])
@is_logged_in
def update_role(admin_id, role):
    """The route for updating admin role.

    This functions allows admin user to toggle admin role between 'admin'
    and 'pending'. 'admin' role can log into application, but 'pending' role
    cannot log into the application.

    Decorators:
        is_logged_in

    Arguments:
        admin_id  -- admin user id
        role  -- role assigned ot admin user

    Returns:
        Renders admin html page
    """
    if request.method == 'POST':
        if role == 'pending':
            role = 'admin'
        else:
            role = 'pending'

        values = (role, admin_id)

        # Get a connection to database
        conn, cur = connect()

        # Get a cursor and execute query
        with cur as cur:
            sql = ''' UPDATE admins
                      SET role = %s
                      WHERE admin_id = %s'''
            cur.execute(sql, values)

        # Commit
        conn.commit()

        # Close cursor
        cur.close()

        # Close connection
        conn.close()

        flash('Role Updated!', 'success')

        return redirect(url_for('admin'))

    return render_template('admin.html',
                           Title="Admin", admin_id=admin_id)


# Search for Member(s)
@app.route('/search', methods=['GET', 'POST'])
@is_logged_in
def search():
    """The route for the search screen.

    This function allows admin to search database for a user.

    Decorators:
        app.route
        is_logged_in

    Returns:
        Renders template for search page upon get request
        Renders template for dashboard upon successful post request
    """
    form = SearchForm()
    if form.validate_on_submit():
        search_first_name = request.form['search_first_name'].title()
        search_last_name = request.form['search_last_name'].title()

        # Get a connection to database
        conn, cur = connect()

        # Get Members
        cur.execute(
            '''SELECT * FROM members
               WHERE first_name like %s
               AND last_name like %s
               ORDER BY last_name ASC''', (
                ('%' + search_first_name + '%'),
                ('%' + search_last_name + '%')))

        members = cur.fetchall()

        if members:
            return render_template('dashboard.html',
                                   Title="Dashboard",
                                   members=members)

        else:
            flash('No members found, please try again.', 'info')
            return redirect(url_for('search'))

        # Close dictionary cursor
        cur.close()

        # Close connection
        conn.close()

    return render_template('search.html', Title="Search", form=form)


# Add Member
@app.route('/add_member', methods=['GET', 'POST'])
@is_logged_in
def add_member():
    """The route for the add member screen.

    This function allows admin to add a user to the database..

    Decorators:
        app.route
        is_logged_in

    Returns:
        Renders template for add member page upon get request
        Renders template for dashboard upon successful post request
    """
    form = MemberForm()
    if form.validate_on_submit():
        first_name = request.form['first_name'].title()
        last_name = request.form['last_name'].title()
        street_num = request.form['street_num']
        street_name = request.form['street_name'].title()
        city = request.form['city'].title()
        state = request.form['state'].upper()
        postal_code = request.form['postal_code']
        contact_num = request.form['contact_num']
        email = request.form['email'].lower()
        birthdate = request.form['birthdate']

        # Get a connection to database
        conn, cur = connect()

        # Get curson and execute query

        cur.execute('''INSERT INTO members (
                first_name,
                last_name,
                street_num,
                street_name,
                city,
                _state,
                postal_code,
                contact_num,
                email,
                birthdate)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''',(first_name,
                 last_name,
                 street_num,
                 street_name,
                 city,
                 state,
                 postal_code,
                 contact_num,
                 email,
                 birthdate))

        # Commit
        conn.commit()

        # Close cursor
        cur.close()

        # Close connection
        conn.close()

        flash('Member Added!', 'success')
        return redirect(url_for('dashboard'))
    else:
        return render_template('add_member.html', Title="Add Member", form=form)


# Edit Member
@app.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_member(member_id):
    """The edit member route.

    This function allows admin to edit a member data in the database.

    Decorators:
        app.route
        is_logged_in

    Arguments:
        member_id  -- member's id

    Returns:
        Renders template for edit member page upon get request
        Renders template for dashboard upon successful post request
    """
    # Get a connection to database
    conn, cur = connect()

    # Execute
    cur.execute("SELECT * FROM members where member_id = %s", [member_id])

    member = cur.fetchone()

    # Close dictionary cursor
    cur.close()

    # Get form
    form = MemberForm()
    if not form.validate_on_submit():
        # Populate member fields
        form.first_name.data = member['first_name']
        form.last_name.data = member['last_name']
        form.street_num.data = member['street_num']
        form.street_name.data = member['street_name']
        form.city.data = member['city']
        form.state.data = member['_state']
        form.postal_code.data = member['postal_code']
        form.contact_num.data = member['contact_num']
        form.email.data = member['email']
        form.birthdate.data = member['birthdate']

        return render_template('edit_member.html',
                            Title="Edit Member", member_id=member[0], form=form)

    else:
        first_name = request.form['first_name'].title()
        last_name = request.form['last_name'].title()
        street_num = request.form['street_num']
        street_name = request.form['street_name'].title()
        city = request.form['city'].title()
        state = request.form['state'].upper()
        postal_code = request.form['postal_code']
        contact_num = request.form['contact_num']
        email = request.form['email'].lower()
        birthdate = request.form['birthdate']

        values = (first_name,
                  last_name,
                  street_num,
                  street_name,
                  city,
                  state,
                  postal_code,
                  contact_num,
                  email,
                  birthdate,
                  member[0])


        # Get a connection to database
        conn, cur = connect()

        # Get cursor and execute query
        with cur as cur:
            sql = ''' UPDATE members
                      SET
                        first_name = %s,
                        last_name = %s,
                        street_num = %s,
                        street_name = %s,
                        city = %s,
                        _state = %s,
                        postal_code = %s,
                        contact_num = %s,
                        email = %s,
                        birthdate = %s
                      WHERE member_id = %s'''

            cur.execute(sql, values)


        # Commit
        conn.commit()

        # Close cursor
        cur.close()

        # Close connection
        conn.close()

        flash('Member Updated!', 'success')
        return redirect(url_for('dashboard'))


# Delete Member
@app.route('/delete_member/<string:member_id>', methods=['GET', 'POST'])
@is_logged_in
def delete_member(member_id):
    """The first step to delete member route.

    This function allows admin to stage the deletion a member from the
    database.

    Decorators:
        app.route
        is_logged_in

    Arguments:
        member_id  -- member's id

    Returns:
        Renders template for delete member page upon get request
        Renders template for deleting a member upon successful post request
    """
    # Get a connection to database
    conn, cur = connect()

    # Execute
    cur.execute("SELECT * FROM members where member_id = %s", [member_id])
    member_to_delete = cur.fetchone()

    # Close dictionary cursor
    cur.close()

    # Close connection
    conn.close()

    return render_template(
        'delete_member_confirmation.html', member_to_delete=member_to_delete)


@app.route('/final_delete/<string:member_id>', methods=['POST'])
@is_logged_in
def final_delete(member_id):
    """The delete member route.

    This function allows admin to delete a member from the database.

    Decorators:
        app.route
        is_logged_in

    Arguments:
        member_id  -- member's id

    Returns:
        Renders dashboard page
    """
    # Get a connection to database

    values = [member_id]
    conn, cur = connect()

    # Get cursor
    with conn.cursor() as cur:
        sql = "DELETE FROM members where member_id = %s"
        cur.execute(sql, values)

    # Commit
    conn.commit()

    # Close cursor
    cur.close()

    # Close connection
    conn.close()

    flash('Member Deleted!', 'success')

    return redirect(url_for('dashboard'))


# Ages
@app.route('/ages')
@is_logged_in
def ages():
    """The member age route.

    This function displays the members age in html page in order of member's
    first name.

    Decorators:
        app.route
        is_logged_in

    Returns:
        Renders age html page
    """
    # Get a connection to database
    conn, cur = connect()

    cur.execute('''SELECT
                            first_name,
                            last_name,
                            extract(month from birthdate) AS month,
                            extract(day from birthdate) AS day,
                            extract(year from birthdate) AS year
                        FROM members
                        ORDER BY first_name''')

    members_ages = cur.fetchall()
    if members_ages is not None:
        birthdate_dict = {}
        birthdate_dict = {(member_age[1] + ", " + member_age[0]): str(get_age(
                          int(member_age[2]),
                          int(member_age[3]),
                          int(member_age[4])))
                          for member_age in members_ages}
        birthdate_dict_sorted = sorted(birthdate_dict.items())
        return render_template('ages.html',
                               Title="Member's Age",
                               birthdate_dict_sorted=birthdate_dict_sorted)

    else:
        msg = 'No members; therefore, no ages displayed.'
        return render_template('ages.html', Title="Member's Age", msg=msg)

    # Close dictionary cursor
    cur.close()

    # Close connection
    conn.close()


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    """The route to log out of the application.

    This function logs a user out of the application.

    Decorators:
        app.route
        is_logged_in

    Returns:
        Renders login page
    """
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))
