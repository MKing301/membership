"""[summary.

[description]
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, IntegerField
from wtforms import validators


# Register Class
class RegisterForm(FlaskForm):
    """[summary.

    [description]

    Extends:
        FlaskForm

    Variables:
        first_name {[type]} -- [description]
        last_name {[type]} -- [description]
        username {[type]} -- [description]
        email {[type]} -- [description]
        password {[type]} -- [description]
        confirm {[type]} -- [description]
    """

    first_name = StringField('First Name', [validators.Length(min=2, max=50)])
    last_name = StringField('Last Name', [validators.Length(min=2, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Email(message="Invalid email!")])
    password = PasswordField('Password', [
        validators.equal_to('confirm', message='Passwords do not match.')])
    confirm = PasswordField('Confirm Password')


# Login Class
class LoginForm(FlaskForm):
    """[summary.

    [description]

    Extends:
        FlaskForm

    Variables:
        username {[type]} -- [description]
        password {[type]} -- [description]
    """

    email = StringField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


# Member Form Class
class MemberForm(FlaskForm):
    """[summary.

    [description]

    Extends:
        FlaskForm

    Variables:
        first_name {[type]} -- [description]
        last_name {[type]} -- [description]
        street_num {[type]} -- [description]
        street_name {[type]} -- [description]
        city {[type]} -- [description]
        state {[type]} -- [description]
        postal_code {[type]} -- [description]
        contact_num {[type]} -- [description]
        birthdate {[type]} -- [description]
        member_tier {[type]} -- [description]
        assigned_elder_first_name {[type]} -- [description]
        assigned_elder_last_name {[type]} -- [description]
    """

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


# Search Form
class SearchForm(FlaskForm):
    """[summary.

    [description]

    Extends:
        FlaskForm

    Variables:
        search_first_name {[type]} -- [description]
        search_last_name {[type]} -- [description]
    """

    search_first_name = StringField(
        'Search First Name', [validators.DataRequired()])
    search_last_name = StringField(
        'Search Last Name', [validators.DataRequired()])
