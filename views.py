"""summary.

[description]
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from membersapp import app, mail
from helpers import get_age, get_reset_token, verify_reset_token
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

    Returns:
    Render template for home page with title of page
    """
    return render_template('index.html', Title="Home")


# User register
@app.route('/register', methods=['GET', 'POST'])
def register():
    """.

    [description]

    Decorators:
        app.route

    Returns:
        [type] -- [description]
    """
    form = RegisterForm()
    if form.validate_on_submit():
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = sha256_crypt.hash(str(request.form['password']))

        # Get a connection
        conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                                user=os.environ.get('DB_USER'),
                                password=os.environ.get('DB_PASSWORD'),
                                host='localhost')
        # conn.cursor will return a cursor object, you can use this cursor to
        # perform queries
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # TODO hard-coded role as pending for now
        dict_cur.execute(
            '''INSERT INTO admins(
                   first_name,
                   last_name,
                   username,
                   email,
                   password,
                   role,
                   registered_date)
               VALUES(%s, %s, %s, %s, %s, %s, %s)
               ''', (first_name, last_name, username, email, password,
                     'pending', datetime.now()))

        # commit to db
        conn.commit()

        # close db connection
        conn.close()

        flash('You are now registered and can log in!', 'success')
        return redirect(url_for('login'))

    else:
        return render_template('register.html', Title="Register", form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """.

    [description]

    Decorators:
        app.route

    Returns:
        [type] -- [description]
    """
    form = LoginForm()
    if form.validate_on_submit():
        # Get form field
        email = request.form['email']
        password_candidate = request.form['password']

        # Get a connection
        conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                                user=os.environ.get('DB_USER'),
                                password=os.environ.get('DB_PASSWORD'),
                                host='localhost')
        # conn.cursor will return a cursor object, you can use this cursor to
        # perform queries
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get user by username
        dict_cur.execute("SELECT * FROM admins WHERE email = %s",
                         [email])
        data = dict_cur.fetchone()

        if data:
            # Get stored hash
            password = data['password']

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['email'] = email.upper()
                session['username'] = data['username'].upper()
                if data['role'] == 'admin':
                    session['logged_in'] = True
                    flash('You are now logged in', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Please contact the Database Administrator.',
                          'danger')
                    return render_template(
                        'login.html', Title="Login", form=form)
            else:
                flash('Invalid password.', 'warning')
                return render_template('login.html', Title="Login", form=form)

        else:
            flash('Invalid username and/or password!', 'danger')
            return render_template('login.html', Title="Login", form=form)

        # close connection
        conn.close()

    return render_template('login.html', Title="Login", form=form)


# Reset Request Form @ 22:27
@app.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    """.

    [description]

    Decorators:
        app.route

    Returns:
        [type] -- [description]
    """
    try:
        if session['email']:
            flash('You must log out before resetting password!', 'warning')
            return redirect(url_for('dashboard'))
    except:
        form = ResetRequestForm()
        if form.validate_on_submit():
            # Get form field
            email = request.form['email']
            # Get a connection
            conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                                    user=os.environ.get('DB_USER'),
                                    password=os.environ.get('DB_PASSWORD'),
                                    host='localhost')
            # conn.cursor will return a cursor object, you can use this cursor
            # to perform queries
            dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            try:
                # Check to see if email exist
                dict_cur.execute("SELECT * FROM admins WHERE email = %s",
                                 [email])
                data = dict_cur.fetchone()
                user = data['email']
                user_id = data['admin_id']

                if data is None:
                    flash('There is no account with that email.',
                          'warning')
                    return render_template('reset_request.html',
                                           Title="Request Password Reset",
                                           form=form)

                else:
                    token = get_reset_token(user, user_id)
                    msg = Message(subject='Reset Password ',
                                  sender=os.environ.get('MAIL_USERNAME'),
                                  recipients=[user])
                    msg.body = f'''To reset your password, visit the following
link: {url_for('reset_password', token=token, _external=True)}

If you did not make this request, then simply ignore this email and
no changes will be made.
'''
                    mail.send(msg)
                    flash('''An email has been sent with instructions to reset your
                          password''', 'info')
                    return redirect(url_for('login'))

                    # close connection
                    conn.close()
            except:
                flash('There is no account with that email.', 'warning')

    return render_template('reset_request.html',
                           Title="Request Password Reset",
                           form=form)


# Reset Password Form @ 18:33 / 34:08
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """.

    [description]

    Decorators:
        app.route

    Returns:
        [type] -- [description]
    """
    try:
        if session['email']:
            flash('You must log out before resetting password!', 'warning')
            return redirect(url_for('dashboard'))
    except:
        # TODO verify token (see time @ 6:18)
        user = verify_reset_token(token)
        if user is None:
            flash('That is an invalid or expired token.', 'warning')
            return redirect(url_for('reset_request'))
        else:
            form = ResetPasswordForm()
            if form.validate_on_submit():
                # Get form field
                password = request.form['password']
                print(password)
                confirm = request.form['confirm']

                # TODO (see time @ 34:13)
                new_password = sha256_crypt.hash(str(password))
                print(new_password)

                # Get a connection
                conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                                        user=os.environ.get('DB_USER'),
                                        password=os.environ.get('DB_PASSWORD'),
                                        host='localhost')
                # conn.cursor will return a cursor object, you can use this cursor
                # to perform queries
                dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                dict_cur.execute(''' UPDATE admins
                                 SET password = %s
                                 WHERE email = %s''', (new_password, user))

                # Commit
                conn.commit()

                # Close Connection
                conn.close()

                flash('Your password has been updated.', 'success')
                return redirect(url_for('login'))
            else:
                return render_template('reset_password.html',
                                       Title='Reset Password',
                                       form=form)


# Check if user logged in
def is_logged_in(f):
    """.

    [description]

    Decorators:
        wraps

    Arguments:
        f {[type]} -- [description]

    Returns:
        [type] -- [description]
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
    """[summary.

    [description]

    Decorators:
        app.route
        is_logged_in

    Returns:
        [type] -- [description]
    """
    # Get a connection
    conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                            user=os.environ.get('DB_USER'),
                            password=os.environ.get('DB_PASSWORD'),
                            host='localhost')

    # conn.cursor will return a cursor object, you can use this cursor to
    # perform queries
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get Members
    dict_cur.execute("SELECT * FROM members ORDER BY last_name ASC")

    members = dict_cur.fetchall()

    if members:
        return render_template('dashboard.html',
                               Title="Dashboard",
                               members=members)

    else:
        msg = 'No Members Found'
        return render_template('dashboard.html',
                               Title="Dashboard",
                               msg=msg)

    # Close connection
    conn.close()


# Admin
@app.route('/admin')
@is_logged_in
def admin():
    """[summary.

    [description]

    Decorators:
        app.route
        is_logged_in

    Returns:
        [type] -- [description]
    """
    # Get a connection

    conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                            user=os.environ.get('DB_USER'),
                            password=os.environ.get('DB_PASSWORD'),
                            host='localhost')

    # conn.cursor will return a cursor object, you can use this cursor to
    # perform queries
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get Members
    dict_cur.execute("SELECT * FROM admins ORDER BY last_name ASC")

    admins = dict_cur.fetchall()

    if admins:
        return render_template('admin.html',
                               Title="Admins",
                               admins=admins)

    else:
        msg = 'No Members Found'
        return render_template('admin.html',
                               Title="Admin",
                               msg=msg)

    # Close connection
    conn.close()


# Update role
@app.route('/update_role/<string:admin_id>/role/<string:role>',
           methods=['GET', 'POST'])
@is_logged_in
def update_role(admin_id, role):
    """[summary].

    [description]

    Decorators:
        is_logged_in

    Arguments:
        admin_id {[type]} -- [description]
        role {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    if request.method == 'POST':
        if role == 'pending':
            role = 'admin'
        else:
            role = 'pending'
        # Get a connection
        conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                                user=os.environ.get('DB_USER'),
                                password=os.environ.get('DB_PASSWORD'),
                                host='localhost')

        # conn.cursor will return a cursor object, you can use this cursor to
        # perform queries
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Execute

        dict_cur.execute(
            ''' UPDATE admins
                SET role = %s
                WHERE admin_id = %s''', (role, admin_id))

        # Commit
        conn.commit()

        # Close Connection
        conn.close()

        flash('Role Updated!', 'success')

        return redirect(url_for('admin'))

    return render_template('admin.html',
                           Title="Admin", admin_id=admin_id)


# Search for Member(s)
@app.route('/search', methods=['GET', 'POST'])
@is_logged_in
def search():
    """[summary.

    [description]

    Decorators:
        app.route
        is_logged_in

    Returns:
        [type] -- [description]
    """
    form = SearchForm()
    if form.validate_on_submit():
        search_first_name = request.form['search_first_name'].capitalize()
        search_last_name = request.form['search_last_name'].capitalize()

        # Get a connection
        conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                                user=os.environ.get('DB_USER'),
                                password=os.environ.get('DB_PASSWORD'),
                                host='localhost')

        # conn.cursor will return a cursor object, you can use this cursor to
        # perform queries
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get Members
        dict_cur.execute(
            '''SELECT * FROM members
               WHERE first_name like %s
               AND last_name like %s
               ORDER BY last_name ASC''', (
                ('%' + search_first_name + '%'),
                ('%' + search_last_name + '%')))

        members = dict_cur.fetchall()

        if members:
            return render_template('dashboard.html',
                                   Title="Dashboard",
                                   members=members)

        else:
            msg = 'No Members Found'
            return render_template('dashboard.html',
                                   Title="Dashboard",
                                   msg=msg)

        # Close connection
        conn.close()

    return render_template('search.html', Title="Search", form=form)


# Add Member
@app.route('/add_member', methods=['GET', 'POST'])
@is_logged_in
def add_member():
    """.

    [description]

    Decorators:
        app.route
        is_logged_in

    Returns:
        [type] -- [description]
    """
    form = MemberForm()
    if form.validate_on_submit():
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        street_num = request.form['street_num']
        street_name = request.form['street_name']
        city = request.form['city']
        state = request.form['state']
        postal_code = request.form['postal_code']
        contact_num = request.form['contact_num']
        birthdate = request.form['birthdate']
        member_tier = request.form['member_tier']
        assigned_elder_first_name = request.form['assigned_elder_first_name']
        assigned_elder_last_name = request.form['assigned_elder_last_name']

        # Get a connection
        conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                                user=os.environ.get('DB_USER'),
                                password=os.environ.get('DB_PASSWORD'),
                                host='localhost')

        # conn.cursor will return a cursor object, you can use this cursor to
        # perform queries
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Execute
        dict_cur.execute(
            ''' INSERT INTO members (first_name,
                                     last_name,
                                     street_num,
                                     street_name,
                                     city,
                                     state,
                                     postal_code,
                                     contact_num,
                                     birthdate,
                                     member_tier,
                                     assigned_elder_first_name,
                                     assigned_elder_last_name)
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                        (first_name,
                         last_name,
                         street_num,
                         street_name,
                         city,
                         state,
                         postal_code,
                         contact_num,
                         birthdate,
                         member_tier,
                         assigned_elder_first_name,
                         assigned_elder_last_name))

        # Commit
        conn.commit()

        # Close Connection
        conn.close()

        flash('Member Added!', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_member.html', Title="Add Member", form=form)


# Edit Member
@app.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_member(member_id):
    """The edit member route.

    [description]

    Decorators:
        app.route
        is_logged_in

    Arguments:
        member_id {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    # Get a connection
    conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                            user=os.environ.get('DB_USER'),
                            password=os.environ.get('DB_PASSWORD'),
                            host='localhost')

    # conn.cursor will return a cursor object, you can use this cursor to
    # perform queries
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute
    dict_cur.execute("SELECT * FROM members where member_id = %s", [member_id])

    member = dict_cur.fetchone()

    # Get form
    form = MemberForm()

    # Populate member fields
    form.first_name.data = member['first_name']
    form.last_name.data = member['last_name']
    form.street_num.data = member['street_num']
    form.street_name.data = member['street_name']
    form.city.data = member['city']
    form.state.data = member['state']
    form.postal_code.data = member['postal_code']
    form.contact_num.data = member['contact_num']
    form.birthdate.data = member['birthdate']
    form.member_tier.data = member['member_tier']
    form.assigned_elder_first_name.data = member['assigned_elder_first_name']
    form.assigned_elder_last_name.data = member['assigned_elder_last_name']

    if request.method == 'POST' and form.validate():
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        street_num = request.form['street_num']
        street_name = request.form['street_name']
        city = request.form['city']
        state = request.form['state']
        postal_code = request.form['postal_code']
        contact_num = request.form['contact_num']
        birthdate = request.form['birthdate']
        member_tier = request.form['member_tier']
        assigned_elder_first_name = request.form['assigned_elder_first_name']
        assigned_elder_last_name = request.form['assigned_elder_last_name']

        # Get a connection
        conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                                user=os.environ.get('DB_USER'),
                                password=os.environ.get('DB_PASSWORD'),
                                host='localhost')

        # conn.cursor will return a cursor object, you can use this cursor to
        # perform queries
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Execute
        dict_cur.execute(
            ''' UPDATE members
                SET first_name = %s,
                last_name = %s,
                street_num = %s,
                street_name = %s,
                city = %s,
                state = %s,
                postal_code = %s,
                contact_num = %s,
                birthdate = %s,
                member_tier = %s,
                assigned_elder_first_name = %s,
                assigned_elder_last_name = %s
                WHERE member_id = %s''', (first_name,
                                          last_name,
                                          street_num,
                                          street_name,
                                          city,
                                          state,
                                          postal_code,
                                          contact_num,
                                          birthdate,
                                          member_tier,
                                          assigned_elder_first_name,
                                          assigned_elder_last_name,
                                          member[0]))

        # Commit
        conn.commit()

        # Close Connection
        conn.close()

        flash('Member Updated!', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_member.html',
                           Title="Edit Member", member_id=member[0], form=form)


# Delete Member
@app.route('/delete_member/<string:member_id>', methods=['GET', 'POST'])
@is_logged_in
def delete_member(member_id):
    """The delete member route.

    [description]

    Decorators:
        app.route
        is_logged_in

    Arguments:
        member_id {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    # Get a connection
    conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                            user=os.environ.get('DB_USER'),
                            password=os.environ.get('DB_PASSWORD'),
                            host='localhost')

    # conn.cursor will return a cursor object, you can use this cursor to
    # perform queries
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute
    dict_cur.execute("SELECT * FROM members where member_id = %s", [member_id])
    member_to_delete = dict_cur.fetchone()
    return render_template(
        'delete_member_confirmation.html', member_to_delete=member_to_delete)


@app.route('/final_delete/<string:member_id>', methods=['POST'])
@is_logged_in
def final_delete(member_id):
    """[summary.

    [description]

    Decorators:
        app.route
        is_logged_in

    Arguments:
        member_id {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    # Get a connection
    conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                            user=os.environ.get('DB_USER'),
                            password=os.environ.get('DB_PASSWORD'),
                            host='localhost')

    # conn.cursor will return a cursor object, you can use this cursor to
    # perform queries
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute
    dict_cur.execute("DELETE FROM members where member_id = %s", [member_id])

    # Commit
    conn.commit()

    # Close Connection
    conn.close()

    flash('Member Deleted!', 'success')

    return redirect(url_for('dashboard'))


# Ages
@app.route('/ages')
@is_logged_in
def ages():
    """[summary].

    [description]

    Decorators:
        app.route
        is_logged_in

    Returns:
        [type] -- [description]
    """
    # Get a connection
    conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                            user=os.environ.get('DB_USER'),
                            password=os.environ.get('DB_PASSWORD'),
                            host='localhost')

    # conn.cursor will return a cursor object, you can use this cursor to
    # perform queries
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # cur = conn.cursor() ---> used to return tuple

    # execute query
    # dict_cur.execute('SELECT * FROM log ORDER BY date_time DESC')
    dict_cur.execute('''SELECT
                            first_name,
                            last_name,
                            extract(month from birthdate) AS month,
                            extract(day from birthdate) AS day,
                            extract(year from birthdate) AS year
                        FROM members
                        ORDER BY first_name''')
    # dict_cur.execute('select users.first_name, users.last_name,
    # log.date_time from users, log where users.rfidtag= log.rfidtag ORDER BY
    # log.date_time DESC')

    members_ages = dict_cur.fetchall()
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

    # Close the communication with the PostgreSQL database
    dict_cur.close()
    conn.close()


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    """The route to log out of the application.

    [description]

    Decorators:
        app.route
        is_logged_in

    Returns:
        [type] -- [description]
    """
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))
