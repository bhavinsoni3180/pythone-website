from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from sqlalchemy import inspect
from .models import User, Image, ContactMe, BookingShoot, Gallery
import os
from werkzeug.utils import secure_filename


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
    tables = ['User', 'Gallery', 'ContactMe', 'BookingShoot']  # List of tables you want to support
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
        elif selected_table == 'Gallery':
            model = Gallery
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
    elif table == 'Gallery':
        model = Gallery
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
    elif table == 'Gallery':
        model = Gallery
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

@views.route('/adminimageupload')

def adminimageupload():
    return render_template('adminimageupload.html')


@views.route('/upload_media', methods=['POST'])
@login_required  # If only admins can upload, add this decorator
def upload_media():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        visibility = request.form.get('visibility')
        client_name = request.form.get('client_name')
        media_type = request.form.get('media_type')
        file = request.files.get('file')

        if not file:
            flash("No file selected", "error")
            return redirect(url_for('views.adminimageupload'))

        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mkv'}
        if '.' not in file.filename or file.filename.split('.')[-1].lower() not in allowed_extensions:
            flash("Invalid file type", "error")
            return redirect(url_for('views.adminimageupload'))

        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)  # FIXED
        file.save(file_path)  # FIXED

        new_media = Gallery(  # ✅ Use 'Gallery' instead of 'Image'
            user_id=current_user.id,  
            user_type=current_user.type,  
            username=current_user.username,  
            title=title,
            description=description,
            category=category,
            visibility=visibility,
            client_name=client_name,
            media_type=media_type,
            media_path=file_path  # ✅ 'file_path' should match 'media_path'
        )
        db.session.add(new_media)
        db.session.commit()

        flash("File uploaded successfully!", "success")
        return redirect(url_for('views.adminimageupload'))