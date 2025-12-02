"""
Utility functions for the email service API.

Author: AI Assistant
Created: 2025-12-02
"""

import os
import secrets
import string
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import jsonify


def generate_api_key(length=48):
    """
    Generate a secure random API key.
    
    Args:
        length: Length of the API key (default: 48)
        
    Returns:
        str: Secure random API key
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def allowed_file(filename, allowed_extensions):
    """
    Check if a file has an allowed extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions
        
    Returns:
        bool: True if file extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, upload_folder, api_key_id):
    """
    Save an uploaded file with a secure filename.
    
    Args:
        file: FileStorage object from request
        upload_folder: Base upload folder path
        api_key_id: ID of the API key (for organizing files)
        
    Returns:
        tuple: (stored_filename, file_path, file_size)
    """
    # Create directory structure: uploads/api_key_id/YYYY-MM/
    now = datetime.utcnow()
    date_folder = now.strftime('%Y-%m')
    target_dir = Path(upload_folder) / str(api_key_id) / date_folder
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate secure filename with timestamp
    original_filename = secure_filename(file.filename)
    timestamp = now.strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(original_filename)
    stored_filename = f"{timestamp}_{secrets.token_hex(8)}_{name}{ext}"
    
    # Save file
    file_path = target_dir / stored_filename
    file.save(str(file_path))
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    return stored_filename, str(file_path), file_size


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        str: Formatted file size (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def success_response(data=None, message=None, status_code=200):
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        tuple: (response, status_code)
    """
    response = {
        'success': True,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code


def error_response(message, status_code=400, errors=None):
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        errors: Additional error details
        
    Returns:
        tuple: (response, status_code)
    """
    response = {
        'success': False,
        'message': message,
        'errors': errors
    }
    return jsonify(response), status_code


def validate_email(email):
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email is valid
    """
    try:
        from email_validator import validate_email as ev_validate
        ev_validate(email)
        return True
    except:
        # Fallback to basic validation
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


def sanitize_form_data(data):
    """
    Sanitize form data by removing potentially dangerous content.
    
    Args:
        data: Dictionary of form data
        
    Returns:
        dict: Sanitized form data
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remove null bytes and limit length
            value = value.replace('\x00', '').strip()
            value = value[:10000]  # Limit to 10k characters
        sanitized[key] = value
    return sanitized


def get_client_ip(request):
    """
    Get the client's IP address from the request.
    
    Args:
        request: Flask request object
        
    Returns:
        str: Client IP address
    """
    # Check for proxy headers
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr
