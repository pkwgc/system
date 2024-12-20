from flask import Flask, render_template, jsonify
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

# Frontend routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/records')
def records():
    return render_template('records.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# API routes with rate limiting
@app.route('/api/records')
@limiter.limit("1000 per minute")
def get_records():
    try:
        records = LoginRecord.query.order_by(LoginRecord.timestamp.desc()).all()
        return jsonify({
            'data': [record.to_dict() for record in records]
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

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
