"""Initial database setup.
This module will establish the new table in the database for the membership
app for members.
"""

import os
import psycopg2
import psycopg2.extras

# Get a connection
conn = psycopg2.connect(host='localhost',
                        database=os.environ.get('DB_NAME'),
                        user=os.environ.get('DB_USER'),
                        password=os.environ.get('DB_PASSWORD'))

# conn.cursor will return a cursor object, you can use this cursor to
# perform queries
dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

dict_cur.execute(
    '''INSERT INTO members(
        first_name,
        last_name,
        street_num,
        street_name,
        city,
        state,
        postal_code,
        contact_num,
        birthdate,
        member_tier,
        assigned_elder_first_name,
        assigned_elder_last_name)
      VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s, %s)
    ''', ('JoAnn',
          'Walker',
          '777',
          'Main St',
          'Raleigh',
          'NC',
          '27610',
          '9197779311',
          '1981-08-28',
          '1',
          'Bobby',
          'Waters')
)

# commit to db
conn.commit()

# close db connection
conn.close()

print("Test Member created!")
