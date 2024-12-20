from flask import Flask
from models import db
from config import Config

def init_database():
    """Initialize database tables"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # Drop all tables first to ensure clean state
        db.drop_all()
        # Create all tables
        db.create_all()
        print('Database tables created successfully')

if __name__ == '__main__':
    init_database()
