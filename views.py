"""summary.

[description]
"""

from membersapp import app
from forms import RegisterForm
from flask import render_template, flash, redirect, url_for, request


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
    return render_template('register.html', Title="Register", form=form)

