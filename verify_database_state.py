from flask import Flask
from models import db, User, LoginRecord
from config import Config
import logging
from sqlalchemy import func

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def verify_database_state():
    """Verify overall database state and data integrity"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # Get counts
        user_count = User.query.count()
        record_count = LoginRecord.query.count()
        logger.info(f"Total users in database: {user_count}")
        logger.info(f"Total login records in database: {record_count}")

        # Verify user statistics
        total_balance = db.session.query(func.sum(User.balance)).scalar()
        avg_balance = db.session.query(func.avg(User.balance)).scalar()
        logger.info(f"Total user balance: {total_balance:.2f}")
        logger.info(f"Average user balance: {avg_balance:.2f}")

        # Verify record statistics
        status_counts = db.session.query(
            LoginRecord.status,
            func.count(LoginRecord.id)
        ).group_by(LoginRecord.status).all()

        logger.info("\nLogin record status distribution:")
        for status, count in status_counts:
            logger.info(f"{status}: {count} records")

        # Verify record amounts
        total_amount = db.session.query(func.sum(LoginRecord.amount)).scalar()
        logger.info(f"\nTotal amount in login records: {total_amount:.2f}")

        # Verify user-record relationships
        orphaned_records = LoginRecord.query.filter(
            ~LoginRecord.user_id.in_(
                db.session.query(User.user_id)
            )
        ).count()

        if orphaned_records > 0:
            logger.error(f"Found {orphaned_records} records with invalid user_id references")
        else:
            logger.info("All login records have valid user references")

        return {
            'user_count': user_count,
            'record_count': record_count,
            'total_balance': total_balance,
            'orphaned_records': orphaned_records
        }

if __name__ == '__main__':
    stats = verify_database_state()
    print("\nDatabase Verification Summary:")
    print(f"Users: {stats['user_count']}")
    print(f"Records: {stats['record_count']}")
    print(f"Total Balance: {stats['total_balance']:.2f}")
    print(f"Orphaned Records: {stats['orphaned_records']}")
