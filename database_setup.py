"""Database setup.
This module will establish the new tables in the database for the
membership app.
"""

import os
import psycopg2
import psycopg2.extras
from helpers import connect
from datetime import datetime
from passlib.hash import sha256_crypt


first_name = os.environ.get('FIRST_NAME')
last_name = os.environ.get('LAST_NAME')
username = os.environ.get('USERNAME')
email = os.environ.get('EMAIL')
hashed_password = sha256_crypt.hash(str(os.environ.get('PASSWORD')))

create_queries = [
    '''CREATE TABLE members(
        member_id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        street_num VARCHAR(10),
        street_name VARCHAR(50),
        city VARCHAR(50),
        _state VARCHAR(2),
        postal_code VARCHAR(10),
        contact_num VARCHAR(10),
        email VARCHAR (50),
        birthdate DATE
        )''',
    '''CREATE TABLE admins(
        admin_id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(50) NOT NULL,
        password TEXT,
        role VARCHAR(7) NOT NULL,
        registered_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )'''
]

for query in create_queries:
    # Get a connection
    conn, cur = connect()

    # Execute query
    cur.execute(query)

    # Commit to db
    conn.commit()

    # Close cursor
    cur.close()

    # Close db connection
    conn.close()

# Insert initial admin
# Get a connection
conn, cur = connect()

# Execute query
cur.execute('''INSERT INTO admins(
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
      datetime.now()))


# Insert initial member

# Execute query
cur.execute('''INSERT INTO members(
        first_name,
        last_name,
        street_num,
        street_name,
        city,
        _state,
        postal_code,
        contact_num,
        email,
        birthdate)
      VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', ('JoAnn',
          'Walker',
          '777',
          'Main St',
          'Raleigh',
          'NC',
          '27610',
          '9197779311',
          'jwalk@gmail.com',
          '1981-08-28'))

# Commit to db
conn.commit()

# Close cursor
cur.close()

# Close db connection
conn.close()

print("Database setup complete!")
