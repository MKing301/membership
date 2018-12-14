"""The module used to set up an initial admin user.

Once the database_setup.py is executed, this will be executed to create
an admin user.  First, insert the first_name, last_name, username, email
and password.  These 5 values must be populated before you execute this
file.
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from passlib.hash import sha256_crypt


first_name = 'Insert First Name Here'
last_name = 'Insert Last Name Here'
username = 'Insert Username Here'
email = 'Insert Email Here'
hashed_password = sha256_crypt.hash(str('Insert Password Here'))

# Get a connection to the database
conn = psycopg2.connect(database=os.environ.get('DB_NAME'),
                        user=os.environ.get('DB_USER'),
                        password=os.environ.get('DB_PASSWORD'),
                        host='localhost')
# conn.cursor will return a cursor object, you can use this cursor to
# perform queries
dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# insert record into the table
dict_cur.execute(
    '''INSERT INTO admins(
        first_name,
        last_name,
        username,
        email,
        password,
        role,
        registered_date)
       VALUES(%s, %s, %s, %s, %s ,%s, %s)
    ''', (first_name,
          last_name,
          username,
          email,
          hashed_password,
          'admin',
          datetime.now())
)

# commit to db
conn.commit()

# close db connection
conn.close()

print("Superuser created!")
