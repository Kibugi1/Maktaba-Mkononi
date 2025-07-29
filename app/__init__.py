import os
from flask import Flask
from dotenv import load_dotenv
from app.routes.registerLogin import auth
from app.routes.books import books
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Or your actual URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Import db from models and initialize it with app
    from app.models import db
    db.init_app(app)

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    app.register_blueprint(auth)
    app.register_blueprint(books)

    return app