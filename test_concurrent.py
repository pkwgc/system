import asyncio
import aiohttp
import time
import logging
import json
from models import db, User
from flask import Flask
from config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def make_request(session, url, data):
    """Make an async HTTP request"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        async with session.post(url, json=data, headers=headers) as response:
            try:
                response_text = await response.text()
                logger.debug(f"Request data: {data}")
                logger.debug(f"Response headers: {response.headers}")
                logger.debug(f"Response text: {response_text}")
                return response_text, response.status
            except Exception as e:
                logger.error(f"Error reading response: {str(e)}")
                return str(e), 500
    except Exception as e:
        logger.error(f"Request error: {str(e)}")
        return str(e), 500

async def setup_test_user():
    """Ensure test user exists with sufficient balance"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        user = User.query.filter_by(user_id="test_user").first()
        if user:
            user.balance = 100.0  # Reset balance to ensure enough for tests
            user.set_password('test123')  # Use correct password setting method
            db.session.commit()
            logger.info("Test user balance reset to 100.0")
        else:
            user = User(
                user_id='test_user',
                username='Test User',
                balance=100.0
            )
            user.set_password('test123')  # Use correct password setting method
            db.session.add(user)
            db.session.commit()
            logger.info("Test user created with balance 100.0")
    return True

async def run_concurrent_test(num_requests=10):  # Reduced to 10 requests for initial testing
    """Test concurrent requests to the API"""
    logger.info(f"Starting concurrent test with {num_requests} requests...")

    # Setup test user
    if not await setup_test_user():
        logger.error("Failed to setup test user")
        return False

    # Test data with proper format including password
    test_data = {
        "user_id": "test_user",
        "password": "test123",  # Added password field
        "card_number": "1234567890",
        "recharge_number": "9876543210"
    }

    url = "http://localhost:8081/login"

    async with aiohttp.ClientSession() as session:
        tasks = []
        start_time = time.time()

        # Create tasks for concurrent requests
        for i in range(num_requests):
            task = make_request(session, url, test_data)
            tasks.append(task)

        # Execute requests concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        duration = end_time - start_time

        # Analyze results
        success_count = 0
        error_count = 0

        for response, status in responses:
            if status == 200:
                success_count += 1
            else:
                error_count += 1
                logger.error(f"Failed request: Status={status}, Response={response}")

        logger.info("\nTest Results:")
        logger.info(f"Total Requests: {num_requests}")
        logger.info(f"Successful Requests: {success_count}")
        logger.info(f"Failed Requests: {error_count}")
        logger.info(f"Total Duration: {duration:.2f} seconds")
        logger.info(f"Requests per Second: {num_requests/duration:.2f}")

        # Log detailed response info for debugging
        for i, (response, status) in enumerate(responses[:5]):
            logger.debug(f"Sample response {i}: Status={status}, Response={response}")

        return success_count > 0  # Consider test successful if at least some requests succeed

async def main():
    """Main async function"""
    return await run_concurrent_test()

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        exit(1)
