"""Initial database setup.

This module will establish the new table in the database for the membership
app for admins.
"""

import psycopg2
import psycopg2.extras

# Get a connection
conn = psycopg2.connect(database='database_name',
                        user='database_user',
                        password='database_password',
                        host='localhost')
# conn.cursor will return a cursor object, you can use this cursor to
# perform queries
dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

dict_cur.execute(
    '''CREATE TABLE admins(
        admin_id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(255)
        )'''
)

# commit to db
conn.commit()

# close db connection
conn.close()

print("Admins table created successfully!")
