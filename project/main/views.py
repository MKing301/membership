import os
import logging

from datetime import datetime
from sqlalchemy import desc, update
from project import db
from project.users.forms import SearchForm, MemberForm
from project.users.utils import get_age
from project.models import User, Member
from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, redirect, url_for ,flash, request, Blueprint
from logging.handlers import TimedRotatingFileHandler


main = Blueprint('main', __name__)


# Set Logger
logger = logging.getLogger(__name__)

# Set logging level
logger.setLevel(logging.DEBUG)

# Define logging formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create file handler to rotate based on time
file_handler = TimedRotatingFileHandler(
    '/home/mfsd1809/Dev/FullStackWebDeveloper/GitRepos/membership/project/log_dir/mainlog.log',
    when='m',
    interval=1,
    backupCount=6)

# Here we set our logHandler's formatter
file_handler.setFormatter(formatter)

# Add handler
logger.addHandler(file_handler)


# Home Page
@main.route('/')
def index():
    """The route for the home screen.

    Decorators:
        app.route

    Returns:
    Renders template for home page
    """
    return render_template('index.html', Title="Home")


# Dashboard
@main.route('/dashboard')
@login_required
def dashboard():
    """The route for application dashboard.

    This functions displays the user's dashboard.

    Decorators:
        app.route
        is_logged_in

    Returns:
        Renders dashboard html page
    """
    members = db.session.query(Member).order_by(Member.last_name).all()

    if members:
        return render_template('dashboard.html',
                               Title="Dashboard",
                               members=members)

    else:
        msg = 'No Members Found'
        return render_template('dashboard.html',
                               Title="Dashboard",
                               msg=msg)


# Admin
@main.route('/admin')
@login_required
def admin():
    """The route for admin page.

    This functions displays the admin page.

    Decorators:
        app.route
        is_logged_in

    Returns:
        Renders admin html page
    """
    # Get Admin users
    users = db.session.query(User).order_by(User.last_name).all()

    if users:
        return render_template('admin.html',
                               Title="Admins",
                               users=users)

    else:
        msg = 'No Admins Found'
        return render_template('admin.html',
                               Title="Admin",
                               msg=msg)


# Update role
@main.route('/update_role/<string:id>/role/<string:role>',
           methods=['GET', 'POST'])
@login_required
def update_role(id, role):
    """The route for updating admin role.

    This functions allows admin user to toggle admin role between 'admin'
    and 'pending'. 'admin' role can log into application, but 'pending' role
    cannot log into the application.

    Decorators:
        is_logged_in

    Arguments:
        id  -- admin user id
        role  -- role assigned ot admin user

    Returns:
        Renders admin html page
    """
    if request.method == 'POST':
        if role == 'locked':
            role = 'admin'
        else:
            role = 'locked'

        user = db.session.query(User).filter(User.id==id).first()
        user.role = role
        user.approved_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()

        flash('Role Updated!', 'success')
        logger.info(f'{current_user.username} updated {user.first_name} {user.last_name} - Admin ID: {user.id} role.')

        return redirect(url_for('main.admin'))

    return render_template('admin.html',
                           Title="Admin", id=id)


# Search for Member(s)
@main.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """The route for the search screen.

    This function allows admin to search database for a user.

    Decorators:
        app.route
        is_logged_in

    Returns:
        Renders template for search page upon get request
        Renders template for dashboard upon successful post request
    """
    form = SearchForm()
    if form.validate_on_submit():
        search_first_name = request.form['search_first_name'].title()
        search_last_name = request.form['search_last_name'].title()
        search_fn = "%{}%".format(search_first_name)
        search_ln = "%{}%".format(search_last_name)

        members = db.session.query(Member).filter(Member.first_name.like(search_fn), Member.last_name.like(search_ln)).order_by(Member.last_name).all()
        if members:
            return render_template('dashboard.html',
                                   Title="Dashboard",
                                   members=members)

        else:
            flash('No members found, please try again.', 'info')
            return redirect(url_for('main.search'))

    return render_template('search.html', Title="Search", form=form)


# Add Member
@main.route('/add_member', methods=['GET', 'POST'])
@login_required
def add_member():
    """The route for the add member screen.

    This function allows admin to add a user to the database..

    Decorators:
        app.route
        is_logged_in

    Returns:
        Renders template for add member page upon get request
        Renders template for dashboard upon successful post request
    """
    form = MemberForm()
    if form.validate_on_submit():
        new_member = Member(
            first_name = request.form['first_name'].title(),
            last_name = request.form['last_name'].title(),
            street_num = request.form['street_num'],
            street_name = request.form['street_name'].title(),
            city = request.form['city'].title(),
            _state = request.form['state'].upper(),
            postal_code = request.form['postal_code'],
            contact_num = request.form['contact_num'],
            email = request.form['email'].lower(),
            birthdate = request.form['birthdate'],
            inserted_date =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        first_name_test = request.form['first_name'].title()
        last_name_test = request.form['last_name'].title()

        member = db.session.query(Member).filter(Member.first_name==first_name_test, Member.last_name==last_name_test).first()
        if member:
            flash('Member already exist with that first and last name.', 'warning')
            return redirect(url_for('main.dashboard'))
        else:
            db.session.add(new_member)
            db.session.commit()

            flash(f'{new_member.first_name} {new_member.last_name} ID{new_member.id} added!', 'success')
            logger.info(f'{current_user.username} added {new_member.first_name} {new_member.last_name} - Member ID: {new_member.id}.')
            return redirect(url_for('main.dashboard'))
    else:
        return render_template('add_member.html', Title="Add Member", form=form)


# Edit Member
@main.route('/edit_member/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_member(id):
    """The edit member route.

    This function allows admin to edit a member data in the database.

    Decorators:
        app.route
        is_logged_in

    Arguments:
        member_id  -- member's id

    Returns:
        Renders template for edit member page upon get request
        Renders template for dashboard upon successful post request
    """
    # member = User.query.filter_by(id=id).first()
    member = db.session.query(Member).filter(Member.id==id).first()

    # Get form
    form = MemberForm()
    if not form.validate_on_submit():
        # Populate member fields
        form.first_name.data = member.first_name
        form.last_name.data = member.last_name
        form.street_num.data = member.street_num
        form.street_name.data = member.street_name
        form.city.data = member.city
        form.state.data = member._state
        form.postal_code.data = member.postal_code
        form.contact_num.data = member.contact_num
        form.email.data = member.email
        form.birthdate.data = member.birthdate

        return render_template('edit_member.html',
                               Title="Edit Member", id=id, form=form)

    else:
        member.first_name = request.form['first_name'].title()
        member.last_name = request.form['last_name'].title()
        member.street_num = request.form['street_num']
        member.street_name = request.form['street_name'].title()
        member.city = request.form['city'].title()
        member.state = request.form['state'].upper()
        member.postal_code = request.form['postal_code']
        member.contact_num = request.form['contact_num']
        member.email = request.form['email'].lower()
        member.birthdate = request.form['birthdate']

        db.session.commit()

        flash('Member Updated!', 'success')
        logger.info(f'{current_user.username} updated {member.first_name} {member.last_name} - Member ID: {member.id}.')
        return redirect(url_for('main.dashboard'))


# Delete Member
@main.route('/delete_member/<string:id>', methods=['GET', 'POST'])
@login_required
def delete_member(id):
    """The first step to delete member route.

    This function allows admin to stage the deletion a member from the
    database.

    Decorators:
        app.route
        is_logged_in

    Arguments:
        id  -- member's id

    Returns:
        Renders template for delete member page upon get request
        Renders template for deleting a member upon successful post request
    """
    member_to_delete = db.session.query(Member).filter(Member.id==id).first()

    return render_template(
        'delete_member_confirmation.html', member_to_delete=member_to_delete)


@main.route('/final_delete/<string:id>', methods=['POST'])
@login_required
def final_delete(id):
    """The delete member route.

    This function allows admin to delete a member from the database.

    Decorators:
        app.route
        is_logged_in

    Arguments:
        id  -- member's id

    Returns:
        Renders dashboard page
    """
    member = db.session.query(Member).filter_by(id=id).first()
    deleted_member = f'{member.first_name} {member.last_name} - Member ID: {member.id}'
    db.session.delete(member)
    db.session.commit()

    flash(f'Member deleted!', 'success')
    logger.info(f'{current_user.username} deleted {deleted_member}.')

    return redirect(url_for('main.dashboard'))


# Ages
@main.route('/ages')
@login_required
def ages():
    """The member age route.

    This function displays the members age in html page in order of member's
    first name.

    Decorators:
        app.route
        is_logged_in

    Returns:
        Renders age html page
    """
    members_ages = db.session.query(Member.first_name, Member.last_name, Member.birthdate).all()

    if members_ages:
        birthdate_dict = []
        for member_age in members_ages:
            bday = member_age.birthdate
            birthdate_dict.append({'first name': member_age.first_name,
                                   'last name': member_age.last_name,
                                   'age': (get_age(
                                        int(bday.month),
                                        int(bday.day),
                                        int(bday.year)))})
        birthdate_dict = sorted(birthdate_dict, key=lambda i: i['age'], reverse=True)
        return render_template('ages.html',
                               Title="Member's Age",
                               birthdate_dict=birthdate_dict)

    else:
        msg = 'No members; therefore, no ages displayed.'
        return render_template('ages.html', Title="Member's Age", msg=msg)
