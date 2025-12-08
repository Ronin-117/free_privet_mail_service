"""
Email service for sending form submission notifications.
Now with Resend API support for production use on Render.

Author: AI Assistant
Created: 2025-12-02
Updated: 2025-12-04 - Added Resend API integration
"""

import smtplib
import logging
import resend
import base64
import socket
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications via Resend API or SMTP."""
    
    def __init__(self, config):
        """
        Initialize email service with configuration.
        
        Args:
            config: Flask configuration object
        """
        # SMTP Configuration (fallback)
        self.smtp_host = getattr(config, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(config, 'SMTP_PORT', 587)
        self.smtp_username = getattr(config, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(config, 'SMTP_PASSWORD', '')
        self.from_email = getattr(config, 'SMTP_FROM_EMAIL', 'onboarding@resend.dev')
        self.from_name = getattr(config, 'SMTP_FROM_NAME', 'Form Service')
        self.app_url = getattr(config, 'APP_URL', 'http://localhost:5000')
        
        # Resend API Configuration - load directly from environment to avoid timing issues
        import os
        self.resend_api_key = os.getenv('RESEND_API_KEY', '')
        
        # Debug logging
        if self.resend_api_key:
            logger.info(f'✅ Resend API key loaded: {self.resend_api_key[:10]}...')
        else:
            logger.warning('❌ No Resend API key found - will use SMTP fallback')
    
    def send_submission_notification(self, recipient_email, api_key_name, form_data, files=None):
        """
        Send email notification for a new form submission.
        
        Args:
            recipient_email: Email address to send notification to
            api_key_name: Name of the API key used
            form_data: Dictionary of form data
            files: List of FileUpload objects (optional)
            
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            # Try Resend first if configured
            if self.resend_api_key:
                logger.info('Attempting to send email via Resend API')
                return self._send_via_resend(recipient_email, api_key_name, form_data, files)
            # Fall back to SMTP
            else:
                logger.info('Attempting to send email via SMTP')
                return self._send_via_smtp(recipient_email, api_key_name, form_data, files)
        except Exception as e:
            error_msg = f'Failed to send email: {str(e)}'
            logger.error(error_msg)
            return False, error_msg
    
    
    def _warm_up_network(self):
        """
        Perform a lightweight network connection to 'wake up' the network stack.
        This resolves DNS and establishes a TCP connection without sending data.
        Does not consume API credits.
        """
        try:
            logger.info('Network warmup: Connecting to api.resend.com...')
            sock = socket.create_connection(("api.resend.com", 443), timeout=3)
            sock.close()
            logger.info('✅ Network warmup successful')
            return True
        except Exception as e:
            logger.warning(f'⚠️ Network warmup failed (proceeding anyway): {str(e)}')
            return False

    def _send_via_resend(self, recipient_email, api_key_name, form_data, files=None):
        """Send email via Resend API using official SDK."""
        try:
            # Step 1: Warm up the network connection
            self._warm_up_network()
            
            # Step 2: Set API key
            resend.api_key = self.resend_api_key
            
            # Prepare email data
            email_data = {
                "from": f'{self.from_name} <{self.from_email}>',
                "to": [recipient_email],
                "subject": f'New Form Submission - {api_key_name}',
                "html": self._create_html_body(api_key_name, form_data, files)
            }
            
            # Add file attachments if any
            if files:
                attachments = []
                for file_obj in files:
                    try:
                        file_path = Path(file_obj.file_path)
                        if file_path.exists():
                            with open(file_path, 'rb') as f:
                                content = base64.b64encode(f.read()).decode()
                                attachments.append({
                                    'filename': file_obj.original_filename,
                                    'content': content
                                })
                    except Exception as e:
                        logger.warning(f'Failed to attach file {file_obj.original_filename}: {str(e)}')
                
                if attachments:
                    email_data['attachments'] = attachments
            
            # Send via Resend SDK
            response = resend.Emails.send(email_data)
            
            logger.info(f'Email sent successfully via Resend to {recipient_email}')
            return True, None
                
        except Exception as e:
            error_msg = f'Resend error: {str(e)}'
            logger.error(error_msg)
            return False, error_msg
    
    def _send_via_smtp(self, recipient_email, api_key_name, form_data, files=None):
        """Send email via SMTP (fallback method)."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'New Form Submission - {api_key_name}'
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = recipient_email
            msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
            
            # Create HTML body
            html_body = self._create_html_body(api_key_name, form_data, files)
            
            # Create plain text body
            text_body = self._create_text_body(api_key_name, form_data, files)
            
            # Attach both versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Attach files if any
            if files:
                for file_obj in files:
                    self._attach_file(msg, file_obj)
            
            # Send email
            self._send_email(msg, recipient_email)
            
            logger.info(f'Email sent successfully to {recipient_email}')
            return True, None
            
        except Exception as e:
            error_msg = f'Failed to send email: {str(e)}'
            logger.error(error_msg)
            return False, error_msg
    
    def _create_html_body(self, api_key_name, form_data, files):
        """Create HTML email body."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .field {{
                    background: white;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #667eea;
                }}
                .field-label {{
                    font-weight: 600;
                    color: #667eea;
                    font-size: 12px;
                    text-transform: uppercase;
                    margin-bottom: 5px;
                }}
                .field-value {{
                    color: #333;
                    font-size: 14px;
                    word-wrap: break-word;
                }}
                .files {{
                    margin-top: 20px;
                }}
                .file-item {{
                    background: white;
                    padding: 10px 15px;
                    margin-bottom: 10px;
                    border-radius: 5px;
                    display: flex;
                    align-items: center;
                }}
                .file-icon {{
                    margin-right: 10px;
                    font-size: 20px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📧 New Form Submission</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">From: {api_key_name}</p>
            </div>
            <div class="content">
        """
        
        # Add form fields
        for key, value in form_data.items():
            html += f"""
                <div class="field">
                    <div class="field-label">{key}</div>
                    <div class="field-value">{value}</div>
                </div>
            """
        
        # Add files if any
        if files:
            html += """
                <div class="files">
                    <h3 style="color: #667eea; margin-bottom: 15px;">📎 Attached Files</h3>
            """
            for file_obj in files:
                filename = getattr(file_obj, 'original_filename', 'file')
                filesize = getattr(file_obj, 'file_size', 0)
                html += f"""
                    <div class="file-item">
                        <span class="file-icon">📄</span>
                        <div>
                            <strong>{filename}</strong>
                            <div style="font-size: 12px; color: #666;">
                                {self._format_file_size(filesize)}
                            </div>
                        </div>
                    </div>
                """
            html += "</div>"
        
        html += f"""
            </div>
            <div class="footer">
                <p>This email was sent from your Form Service API</p>
                <p><a href="{self.app_url}" style="color: #667eea;">View Dashboard</a></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_text_body(self, api_key_name, form_data, files):
        """Create plain text email body."""
        text = f"New Form Submission\n"
        text += f"From: {api_key_name}\n"
        text += f"{'-' * 50}\n\n"
        
        for key, value in form_data.items():
            text += f"{key}:\n{value}\n\n"
        
        if files:
            text += f"\nAttached Files ({len(files)}):\n"
            for file_obj in files:
                filename = getattr(file_obj, 'original_filename', 'file')
                filesize = getattr(file_obj, 'file_size', 0)
                text += f"- {filename} ({self._format_file_size(filesize)})\n"
        
        text += f"\n{'-' * 50}\n"
        text += f"View dashboard: {self.app_url}\n"
        
        return text
    
    def _attach_file(self, msg, file_obj):
        """Attach a file to the email message."""
        try:
            file_path = Path(file_obj.file_path)
            original_filename = file_obj.original_filename
            
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {original_filename}'
                    )
                    msg.attach(part)
        except Exception as e:
            logger.error(f'Failed to attach file {file_obj.original_filename}: {str(e)}')
    
    def _send_email(self, msg, recipient):
        """Send the email via SMTP."""
        try:
            # Add timeout to prevent worker hanging
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
        except Exception as e:
            logger.error(f'SMTP error: {str(e)}')
            raise
    
    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
