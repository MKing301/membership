"""[summary.

[description]
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, IntegerField
from wtforms import validators


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


# Member Form Class
class MemberForm(FlaskForm):
    first_name = StringField('First Name', [validators.DataRequired()])
    last_name = StringField('Last Name', [validators.DataRequired()])
    street_num = StringField('Street Number', [validators.DataRequired()])
    street_name = StringField('Street Name', [validators.DataRequired()])
    city = StringField('City', [validators.DataRequired()])
    state = StringField('State', [validators.DataRequired()])
    postal_code = StringField('Postal Code', [validators.DataRequired()])
    contact_num = StringField('Contact Number', [validators.DataRequired()])
    birthdate = DateField('Birthdate', format='%Y-%m-%d')
    member_tier = IntegerField('Member Tier', [validators.DataRequired()])
    assigned_elder_first_name = StringField(
        'Assigned Elder First Name', [validators.DataRequired()])
    assigned_elder_last_name = StringField(
        'Assigned Elder Last Name', [validators.DataRequired()])
