"""The module module.

This module contains the user and member class of the application.
"""

from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from project import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), unique=False, nullable=False)
    last_name = db.Column(db.String(50), unique=False, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(7), unique=False, nullable=False)
    registered_date = db.Column(db.DateTime(), unique=False, nullable=False)
    approved_date = db.Column(db.DateTime(), unique=False, nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')


    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    def __repr__(self):
        return f"User('{self.first_name}, {self.last_name}, {self.username}, {self.email})"


class Member(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), unique=False, nullable=False)
    last_name = db.Column(db.String(50), unique=False, nullable=False)
    street_num = db.Column(db.String(10), unique=False, nullable=False)
    street_name = db.Column(db.String(50), unique=False, nullable=False)
    city = db.Column(db.String(50), unique=False, nullable=False)
    _state = db.Column(db.String(2), unique=False, nullable=False)
    postal_code = db.Column(db.String(10), unique=False, nullable=False)
    contact_num = db.Column(db.Integer, unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    birthdate = db.Column(db.DateTime(), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    inserted_date = db.Column(db.DateTime(), nullable=False)
