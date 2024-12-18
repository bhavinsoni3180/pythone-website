from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from sqlalchemy import inspect
from .models import User, Image, ContactMe, BookingShoot

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("index.html")

@views.route('/serviceaout')
@login_required
def serviceabout():
    return render_template('serviceaout.html')

@views.route('/workcontact')
@login_required
def workcontact():
    return render_template('workcontact.html')

@views.route('/booking')
@login_required
def booking():
    return render_template('booking.html')

@views.route('/adminindex')
@login_required
def adminindex():
    # Check if the logged-in user is an admin by checking the 'type' column
    if current_user.type == "admin":  # Check the 'type' of the logged-in user
        return render_template('adminindex.html')  # Show the admin dashboard
    else:
        flash("You do not have permission to access this page.", category='error')
        return redirect(url_for('views.home'))  # Redirect non-admin users to home or another appropriate page
    
def adminindex():
    return render_template('adminindex.html')

@views.route('/adminviewdata')

def adminviewdata():
    return render_template('adminviewdata.html')

@views.route('/adminviewdata', methods=['GET', 'POST'])

def show_table_data():
    # List all the table names dynamically
    tables = ['User', 'Image', 'ContactMe', 'BookingShoot']  # List of tables you want to support
    table_data = None
    columns = None
    selected_table = None
    model = None  # Initialize model variable
    unhashed_passwords = {}  # Initialize the unhashed_passwords dictionary

    if request.method == 'POST':
        selected_table = request.form.get('table_name')

        # Dynamically select table class
        if selected_table == 'User':
            model = User
        elif selected_table == 'Image':
            model = Image
        elif selected_table == 'ContactMe':
            model = ContactMe
        elif selected_table == 'BookingShoot':
            model = BookingShoot

        if model:
            # Get the column names for the selected table
            columns = [column.name for column in inspect(model).c]

            # Fetch data from the selected table
            table_data = db.session.query(model).all()

            # If the table is 'User', we will display the unhashed passwords for testing purposes
            if selected_table == 'User':
                for user in table_data:
                    # Assuming that the password is stored in 'password' column and is hashed
                    unhashed_passwords[user.id] = user.password  # Store the unhashed password temporarily

    return render_template('adminviewdata.html', tables=tables, table_data=table_data, columns=columns, selected_table=selected_table, getattr=getattr)

@views.route('/update_data/<table>/<int:row_id>', methods=['POST'])
def update_data(table, row_id):
    # Dynamically select the model based on the table name
    model = None
    if table == 'User':
        model = User
    elif table == 'Image':
        model = Image
    elif table == 'ContactMe':
        model = ContactMe
    elif table == 'BookingShoot':
        model = BookingShoot
    
    if model:
        # Fetch the row by ID
        row = model.query.get(row_id)
        
        if row:
            # Update the row with the new data from the form
            for column in model.__table__.columns:
                if column.name != 'id':  # Skip the ID column
                    new_value = request.form.get(column.name)
                    setattr(row, column.name, new_value)
            
            # Commit the changes to the database
            db.session.commit()

        # Redirect back to the admin view data page to show updated data
        return redirect(url_for('views.adminviewdata'))

    return "Table not found", 404
@views.route('/delete/<table>/<int:row_id>', methods=['GET'])

def delete_data(table, row_id):
    # Dynamically select the model based on the table name
    model = None
    if table == 'User':
        model = User
    elif table == 'Image':
        model = Image
    elif table == 'ContactMe':
        model = ContactMe
    elif table == 'BookingShoot':
        model = BookingShoot
    
    if model:
        # Fetch the row by ID and delete it
        row = model.query.get(row_id)
        if row:
            db.session.delete(row)
            db.session.commit()
        return redirect(url_for('views.adminviewdata'))
    return "Table not found", 404