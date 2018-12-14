"""This is the configuration file for the application."""
import os

DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY_LOCAL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.environ.get('LOCAL_DB_URI_MEMBERSHIP')
CSEF_ENABLED = True
