from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


# Callable returns a new base class from which all mapped classes should inherit
Base = declarative_base()


class User(Base):
    '''A registered user of the program. Users will have
       the following attributes:
       Attibute(s):
       id - unique id number for each user
       first_name - user's first name
       last_name - user's last name
       username = user's username
       email - user's email address
       password - user's password
       role = user's role
       registered_date - date user registerd
       approved_date - date admin approved user's access
    '''
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    registered_date = Column(DateTime, nullable=False)
    approved_date = Column(DateTime, nullable=False)


class Member(Base):
    '''A member of the organization. 
       This person will have the following attributes:
       Attibute(s):
       id - unique id number for each user
       first_name - user's first name
       last_name - user's last name
       street_num - member's street number for address
       street_name - member's street address
       city - member's city
       _state - member's state
       postal_code - member's postal code
       contact_num - member's contact number
       email - member's email address
       birthdate - date of birth
       inserted_date - date inserted into the db
    '''
    __tablename__ = 'member'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    street_num = Column(String, nullable=False)
    street_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    _state = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    contact_num = Column(Integer, nullable=False)
    email = Column(String, nullable=False)
    birthdate = Column(DateTime, nullable=False)
    inserted_date = Column(DateTime, nullable=False)


engine = create_engine(os.environ.get('LOCAL_DB_URI_MEMBERSHIP'))
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.create_all(engine)
