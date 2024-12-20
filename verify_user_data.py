from flask import Flask
from models import db, User
from config import Config
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def verify_user_data():
    """Verify generated user data integrity"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # Get all users
        users = User.query.all()
        logger.info(f"Found {len(users)} users in database")

        # Verify each user's data
        for user in users:
            logger.info(f"\nVerifying user: {user.user_id}")
            logger.info(f"Balance: {user.balance}")

            # Verify password hash format
            if user.password_hash and len(user.password_hash) > 20:
                logger.info("Password hash present and valid length")
            else:
                logger.error(f"Invalid password hash for user {user.user_id}")

            # Verify balance is within expected range
            if 0.0 <= user.balance <= 100.0:
                logger.info("Balance within valid range")
            else:
                logger.error(f"Invalid balance {user.balance} for user {user.user_id}")

if __name__ == '__main__':
    verify_user_data()
