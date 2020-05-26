import os
import csv

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from database import Base, User, Member
from datetime import datetime


engine = create_engine(os.environ.get('LOCAL_DB_URI_MEMBERSHIP'))
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.create_all(engine)

# Read member's data from csv file
with open('/home/mfsd1809/Dev/FullStackWebDeveloper/GitRepos/membership/directory.csv', encoding="utf8") as fin:
    # Read csv file as a dictionary
    csv_reader = csv.DictReader(fin)

    # Iterate through rows of csv file and insert each member into db
    for row in csv_reader:
        member = Member(
            first_name = row['first_name'],
            last_name = row['last_name'],
            street_num = row['street_num'],
            street_name = row['street_name'],
            city = row['city'],
            _state = row['_state'],
            postal_code = row['postal_code'],
            contact_num = row['contact_num'],
            email = row['email'],
            birthdate = row['birthdate'],
            inserted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.session.add(member)
        db.session.commit()

print('Initial member data inserted into database!')

# Create initial user
user = User(
            first_name = row['first_name'],
            last_name = row['last_name'],
            username = row['username'],
            email = row['email'],
            password = row['password'],
            role = 'admin',
            registered_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            approved_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.session.add(user)
        db.session.commit()

print("Initial user's data inserted into database!")
