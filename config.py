"""This is the configuration file for the application."""
import os

SECRET_KEY = os.environ.get('SECRET_KEY_LOCAL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.environ.get('LOCAL_DB_URI_MEMBERSHIP')
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
CSRF_ENABLED = True
