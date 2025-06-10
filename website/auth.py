import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from .models import ContactMe, User, BookingShoot
from . import db
from flask_login import logout_user
from datetime import datetime

auth = Blueprint('auth', __name__)
login_manager = LoginManager()

@login_manager.user_loader

#fix login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('emails')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)  # Log the user in
            if user.type == "admin":
                return redirect(url_for('views.adminindex'))  # Redirect to admin page if admin
            else:
                return redirect(url_for('views.home'))  # Redirect to serviceabout page
        else:
            flash('Invalid email or password', category='error')

    return render_template("login.html")
# fix logout
@auth.route('/logout')
def logout():
    logout_user()  # This logs the user out
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def signup():

    email = request.form.get('email', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    password2 = request.form.get('password2', '')

    if len(email) < 4:
        flash('Email is short', category='error')
    elif len(username) < 4:
        flash('username is short', category='error')
    elif password != password2:
        flash('Both password don\'t match', category='error')
    elif len(password) < 4:
        flash('password is short', category='error')
    else:
        #add data in datBase
        hashed_password = generate_password_hash(password)
         # Create new user and add to database
        new_user = User(email=email, username=username, password=hashed_password)
        
        try:
                db.session.add(new_user)
                db.session.commit()
                flash('Account created successfully', category='success')
                return redirect(url_for('auth.login'))  # Redirect to login page
        except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', category='error')
        flash('account created', category='success')
    return render_template("register.html")

@auth.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        # Retrieve data from the form
        name = request.form.get('name')
        partnername = request.form.get('partnername')
        email = request.form.get('email')
        occasiontype = request.form.get('occasiontype')
        datetime_str = request.form.get('datetime')  # Assuming it's in 'yyyy-mm-ddThh:mm' format
        address = request.form.get('address')
        latitude = request.form.get('latitude')  # From hidden field
        longitude = request.form.get('longitude')  # From hidden field
        hoursofshoot = request.form.get('hoursofshoot')
        contactnumber = request.form.get('contactnumber')

        # Make sure the hidden fields are present and correctly populated
        if not latitude or not longitude:
            flash('Location details are required.', category='error')
            return redirect(url_for('auth.booking'))  # Redirect to the booking page again

        # Convert datetime string to datetime object (optional, depending on your database)
        from datetime import datetime
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M")

        # Create a new booking object with the current user's ID
        new_booking = BookingShoot(
            id=current_user.id,  # Use current user's ID from the session
            name=name,
            partnername=partnername,
            email=email,
            occasiontype=occasiontype,
            datetime=datetime_obj,
            address=address,
            latitude=latitude,
            longitude=longitude,
            hoursofshoot=hoursofshoot,
            contactnumber=contactnumber
        )

        # Add to the database
        try:
            db.session.add(new_booking)
            db.session.commit()
            flash('Your booking has been successfully made!', category='success')
            return redirect(url_for('auth.booking'))  # Redirect to booking confirmation page or back to the form
        except Exception as e:
            db.session.rollback()  # If something goes wrong, rollback
            flash(f'Error: {str(e)}', category='error')

    return render_template('booking.html')

@auth.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Retrieve the data from the form
        contact_email = request.form.get('contactmeemail')
        contact_number = request.form.get('contactmenumber')
        contact_details = request.form.get('contactmearea')
        
        # Error checking: ensure all fields are filled
        if not contact_email or not contact_number or not contact_details:
            flash('All fields are required!', category='error')
            return redirect(url_for('auth.contact'))  # Redirect back to the contact page

        # Get the current user's ID from the session (logged-in user)
        user_id = current_user.id

        # Get the current date and time for the database
        current_date = datetime.now()
        current_time = datetime.now()

        # Create a new ContactMe object and add it to the database
        new_contact = ContactMe(
            id=user_id,  # The current logged-in user's ID
            email=contact_email,
            contactnumbre=contact_number,
            details=contact_details,
            date=current_date,  # Store the current date
            time=current_time   # Store the current time
        )

        try:
            db.session.add(new_contact)
            db.session.commit()
            flash('Your message has been sent successfully!', category='success')
            return redirect(url_for('auth.contact'))  # Redirect back to the contact page
        except Exception as e:
            db.session.rollback()  # If something goes wrong, rollback
            flash(f'Error: {str(e)}', category='error')

    return render_template('workcontact.html')  # Render the contact form page