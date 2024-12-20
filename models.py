from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'balance': self.balance,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class LoginRecord(db.Model):
    __tablename__ = 'login_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    card_number = db.Column(db.String(50), nullable=False)
    recharge_number = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.1)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

    __table_args__ = (
        db.Index('idx_user_id', 'user_id'),
        db.Index('idx_timestamp', 'timestamp'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'card_number': self.card_number,
            'recharge_number': self.recharge_number,
            'amount': self.amount,
            'status': self.status,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
