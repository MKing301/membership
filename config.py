"""This is the configuration file for the application."""

DEBUG = True
SECRET_KEY = 'secret_key_here'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/members'
CSEF_ENABLED = True
