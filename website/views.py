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

@views.route('/clientgallery')
@login_required
def clientgallery():
    page = request.args.get('page', 1, type=int)
    per_page = 16  # or any number you like
    pagination = Gallery.query.filter(Gallery.media_type.in_(['image', 'video'])).paginate(page=page, per_page=per_page, error_out=False)

    images = pagination.items
    next_url = url_for('views.clientgallery', page=pagination.next_num) if pagination.has_next else None
    prev_url = url_for('views.clientgallery', page=pagination.prev_num) if pagination.has_prev else None

    return render_template('clientgallery.html', images=images, next_url=next_url, prev_url=prev_url)

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
@login_required  # If only admins can upload, added this.
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
        # upload path inside 'static/uploads/'
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)  # Ensure the folder exists

        file_path = os.path.join(upload_folder, filename)  # Full path of image or video
        file.save(file_path)  # Save file in 'static/uploads/' which is relative path.

        new_media = Gallery(  # Use 'Gallery' for image and video storage.
            user_id=current_user.id,  
            user_type=current_user.type,  
            username=current_user.username,  
            title=title,
            description=description,
            category=category,
            visibility=visibility,
            client_name=client_name,
            media_type=media_type,
            media_path=f'uploads/{filename}'  # Store relative path for images
        )
        db.session.add(new_media)
        db.session.commit()

        flash("File uploaded successfully!", "success")
        return redirect(url_for('views.adminimageupload'))
    
@views.route('/admingallery')
@login_required
def admingallery():
    page = request.args.get('page', 1, type=int)
    per_page = 16  # Show 16 images per page
    pagination = Gallery.query.filter(Gallery.media_type.in_(['image', 'video'])).paginate(page=page, per_page=per_page, error_out=False)

    images = pagination.items
    next_url = url_for('views.admingallery', page=pagination.next_num) if pagination.has_next else None
    prev_url = url_for('views.admingallery', page=pagination.prev_num) if pagination.has_prev else None

     # Convert SQLAlchemy objects to dictionaries
    image_dicts = [{
        'id': img.galleryid,
        'title': img.title,
        'description': img.description,
        'client_name': img.client_name,
        'media_type': img.media_type,
        'media_path': img.media_path,
        'user_id': img.user_id,
        'username': img.username
    } for img in images]

    return render_template('admingallery.html', images=image_dicts, next_url=next_url, prev_url=prev_url)

@views.route('/admin_gallery_modal')
@login_required
def admin_gallery_modal():
    if current_user.type != 'admin':
        flash("Access denied", "error")
        return redirect(url_for('views.home'))

    page = request.args.get('page', 1, type=int)
    per_page = 16
    pagination = Gallery.query.paginate(page=page, per_page=per_page, error_out=False)

    images = pagination.items
    next_url = url_for('views.admin_gallery_modal', page=pagination.next_num) if pagination.has_next else None
    prev_url = url_for('views.admin_gallery_modal', page=pagination.prev_num) if pagination.has_prev else None

    # ✅ Convert objects to dictionaries (this was missing!)
    image_dicts = [{
        'galleryid': img.galleryid,
        'title': img.title,
        'description': img.description,
        'client_name': img.client_name,
        'media_type': img.media_type,
        'media_path': img.media_path,
        'user_id': img.user_id,
        'username': img.username
    } for img in images]

    return render_template('admin_gallery_modal.html', images=image_dicts, next_url=next_url, prev_url=prev_url)

@views.route('/delete/gallery/<int:gallery_id>', methods=['GET'])
def delete_gallery_item(gallery_id):
    gallery_item = Gallery.query.get(gallery_id)
    if gallery_item:
        db.session.delete(gallery_item)
        db.session.commit()
    return redirect(url_for('views.admin_gallery_modal'))
