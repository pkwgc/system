from flask import Flask
from models import db
from config import Config

def init_db():
    """Initialize the database with all tables"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()
        return True, "Database tables created successfully"

if __name__ == "__main__":
    success, message = init_db()
    print(message)
