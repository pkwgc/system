from flask import Flask
from models import db
from config import Config
import time
from sqlalchemy import text

def test_database_connection():
    """Test database connection and basic operations"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    try:
        with app.app_context():
            # Test connection
            db.engine.connect()
            print("✓ Database connection successful")

            # Test query execution
            result = db.session.execute(text("SELECT 1")).scalar()
            print("✓ Query execution successful")

            # Test connection pool
            for _ in range(5):
                db.engine.connect()
                time.sleep(0.1)
            print("✓ Connection pool working")

            return True

    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    if not success:
        exit(1)
