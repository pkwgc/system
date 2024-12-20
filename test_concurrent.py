import threading
import pytest
from main import app, db
from models import User
import time
import uuid

@pytest.fixture(autouse=True)
def cleanup():
    with app.app_context():
        test_user = User.query.filter(User.userid.like('test_user%')).first()
        if test_user:
            db.session.delete(test_user)
            db.session.commit()
        yield
        test_user = User.query.filter(User.userid.like('test_user%')).first()
        if test_user:
            db.session.delete(test_user)
            db.session.commit()

def test_concurrent_login():
    with app.app_context():
        test_userid = f'test_user_{uuid.uuid4().hex[:8]}'
        try:
            user = User(userid=test_userid, balance=1.0)
            # Debug logging for password setting
            print(f"\nDebug - Creating user with ID: {test_userid}")
            user.set_password('password')
            print(f"Debug - Set password hash: {user.password_hash}")
            db.session.add(user)
            db.session.commit()

            # Verify password immediately after creation
            fresh_user = User.query.filter_by(userid=test_userid).first()
            print(f"Debug - Verification test: {fresh_user.check_password('password')}\n")
        except Exception as e:
            db.session.rollback()
            pytest.fail(f"Failed to create test user: {str(e)}")

        results = []
        response_data = []  # Add list to store full response data

        def login_request():
            try:
                client = app.test_client()
                response = client.post('/login',
                    json={
                        'userid': test_userid,
                        'password': 'password',
                        'phoneNum': '1234567890'
                    },
                    headers={'X-Test-Request': 'true'}  # Add test header
                )
                results.append(response.status_code)
                response_data.append(response.get_json())
                print(f"Response: {response.status_code}, Data: {response.get_json()}")
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                results.append(error_msg)
                response_data.append({"error": str(e)})
                print(error_msg)

        threads = [threading.Thread(target=login_request) for _ in range(10)]
        for t in threads:
            t.start()

        for t in threads:
            t.join()

        try:
            user = User.query.filter_by(userid=test_userid).first()
            expected_balance = 0.0
            assert user.balance == expected_balance, f"Expected balance {expected_balance}, got {user.balance}"

            assert all(isinstance(code, int) and code == 200 for code in results), \
                f"Not all login requests succeeded. Results: {results}"

        finally:
            if user:
                db.session.delete(user)
                db.session.commit()

if __name__ == '__main__':
    pytest.main([__file__])
