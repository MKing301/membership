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


def get_age(birthmonth, birthday, birthyear):
    """[summary].

    [description]

    Arguments:
    birthmonth {[type]} -- [description]
    birthday {[type]} -- [description]
    birthyear {[type]} -- [description]

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
    """[summary].

    [description]

    Arguments:
        user {[type]} -- [description]
        user_id {[type]} -- [description]
    """
    s = Serializer(app.config['SECRET_KEY'], 1800)
    return s.dumps({'user_id': id}).decode('utf-8')


def verify_reset_token(token):
    """[summary].

    [description]

    Arguments:
        token {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    s = Serializer(app.config['SECRET_KEY'])
    try:
        user_id = s.loads(token)['user_id']
    except:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('reset_request'))
    # Get a connection
    conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                            user=os.environ.get('DB_USER'),
                            password=os.environ.get('DB_PASSWORD'),
                            host='localhost')
    # conn.cursor will return a cursor object, you can use this cursor
    # to perform queries
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check to see if email exist
    dict_cur.execute("SELECT * FROM admins WHERE admin_id = %s",
                     [user_id])
    data = dict_cur.fetchone()
    user = data['email']
    return user
