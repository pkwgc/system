from flask import Flask
from models import db, User
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def create_test_user():
    with app.app_context():
        # Create test user if it doesn't exist
        test_user = User.query.filter_by(user_id='test_user').first()
        if not test_user:
            test_user = User(user_id='test_user')
            test_user.set_password('test_pass')
            test_user.balance = 1.0
            db.session.add(test_user)
            db.session.commit()
            print('Test user created successfully')
        else:
            test_user.balance = 1.0  # Ensure test user has sufficient balance
            db.session.commit()
            print('Test user updated with new balance')

if __name__ == '__main__':
    create_test_user()
