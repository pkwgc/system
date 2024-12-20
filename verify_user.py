from flask import Flask
from models import db, User
from config import Config
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def recreate_test_user():
    """Recreate test user with proper password hashing"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # Delete existing test user if exists
        test_user = User.query.filter_by(user_id='test_user').first()
        if test_user:
            logger.debug(f"Deleting existing test user: {test_user.user_id}")
            db.session.delete(test_user)
            db.session.commit()

        # Create new test user
        new_user = User(user_id='test_user', balance=1.0)
        password = 'test_pass'
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Verify password hash
        logger.debug(f"New user created with hash: {new_user.password_hash}")
        verification = new_user.check_password(password)
        logger.debug(f"Password verification result: {verification}")

        return verification

if __name__ == '__main__':
    result = recreate_test_user()
    print(f"User recreation successful: {result}")
