"""
Database models for the email service API.

Author: AI Assistant
Created: 2025-12-02
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

db = SQLAlchemy()


class User(db.Model):
    """Admin user model for dashboard access."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set the user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class ApiKey(db.Model):
    """API key model for form submission authentication."""
    
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    recipient_email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_used = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    usage_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Relationships
    submissions = db.relationship('FormSubmission', backref='api_key', lazy='dynamic', cascade='all, delete-orphan')
    
    @staticmethod
    def generate_key():
        """Generate a secure random API key."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(48))
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used = datetime.utcnow()
    
    def to_dict(self):
        """Convert API key to dictionary."""
        return {
            'id': self.id,
            'key': self.key,
            'name': self.name,
            'description': self.description,
            'recipient_email': self.recipient_email,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'is_active': self.is_active,
            'usage_count': self.usage_count,
            'submission_count': self.submissions.count()
        }


class FormSubmission(db.Model):
    """Form submission model to store submitted data."""
    
    __tablename__ = 'form_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=False, index=True)
    data = db.Column(db.JSON, nullable=False)  # Store form data as JSON
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    email_sent = db.Column(db.Boolean, default=False, nullable=False)
    email_error = db.Column(db.Text)
    
    # Relationships
    files = db.relationship('FileUpload', backref='submission', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_files=True):
        """Convert submission to dictionary."""
        result = {
            'id': self.id,
            'api_key_id': self.api_key_id,
            'data': self.data,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat(),
            'email_sent': self.email_sent,
            'email_error': self.email_error
        }
        
        if include_files:
            result['files'] = [f.to_dict() for f in self.files]
        
        return result


class FileUpload(db.Model):
    """File upload model to store uploaded file metadata."""
    
    __tablename__ = 'file_uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('form_submissions.id'), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert file upload to dictionary."""
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'created_at': self.created_at.isoformat() if self.created_at else datetime.utcnow().isoformat()
        }
