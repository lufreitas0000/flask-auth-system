from src.extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # UX
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(50), unique=True, nullable=True)
    bio = db.Column(db.String(255), nullable=True)
    locked_until = db.Column(db.DateTime(timezone=True), nullable=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'



class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    # The Foreign Key links this log row directly to a specific user's ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ip_address = db.Column(db.String(45), nullable=True) # Supports IPv6
    was_successful = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<AuditLog {self.user_id} - Success: {self.was_successful}>'




# Flask-Login doesn't automatically know how to talk to SQLAlchemy. We have to give it a "Translator" function.
# This tells Flask-Login how to find a user in the database using the ID from the cookie

from src.extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
