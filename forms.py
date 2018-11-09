"""[summary.

[description]
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators


# Register Class
class RegisterForm(FlaskForm):
    first_name = StringField('First Name', [validators.Length(min=2, max=50)])
    last_name = StringField('Last Name', [validators.Length(min=2, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Email(message="Invalid email!")])
    password = PasswordField('Password', [
        validators.equal_to('confirm', message='Passwords do not match.')])
    confirm = PasswordField('Confirm Password')


# Login Class
class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
