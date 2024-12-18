from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from os import path


db = SQLAlchemy()
DB_NAME = "photodb.db"
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'bhavin soni'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=1)  # Set session timeout to 1 hour
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=1)  # Set the duration of the 'remember me' cookie
    #app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
    db.init_app(app)

     # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # Set the login route for redirect if needed

    # Define the user_loader function
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import User, Image, ContactMe, BookingShoot

    create_database(app)

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Dataase!')