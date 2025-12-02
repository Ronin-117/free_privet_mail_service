"""
Main Flask application for the email service API.

Author: AI Assistant
Created: 2025-12-02
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity
from werkzeug.exceptions import RequestEntityTooLarge

from config import config
from models import db, User, ApiKey, FormSubmission, FileUpload
from email_service import EmailService
from auth import jwt_required_custom
from utils import (
    allowed_file, save_uploaded_file, success_response, 
    error_response, validate_email, sanitize_form_data, get_client_ip
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """Create and configure the Flask application."""
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    jwt = JWTManager(app)
    
    # Initialize email service
    email_service = EmailService(app.config)
    
    # Create database tables and default user
    with app.app_context():
        db.create_all()
        create_default_user(app)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return error_response('Resource not found', 404)
    
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f'Internal server error: {str(e)}')
        return error_response('Internal server error', 500)
    
    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(e):
        return error_response('File size exceeds maximum allowed size', 413)
    
    # ============================================================================
    # PUBLIC API ENDPOINTS
    # ============================================================================
    
    @app.route('/api/v1/submit/<api_key>', methods=['POST', 'OPTIONS'])
    def submit_form(api_key):
        """
        Public endpoint for form submissions.
        
        Args:
            api_key: API key for authentication
            
        Returns:
            JSON response with submission status
        """
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            return '', 204
        
        try:
            # Validate API key
            key_obj = ApiKey.query.filter_by(key=api_key, is_active=True).first()
            if not key_obj:
                return error_response('Invalid or inactive API key', 401)
            
            # Get form data
            form_data = request.form.to_dict()
            
            # Validate that we have some data
            if not form_data:
                return error_response('No form data provided', 400)
            
            # Sanitize form data
            form_data = sanitize_form_data(form_data)
            
            # Create submission record
            submission = FormSubmission(
                api_key_id=key_obj.id,
                data=form_data,
                ip_address=get_client_ip(request),
                user_agent=request.headers.get('User-Agent', '')[:255]
            )
            db.session.add(submission)
            db.session.flush()  # Get submission ID
            
            # Handle file uploads
            uploaded_files = []
            if request.files:
                for field_name in request.files:
                    file = request.files[field_name]
                    if file and file.filename:
                        # Validate file
                        if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
                            return error_response(
                                f'File type not allowed: {file.filename}',
                                400
                            )
                        
                        # Save file
                        try:
                            stored_filename, file_path, file_size = save_uploaded_file(
                                file,
                                app.config['UPLOAD_FOLDER'],
                                key_obj.id
                            )
                            
                            # Create file record
                            file_upload = FileUpload(
                                submission_id=submission.id,
                                original_filename=file.filename,
                                stored_filename=stored_filename,
                                file_path=file_path,
                                file_size=file_size,
                                mime_type=file.content_type
                            )
                            db.session.add(file_upload)
                            uploaded_files.append(file_upload.to_dict())
                            
                        except Exception as e:
                            logger.error(f'File upload error: {str(e)}')
                            return error_response(f'Failed to upload file: {file.filename}', 500)
            
            # Send email notification
            try:
                success, error_msg = email_service.send_submission_notification(
                    key_obj.recipient_email,
                    key_obj.name,
                    form_data,
                    uploaded_files
                )
                submission.email_sent = success
                if not success:
                    submission.email_error = error_msg
            except Exception as e:
                logger.error(f'Email sending error: {str(e)}')
                submission.email_sent = False
                submission.email_error = str(e)
            
            # Update API key usage
            key_obj.increment_usage()
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f'Form submission received for API key: {key_obj.name}')
            
            return success_response(
                data={'submission_id': submission.id},
                message='Form submitted successfully',
                status_code=201
            )
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Form submission error: {str(e)}')
            return error_response('Failed to process form submission', 500)
    
    # ============================================================================
    # AUTHENTICATION ENDPOINTS
    # ============================================================================
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """
        Login endpoint for admin users.
        
        Returns:
            JSON response with JWT token
        """
        try:
            data = request.get_json()
            
            if not data or not data.get('email') or not data.get('password'):
                return error_response('Email and password required', 400)
            
            user = User.query.filter_by(email=data['email']).first()
            
            if not user or not user.check_password(data['password']):
                return error_response('Invalid email or password', 401)
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Create access token
            access_token = create_access_token(identity=user.id)
            
            return success_response(
                data={
                    'access_token': access_token,
                    'user': user.to_dict()
                },
                message='Login successful'
            )
            
        except Exception as e:
            logger.error(f'Login error: {str(e)}')
            return error_response('Login failed', 500)
    
    @app.route('/api/auth/me', methods=['GET'])
    @jwt_required_custom
    def get_current_user():
        """
        Get current authenticated user.
        
        Returns:
            JSON response with user data
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return error_response('User not found', 404)
            
            return success_response(data=user.to_dict())
            
        except Exception as e:
            logger.error(f'Get user error: {str(e)}')
            return error_response('Failed to get user', 500)
    
    # ============================================================================
    # API KEY MANAGEMENT ENDPOINTS
    # ============================================================================
    
    @app.route('/api/keys', methods=['GET'])
    @jwt_required_custom
    def get_api_keys():
        """
        Get all API keys.
        
        Returns:
            JSON response with list of API keys
        """
        try:
            keys = ApiKey.query.order_by(ApiKey.created_at.desc()).all()
            return success_response(data=[key.to_dict() for key in keys])
            
        except Exception as e:
            logger.error(f'Get API keys error: {str(e)}')
            return error_response('Failed to get API keys', 500)
    
    @app.route('/api/keys', methods=['POST'])
    @jwt_required_custom
    def create_api_key():
        """
        Create a new API key.
        
        Returns:
            JSON response with created API key
        """
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data or not data.get('name') or not data.get('recipient_email'):
                return error_response('Name and recipient email are required', 400)
            
            # Validate email
            if not validate_email(data['recipient_email']):
                return error_response('Invalid email address', 400)
            
            # Create API key
            api_key = ApiKey(
                key=ApiKey.generate_key(),
                name=data['name'],
                description=data.get('description', ''),
                recipient_email=data['recipient_email']
            )
            
            db.session.add(api_key)
            db.session.commit()
            
            logger.info(f'API key created: {api_key.name}')
            
            return success_response(
                data=api_key.to_dict(),
                message='API key created successfully',
                status_code=201
            )
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Create API key error: {str(e)}')
            return error_response('Failed to create API key', 500)
    
    @app.route('/api/keys/<int:key_id>', methods=['PUT'])
    @jwt_required_custom
    def update_api_key(key_id):
        """
        Update an API key.
        
        Args:
            key_id: ID of the API key to update
            
        Returns:
            JSON response with updated API key
        """
        try:
            api_key = ApiKey.query.get(key_id)
            if not api_key:
                return error_response('API key not found', 404)
            
            data = request.get_json()
            
            # Update fields
            if 'name' in data:
                api_key.name = data['name']
            if 'description' in data:
                api_key.description = data['description']
            if 'recipient_email' in data:
                if not validate_email(data['recipient_email']):
                    return error_response('Invalid email address', 400)
                api_key.recipient_email = data['recipient_email']
            if 'is_active' in data:
                api_key.is_active = bool(data['is_active'])
            
            db.session.commit()
            
            logger.info(f'API key updated: {api_key.name}')
            
            return success_response(
                data=api_key.to_dict(),
                message='API key updated successfully'
            )
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Update API key error: {str(e)}')
            return error_response('Failed to update API key', 500)
    
    @app.route('/api/keys/<int:key_id>', methods=['DELETE'])
    @jwt_required_custom
    def delete_api_key(key_id):
        """
        Delete an API key.
        
        Args:
            key_id: ID of the API key to delete
            
        Returns:
            JSON response with success message
        """
        try:
            api_key = ApiKey.query.get(key_id)
            if not api_key:
                return error_response('API key not found', 404)
            
            db.session.delete(api_key)
            db.session.commit()
            
            logger.info(f'API key deleted: {api_key.name}')
            
            return success_response(message='API key deleted successfully')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Delete API key error: {str(e)}')
            return error_response('Failed to delete API key', 500)
    
    # ============================================================================
    # SUBMISSION MANAGEMENT ENDPOINTS
    # ============================================================================
    
    @app.route('/api/submissions', methods=['GET'])
    @jwt_required_custom
    def get_submissions():
        """
        Get all form submissions with pagination.
        
        Returns:
            JSON response with list of submissions
        """
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            api_key_id = request.args.get('api_key_id', type=int)
            
            query = FormSubmission.query
            
            # Filter by API key if specified
            if api_key_id:
                query = query.filter_by(api_key_id=api_key_id)
            
            # Order by most recent first
            query = query.order_by(FormSubmission.created_at.desc())
            
            # Paginate
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return success_response(data={
                'submissions': [s.to_dict() for s in pagination.items],
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            })
            
        except Exception as e:
            logger.error(f'Get submissions error: {str(e)}')
            return error_response('Failed to get submissions', 500)
    
    @app.route('/api/submissions/<int:submission_id>', methods=['GET'])
    @jwt_required_custom
    def get_submission(submission_id):
        """
        Get a specific submission.
        
        Args:
            submission_id: ID of the submission
            
        Returns:
            JSON response with submission data
        """
        try:
            submission = FormSubmission.query.get(submission_id)
            if not submission:
                return error_response('Submission not found', 404)
            
            return success_response(data=submission.to_dict())
            
        except Exception as e:
            logger.error(f'Get submission error: {str(e)}')
            return error_response('Failed to get submission', 500)
    
    @app.route('/api/submissions/<int:submission_id>', methods=['DELETE'])
    @jwt_required_custom
    def delete_submission(submission_id):
        """
        Delete a submission.
        
        Args:
            submission_id: ID of the submission to delete
            
        Returns:
            JSON response with success message
        """
        try:
            submission = FormSubmission.query.get(submission_id)
            if not submission:
                return error_response('Submission not found', 404)
            
            db.session.delete(submission)
            db.session.commit()
            
            logger.info(f'Submission deleted: {submission_id}')
            
            return success_response(message='Submission deleted successfully')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Delete submission error: {str(e)}')
            return error_response('Failed to delete submission', 500)
    
    @app.route('/api/files/<int:file_id>/download', methods=['GET'])
    @jwt_required_custom
    def download_file(file_id):
        """
        Download an uploaded file.
        
        Args:
            file_id: ID of the file to download
            
        Returns:
            File download
        """
        try:
            file_upload = FileUpload.query.get(file_id)
            if not file_upload:
                return error_response('File not found', 404)
            
            return send_file(
                file_upload.file_path,
                as_attachment=True,
                download_name=file_upload.original_filename
            )
            
        except Exception as e:
            logger.error(f'Download file error: {str(e)}')
            return error_response('Failed to download file', 500)
    
    # ============================================================================
    # STATISTICS ENDPOINTS
    # ============================================================================
    
    @app.route('/api/stats', methods=['GET'])
    @jwt_required_custom
    def get_stats():
        """
        Get dashboard statistics.
        
        Returns:
            JSON response with statistics
        """
        try:
            total_keys = ApiKey.query.count()
            active_keys = ApiKey.query.filter_by(is_active=True).count()
            total_submissions = FormSubmission.query.count()
            total_files = FileUpload.query.count()
            
            # Recent submissions (last 7 days)
            from datetime import timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_submissions = FormSubmission.query.filter(
                FormSubmission.created_at >= week_ago
            ).count()
            
            return success_response(data={
                'total_api_keys': total_keys,
                'active_api_keys': active_keys,
                'total_submissions': total_submissions,
                'recent_submissions': recent_submissions,
                'total_files': total_files
            })
            
        except Exception as e:
            logger.error(f'Get stats error: {str(e)}')
            return error_response('Failed to get statistics', 500)
    
    # ============================================================================
    # WEB INTERFACE ROUTES
    # ============================================================================
    
    @app.route('/')
    def index():
        """Render the dashboard page."""
        return render_template('index.html')
    
    @app.route('/login')
    def login_page():
        """Render the login page."""
        return render_template('login.html')
    
    @app.route('/submissions')
    def submissions_page():
        """Render the submissions page."""
        return render_template('submissions.html')
    
    # Health check endpoint
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return success_response(data={'status': 'healthy'})
    
    return app


def create_default_user(app):
    """Create default admin user if none exists."""
    try:
        if User.query.count() == 0:
            user = User(email=app.config['ADMIN_EMAIL'])
            user.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(user)
            db.session.commit()
            logger.info(f'Default admin user created: {app.config["ADMIN_EMAIL"]}')
    except Exception as e:
        logger.error(f'Failed to create default user: {str(e)}')


# Create app instance for Gunicorn
env = os.getenv('FLASK_ENV', 'production')
app = create_app(env)


if __name__ == '__main__':
    # Run app directly (for local development)
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(env == 'development'))
