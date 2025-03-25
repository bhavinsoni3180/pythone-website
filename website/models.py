from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(15), nullable=False, default='client')

class Image(db.Model):
    __tablename__ = 'images'
    imgid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    imgpath = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref=db.backref('images', lazy=True))

class ContactMe(db.Model):
    __tablename__ = 'contactme'
    cid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    contactnumbre = db.Column(db.BigInteger, nullable=False)
    details = db.Column(db.String(10000), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('contactmes', lazy=True))

class BookingShoot(db.Model):
    __tablename__ = 'bookingshoot'
    bookingid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    partnername = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    occasiontype = db.Column(db.String(50), nullable=True)
    datetime = db.Column(db.DateTime, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    hoursofshoot = db.Column(db.Integer, nullable=True)
    contactnumber = db.Column(db.BigInteger, nullable=True)

    user = db.relationship('User', backref=db.backref('bookingshoots', lazy=True))

class Gallery(db.Model):
    __tablename__ = 'gallery'
    galleryid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_type = db.Column(db.String(15), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    visibility = db.Column(db.Enum('public', 'private', 'clients'), nullable=False, default='public')
    views = db.Column(db.Integer, nullable=False, default=0)
    client_name = db.Column(db.String(100), nullable=True)
    media_type = db.Column(db.String(10), nullable=False)  # 'image' or 'video'
    media_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    
    user = db.relationship('User', backref=db.backref('gallery', lazy=True))