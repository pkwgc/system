from flask import Flask
from models import db, LoginRecord, User
from config import Config
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def verify_recharge_records():
    """Verify generated recharge record data integrity"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # Get all records
        records = LoginRecord.query.all()
        logger.info(f"Found {len(records)} recharge records in database")

        # Get all valid user_ids
        valid_users = set(user.user_id for user in User.query.all())

        # Verify each record
        for record in records:
            logger.info(f"\nVerifying record ID: {record.id}")

            # Verify user exists
            if record.user_id in valid_users:
                logger.info(f"Valid user_id: {record.user_id}")
            else:
                logger.error(f"Invalid user_id: {record.user_id}")

            # Verify card number format
            if record.card_number and record.card_number.isdigit():
                logger.info(f"Valid card number format: {record.card_number}")
            else:
                logger.error(f"Invalid card number format: {record.card_number}")

            # Verify recharge number format
            if record.recharge_number and record.recharge_number.isdigit():
                logger.info(f"Valid recharge number format: {record.recharge_number}")
            else:
                logger.error(f"Invalid recharge number format: {record.recharge_number}")

            # Verify amount
            if record.amount == 0.1:
                logger.info("Valid amount: 0.1")
            else:
                logger.error(f"Invalid amount: {record.amount}")

            # Verify status
            if record.status in ['success', 'pending', 'failed']:
                logger.info(f"Valid status: {record.status}")
            else:
                logger.error(f"Invalid status: {record.status}")

            # Verify timestamp
            if isinstance(record.timestamp, datetime):
                logger.info(f"Valid timestamp: {record.timestamp}")
            else:
                logger.error(f"Invalid timestamp format: {record.timestamp}")

if __name__ == '__main__':
    verify_recharge_records()
