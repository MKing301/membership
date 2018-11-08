"""summary.

[description]
"""

import psycopg2
import psycopg2.extras
from datetime import datetime
from membersapp import app
from forms import RegisterForm, LoginForm
from flask import render_template, flash, redirect, url_for, request
from passlib.hash import sha256_crypt


# Home Page
@app.route('/')
def index():
    """This is the route for the home screen.

    Returns:
    Render template for home page with title of page
    """
    return render_template('index.html', Title="Home")


# User register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = sha256_crypt.hash(str(request.form['password']))

        # Get a connection
        conn = psycopg2.connect(database='database_name',
                                user='database_user',
                                password='database_password',
                                host='localhost')
        # conn.cursor will return a cursor object, you can use this cursor to
        # perform queries
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # TODO hard-coded role as member for now
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
                     'member', datetime.now()))

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
    form = LoginForm()
    return render_template('login.html', Title="Login", form=form)
