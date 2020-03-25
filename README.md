# Membership App

The _**Membership App**_ (`membersapp.py`) allows an Administrator to register 
and log into the application after their role is updated by the application's Superuser.  The application provides an admin user the ability to reset thier password.

Administrators will be able to Create, Read, Update and Delete members in the
database.

--TODO--

## Requirements

* Ubuntu 16.04
* You successfully installed *Python 3.5*  on your computer.
* [Virtual Environment for Python3](https://docs.python.org/3/library/venv.html)
* You successfully installed *PostgreSQL* on your computer. (sudo apt-get install postgresql postgresql-contrib)

## Installation
For the installtion, you will need to set your system variables, download the application, and install the required packages.

### Set System Wide Variables
In your terminal, at the home directory, edit the .bashrc file (nano .bashrc) by typing the following at the top of the file (without the numbers):
1. export DB_NAME="enter your database name here"
2. export DB_USER="enter your database name here"
3. export MAIL_PASSWORD="enter your database name here"
4. export MAIL_USERNAME="enter your database name here"
5. export LOCAL_DB_URI_MEMBERSHIP="postgresql://db_user_name_here:db_password_here@localhost/table_name_here"
6. export SECRET_KEY_LOCAL="enter your secret key here"
7. Type `CTRL + o`, then type `CTRL + x` to save your changes.
8. Type `source .bashrc` to set new changes

### Clone Repository (Load App on Local Machine)
1. Install git (sudo apt-get install git-core)
2. Configure git user name (git config --global user.name "your user name")
3. Configure git email (git config --global user.email "your email")
4. Create directory, cd into the directory, then get a copy of app (git clone https://github.com/MKing301/membership.git membership)
5. First, install pip (sudo apt-get install python3-pip)
6. Second, install virtual environment (sudo pip3 install virtualenv)
7. Now, create a virtual environment (virtualenv -p /usr/bin/python3.5 venv)

### Install dependencies

* From the project directory, activate the virtual environment (source venv/bin/activate)
* Install required packages (pip install -r requirements.txt) 

## Run the program

Once you have downloaded the application and have installed the listed 
requirements, you can run the project by typing `python3 membersapp.py`.  Once the application is running, open a browswer and enter `localhost:5000` then click `ENTER`.  The application is running.

NOTE:  To stop the application, in the terminal type `CTRL + C`, then type `deactivate` to stop the virtual environment.

--TODO--

* Type `python database_setup.py` to run the application.
* Type `python database_setup2.py` to run the application.
* Type `python database_superuser_setup.py` to run the application.
* Type `python membersapp.py` to run the application.