from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, RechargeRecord
from config import Config
from database_ops import safe_delete_tables, backup_tables

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Import routes after app creation to avoid circular imports
from login_module import login_route, rechargesubmission

# Route for login page (GET)
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# API routes (POST)
app.add_url_rule('/login', view_func=login_route, methods=['POST'])
app.add_url_rule('/rechargesubmission', view_func=rechargesubmission, methods=['POST'])

@app.route('/records')
def view_records():
    records = RechargeRecord.query.order_by(RechargeRecord.timestamp.desc()).all()
    return render_template('records.html', records=records)

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/admin/delete-tables', methods=['POST'])
def delete_tables():
    tables = request.json.get('tables', None)  # None means all tables
    success, message = safe_delete_tables(tables)
    return jsonify({'success': success, 'message': message})

@app.route('/admin/backup', methods=['POST'])
def create_backup():
    tables = request.json.get('tables', None)  # None means all tables
    try:
        backup_file = backup_tables(tables)
        return jsonify({'success': True, 'backup_file': backup_file})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(port=8081, debug=True, threaded=True)
