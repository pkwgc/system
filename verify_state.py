from flask import Flask
from models import db, User
from config import Config

def verify_database_state():
    """Verify database state and user existence"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        user = User.query.filter_by(user_id='test_user').first()
        if user:
            print(f'User exists with balance: {user.balance}')
            print(f'Password hash: {user.password_hash}')
        else:
            print('User not found')

if __name__ == '__main__':
    verify_database_state()
