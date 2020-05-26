import os
import logging

from datetime import datetime
from project import db
from project.models import User
from project import mail
from flask_mail import Message
from passlib.hash import sha256_crypt
from flask import render_template, flash, redirect, url_for, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from logging.handlers import TimedRotatingFileHandler


# Set Logger
logger = logging.getLogger(__name__)

# Set logging level
logger.setLevel(logging.DEBUG)

# Define logging formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create file handler to rotate based on time
file_handler = TimedRotatingFileHandler(
    '/home/mfsd1809/Dev/FullStackWebDeveloper/GitRepos/membership/project/log_dir/utilslog.log',
    when='m',
    interval=1,
    backupCount=6)

# Here we set our logHandler's formatter
file_handler.setFormatter(formatter)

# Add handler
logger.addHandler(file_handler)


def get_age(birthmonth, birthday, birthyear):
    """Get age.

    This function calculates the age of a member.

    Arguments:
    birthmonth -- member's birth month
    birthday -- member's birth day
    birthyear -- member's birth year

    Returns:
    [type] -- [description]
    """
    currentyear = datetime.now().year
    currentmonth = datetime.now().month
    currentday = datetime.now().day
    try:
        if currentyear < birthyear:
            return -1
        else:
            if currentmonth < birthmonth:
                age = (currentyear - birthyear) - 1
            elif currentmonth > birthmonth:
                age = currentyear - birthyear
            elif currentmonth == birthmonth:
                if currentday >= birthday:
                    age = currentyear - birthyear
                else:
                    age = (currentyear - birthyear) - 1
        return age
    except Exception as e:
        logging.exception(f'Exception: {e}')
