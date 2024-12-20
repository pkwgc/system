import unittest
from main import app, db
from models import User, RechargeRecord
from sqlalchemy import inspect

class TestWebApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://pkwgc:Wghfd@584521@fd@rm-m5e0666vtv5234qi39o.mysql.rds.aliyuncs.com:3306/stsmen'
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()  # Drop all tables first
            db.create_all()  # Create fresh tables

    def tearDown(self):
        with app.app_context():
            try:
                db.session.query(User).delete()
                db.session.query(RechargeRecord).delete()
                db.session.commit()
            except:
                db.session.rollback()
            finally:
                db.session.remove()
                db.drop_all()  # Clean up by dropping all tables

    def test_database_connection(self):
        """Test database connection and table creation"""
        with app.app_context():
            # Check if tables exist using SQLAlchemy inspector
            inspector = inspect(db.engine)
            self.assertTrue('users' in inspector.get_table_names())
            self.assertTrue('recharge_records' in inspector.get_table_names())

    def test_user_creation_and_balance(self):
        """Test user creation and balance management"""
        with app.app_context():
            user = User(userid='test_user', balance=1.0)
            db.session.add(user)
            db.session.commit()

            fetched_user = User.query.filter_by(userid='test_user').first()
            self.assertIsNotNone(fetched_user)
            self.assertEqual(fetched_user.balance, 1.0)

    def test_login_insufficient_balance(self):
        """Test login with insufficient balance"""
        with app.app_context():
            user = User(userid='poor_user', balance=0.05)
            db.session.add(user)
            db.session.commit()

            response = self.client.post('/login', json={
                'userid': 'poor_user',
                'phoneNum': '1234567890',
                'androidId': 'test_android',
                'token': 'test_token',
                'ip': '127.0.0.1',
                'mobile': '1234567890'
            })

            self.assertEqual(response.status_code, 400)
            self.assertIn('Insufficient balance', response.get_json()['error'])

    def test_login_sufficient_balance(self):
        """Test login with sufficient balance"""
        with app.app_context():
            user = User(userid='rich_user', balance=1.0)
            db.session.add(user)
            db.session.commit()

            initial_balance = user.balance

            response = self.client.post('/login', json={
                'userid': 'rich_user',
                'phoneNum': '1234567890',
                'androidId': 'test_android',
                'token': 'test_token',
                'ip': '127.0.0.1',
                'mobile': '1234567890'
            })

            user = User.query.filter_by(userid='rich_user').first()
            self.assertEqual(user.balance, initial_balance - 0.1)

    def test_record_creation(self):
        """Test recharge record creation"""
        with app.app_context():
            record = RechargeRecord(
                userid='test_user',
                phone_number='1234567890',
                card_number='TEST123',
                amount=0.1,
                status='success'
            )
            db.session.add(record)
            db.session.commit()

            fetched_record = RechargeRecord.query.filter_by(userid='test_user').first()
            self.assertIsNotNone(fetched_record)
            self.assertEqual(fetched_record.amount, 0.1)

    def test_records_page(self):
        """Test frontend records page"""
        response = self.client.get('/records')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<meta charset="utf-8">', response.data)
        self.assertIn(b'records', response.data)

if __name__ == '__main__':
    unittest.main()
