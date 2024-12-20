from flask import Flask
from models import db
from config import Config

def verify_database():
    """Initialize database and verify table creation"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # Drop existing tables first
        db.drop_all()
        # Create tables
        db.create_all()
        # Get inspector
        inspector = db.inspect(db.engine)
        # Print created tables
        print('\nCreated tables:', inspector.get_table_names())
        # Print table details
        for table in inspector.get_table_names():
            print(f'\nColumns in {table}:')
            for column in inspector.get_columns(table):
                print(f'- {column["name"]}: {column["type"]}')

if __name__ == '__main__':
    verify_database()
