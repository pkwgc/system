from main import app, db
from models import User, RechargeRecord

def test_database_connection():
    with app.app_context():
        try:
            # Test database connection and table creation
            db.create_all()
            print('Database connection successful')
            print('Tables created successfully:')
            print('- users table exists:', User.__table__.exists(db.engine))
            print('- recharge_records table exists:', RechargeRecord.__table__.exists(db.engine))
            return True
        except Exception as e:
            print('Database connection failed:', str(e))
            return False

if __name__ == '__main__':
    test_database_connection()
