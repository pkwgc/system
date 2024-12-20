from flask import Flask
from models import db, User, LoginRecord
from config import Config
from werkzeug.security import generate_password_hash
import random
import string
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_random_string(length=8):
    """Generate random string for usernames"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_random_number(length=10):
    """Generate random number string for card/recharge numbers"""
    return ''.join(random.choices(string.digits, k=length))

def generate_test_data(num_users=10, records_per_user=5):
    """Generate random test users and login records"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        try:
            # Generate users
            users = []
            for i in range(num_users):
                user_id = f"test_user_{generate_random_string()}"
                password = generate_random_string(10)
                balance = round(random.uniform(1.0, 100.0), 2)

                user = User(user_id=user_id, balance=balance)
                user.set_password(password)
                db.session.add(user)
                users.append((user_id, password))
                logger.debug(f"Created user: {user_id} with balance: {balance}")

            db.session.commit()
            logger.info(f"Successfully created {num_users} test users")

            # Generate login records
            for user_id, _ in users:
                for _ in range(records_per_user):
                    card_number = generate_random_number()
                    recharge_number = generate_random_number()
                    timestamp = datetime.utcnow() - timedelta(
                        days=random.randint(0, 30),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                    status = random.choice(['success', 'pending', 'failed'])

                    record = LoginRecord(
                        user_id=user_id,
                        card_number=card_number,
                        recharge_number=recharge_number,
                        timestamp=timestamp,
                        status=status,
                        amount=0.1
                    )
                    db.session.add(record)
                    logger.debug(f"Created login record for user: {user_id}")

            db.session.commit()
            logger.info(f"Successfully created {num_users * records_per_user} login records")

            # Print sample of created data
            print("\nSample of created test data:")
            print("\nUsers:")
            for user_id, password in users[:3]:
                user = User.query.filter_by(user_id=user_id).first()
                print(f"User ID: {user_id}, Password: {password}, Balance: {user.balance}")

            print("\nLogin Records (sample):")
            records = LoginRecord.query.limit(3).all()
            for record in records:
                print(f"User: {record.user_id}, Status: {record.status}, Time: {record.timestamp}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error generating test data: {str(e)}")
            raise

if __name__ == '__main__':
    generate_test_data(num_users=20, records_per_user=10)
