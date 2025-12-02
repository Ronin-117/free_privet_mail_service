"""
Database initialization script.

Author: AI Assistant
Created: 2025-12-02
"""

import os
import sys
from app import create_app
from models import db, User

def init_database():
    """Initialize the database and create default admin user."""
    
    # Get environment
    env = os.getenv('FLASK_ENV', 'development')
    
    # Create app
    app = create_app(env)
    
    with app.app_context():
        print('Creating database tables...')
        db.create_all()
        print('✓ Database tables created')
        
        # Check if admin user exists
        admin_email = app.config['ADMIN_EMAIL']
        existing_user = User.query.filter_by(email=admin_email).first()
        
        if existing_user:
            print(f'✓ Admin user already exists: {admin_email}')
        else:
            # Create admin user
            admin_password = app.config['ADMIN_PASSWORD']
            user = User(email=admin_email)
            user.set_password(admin_password)
            db.session.add(user)
            db.session.commit()
            print(f'✓ Admin user created: {admin_email}')
            print(f'  Password: {admin_password}')
            print('  Please change the password after first login!')
        
        print('\n✓ Database initialization complete!')

if __name__ == '__main__':
    init_database()
