"""This is the main application file."""

import os
from flask import Flask
from flask_mail import Mail

# Create app
app = Flask(__name__)
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": os.environ.get('MAIL_USERNAME'),
    "MAIL_PASSWORD": os.environ.get('MAIL_PASSWORD')
}

app.config.update(mail_settings)
mail = Mail(app)
# Load configuration
app.config.from_pyfile('config.py')

from views import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
