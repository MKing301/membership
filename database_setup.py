"""Initial database setup.

This module will establish the new database for the membership app.
"""

import psycopg2
import psycopg2.extras

# Get a connection
conn = psycopg2.connect(database='database_name', user='database_username',
                        password='database_password', host='localhost')
# conn.cursor will return a cursor object, you can use this cursor to
# perform queries
dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

dict_cur.execute(
    '''CREATE TABLE members(
        member_id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        street_num VARCHAR(10),
        street_name VARCHAR(50),
        city VARCHAR(50),
        state VARCHAR(2),
        postal_code VARCHAR(10),
        contact_num VARCHAR(10),
        member_tier INTEGER,
        assigned_elder_first_name VARCHAR(50),
        assigned_elder_last_name VARCHAR(50)
        )'''
)

# commit to db
conn.commit()

# close db connection
conn.close()

print("Database created successfully!")
