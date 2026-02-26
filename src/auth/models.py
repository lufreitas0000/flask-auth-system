from src.extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone
from typing import Optional

from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer

class BaseModel(db.Model):
    """An Abstract base model"""
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class User(UserMixin, BaseModel):
    """
    The core User model representing an authenticated entity in the system.
    """
    __tablename__ = "users"

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # security and state
    last_login = db.Column(db.DateTime, nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Boolean, default=False)
    locked_until = db.Column(db.DateTime(timezone=True), nullable=True)

    # profile data
    username = db.Column(db.String(50), unique=True, nullable=True)
    bio = db.Column(db.String(255), nullable=True)

    # relationships
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def get_reset_token(self) -> str:
        """Generates a cryptographically sign token containing the user ID"""
        s = Serializer( current_app.config['SECRET_KEY'])
        return s.dumps({'user_id':self.id})
    @staticmethod
    def verify_reset_token(token:str, expires_sec: int = 1800) -> Optional['User']:
        """Verifies the token and returns the user if it is valid and not expired."""
        s = Serializer( current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except Exception:
            return None
        #return User.query.get(user_id)
        return db.session.get(User, user_id)


class AuditLog(BaseModel):
    """
    Tracks historical authentication events for security auditing.
    """
    __tablename__ = "audit_logs"

    # The Foreign Key links this log row directly to a specific user's ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    ip_address = db.Column(db.String(45), nullable=True) # Supports IPv6
    was_successful = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<AuditLog {self.user_id} - Success: {self.was_successful}>'




# Flask-Login doesn't automatically know how to talk to SQLAlchemy. We have to give it a "Translator" function.
# This tells Flask-Login how to find a user in the database using the ID from the cookie

from src.extensions import login_manager

@login_manager.user_loader
def load_user(user_id) -> Optional[User]:
    """Retrieves a user by their ID from the encrypted session cookie."""
    return User.query.get(int(user_id))
