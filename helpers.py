"""The helper functions.

[description]
"""
import os
import psycopg2
import psycopg2.extras
from membersapp import app
from flask import flash, redirect, url_for
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def connect():
    """Get database connection.

    This function establishes a connection with the database.

    Returns:
        conn -- connection to the dB
        cur -- cursor to execute queries in dB
    """
    # Get a connection to database
    try:
        conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                                user=os.environ.get('DB_USER'),
                                password=os.environ.get('DB_PASSWORD'),
                                host='localhost')
        # dict cursors allows access to the retrieved records using an
        # interface similar to the Python dictionaries to perform queries
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return conn, cur
    except:
        print("No connection to database established!")
        return None


def get_age(birthmonth, birthday, birthyear):
    """Get age.

    This function calculates the age of a member.

    Arguments:
    birthmonth -- member's birth month
    birthday -- member's birth day
    birthyear -- member's birth year

    Returns:
    [type] -- [description]
    """
    currentyear = datetime.now().year
    currentmonth = datetime.now().month
    currentday = datetime.now().day
    if currentyear >= birthyear:
        if currentmonth < birthmonth:
            age = (currentyear - birthyear) - 1
        elif currentmonth > birthmonth:
            age = currentyear - birthyear
        elif currentmonth == birthmonth:
            if currentday >= birthday:
                age = currentyear - birthyear
            else:
                age = (currentyear - birthyear) - 1
    return age


def get_reset_token(user_id, id):
    """Get a token to reset password.

    This function will allow the user to obtain a 256-bit key (minimum)/token
    to use in order to reset their password.  The token is "good" for 30
    minutes.

    Arguments:
        user -- user's email
        user_id -- represents the user's admin id

    Returns:
    256-bit key (minimum)/token
    """
    s = Serializer(app.config['SECRET_KEY'], 1800)
    return s.dumps({'user_id': id}).decode('utf-8')


def verify_reset_token(token):
    """Verify token of user requesting password reset.

    This funtion is used to verify the user requesting to reset their passward
    is the same user that requested the provided token.

    Arguments:
        token -- 256-bit key (minimum)/token

    Returns:
        user's email
    """
    s = Serializer(app.config['SECRET_KEY'])
    try:
        # Check if token is valid or expired.
        user_id = s.loads(token)['user_id']
    except:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('reset_request'))

    # If token valid, get a connection to the database
    cur, conn = connect()

    # dict cursors allows access to the retrieved records using an interface
    # similar to the Python dictionaries to perform queries
    dict_cur = cur(cursor_factory=psycopg2.extras.DictCursor)

    # Check to see if email exist for user_id
    dict_cur.execute("SELECT * FROM admins WHERE admin_id = %s",
                     [user_id])
    data = dict_cur.fetchone()
    user = data['email']
    return user
