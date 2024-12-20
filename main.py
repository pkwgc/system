from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from models import db, User, RechargeRecord
import urllib.parse

app = Flask(__name__)
password = urllib.parse.quote_plus('Wghfd@584521@fd')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://pkwgc:{password}@rm-m5e0666vtv5234qi39o.mysql.rds.aliyuncs.com:3306/stsmen'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Import routes after app creation to avoid circular imports
from login_module import login_route, rechargesubmission

app.add_url_rule('/login', view_func=login_route, methods=['POST'])
app.add_url_rule('/rechargesubmission', view_func=rechargesubmission, methods=['POST'])

@app.route('/records')
def view_records():
    records = RechargeRecord.query.order_by(RechargeRecord.timestamp.desc()).all()
    return render_template('records.html', records=records)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=8081, debug=True, threaded=True)
