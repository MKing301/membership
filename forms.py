"""The forms module.

This module contains all of the forms used by the application.
"""

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, DateField, IntegerField
from wtforms import validators


# Register Class
class RegisterForm(FlaskForm):
    """The Registration Form.

    This form contains field to collect admin users that will register to
    access the application.

    Extends:
        FlaskForm

    Variables:
        first_name -- admin's first name
        last_name -- admin's last name
        username -- admin's username
        email -- admin's email
        password -- password
        confirm -- password
    """

    first_name = StringField('First Name', [validators.Length(min=2, max=50)])
    last_name = StringField('Last Name', [validators.Length(min=2, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Email(message="Invalid email!")])
    password = PasswordField('Password', [
        validators.equal_to('confirm', message='Passwords do not match.')])
    confirm = PasswordField('Confirm Password')
    recaptcha = RecaptchaField()

# Login Class
class LoginForm(FlaskForm):
    """The Login Form.

    This is the form that contains the field to capture login details.

    Extends:
        FlaskForm

    Variables:
        email -- admin's email
        password -- admin's password
    """

    email = StringField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    recaptcha = RecaptchaField()

# Member Form Class
class MemberForm(FlaskForm):
    """The Member Form.

    This is the form the contain the field for the member's details.

    Extends:
        FlaskForm

    Variables:
        first_name -- member's first name
        last_name -- member's last name
        street_num -- member's street_num
        street_name -- member's street_name
        city -- member's city
        state -- member's state
        postal_code -- member's postal_code
        contact_num -- member's contact_num
        email -- member's email
        birthdate -- member's birthdate
    """

    first_name = StringField('First Name', [validators.DataRequired()])
    last_name = StringField('Last Name', [validators.DataRequired()])
    street_num = StringField('Street Number', [validators.DataRequired()])
    street_name = StringField('Street Name', [validators.DataRequired()])
    city = StringField('City', [validators.DataRequired()])
    state = StringField('State', [validators.DataRequired(), validators.Length(min=2, max=2)])
    postal_code = StringField('Postal Code', [validators.DataRequired()])
    def validate_postal_code(form, field):
        if len(field.data) != 5:
            raise ValueError("Field must be exactly 5 characters")
        if not field.data.isnumeric():
            raise ValueError("Field must be numbers only")
    contact_num = StringField('Contact Number', [validators.DataRequired()])
    def validate_contact_num(form, field):
        if len(field.data) != 10:
            raise ValueError("Field must be exactly 10 characters")
        if not field.data.isnumeric():
            raise ValueError("Field must be numbers only")
    email = StringField('Email', [validators.Email(message="Invalid email!")])
    birthdate = DateField('Birthdate', format='%Y-%m-%d')


# Search Form
class SearchForm(FlaskForm):
    """The Search Form.

    The form contins the field an admin can search for members in the
    database.

    Extends:
        FlaskForm

    Variables:
        search_first_name -- search by member's first name
        search_last_name -- search by member's last name
    """

    search_first_name = StringField('Search First Name')
    search_last_name = StringField('Search Last Name')


# Form to Request Reset of Password
class ResetRequestForm(FlaskForm):
    """The Reset Request Form.

    This form is used when an admin wants to make a request to reset their
    password.

    Extends:
        FlaskForm

    Variables:
        email -- admin's email address
    """

    email = StringField('Email', [validators.DataRequired()])
    recaptcha = RecaptchaField()

# Form to Request Password Reset
class ResetPasswordForm(FlaskForm):
    """The Reset Password Form.

    The form used for admin to reset their password.

    Extends:
        FlaskForm

    Variables:
        password -- new password
        confirm -- new password
    """

    password = PasswordField('Password', [validators.DataRequired(),
                             validators.equal_to('confirm',
                             message='Passwords do not match.')])
    confirm = PasswordField('Confirm Password')
    recaptcha = RecaptchaField()
