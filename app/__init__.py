import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.extensions import db, migrate


load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Or your actual URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Import db from models and initialize it with app
    from app.extensions import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    
    from app.routes.auth import auth
    from app.routes.books import books
    from app.routes.librarianroutes import librarian
    
    
    app.register_blueprint(auth)
    app.register_blueprint(books)
    app.register_blueprint(librarian)

    return app