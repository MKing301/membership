"""summary.

[description]
"""

from membersapp import app
from flask import render_template, flash, redirect, url_for, request


# Home Page
@app.route('/')
def index():
    """This is the route for the home screen.

    Returns:
    Render template for home page with title of page
    """
    return render_template('index.html', Title="Home")
