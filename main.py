from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from login_module import login_route, rechargesubmission
from models import db, User, LoginRecord
from config import Config
import argparse

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per minute"],
    storage_uri="memory://"
)

# Apply rate limiting to routes
@app.route('/login', methods=['POST'])
@limiter.limit("1000 per minute")
def login():
    return login_route()

@app.route('/rechargesubmission', methods=['POST'])
@limiter.limit("1000 per minute")
def recharge():
    return rechargesubmission()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8081)
    args = parser.parse_args()

    app.run(
        host='0.0.0.0',  # Allow external access
        port=args.port,  # Use port from command line arguments
        debug=False,     # Disable debug mode for production
        threaded=True    # Enable threading for concurrent requests
    )
