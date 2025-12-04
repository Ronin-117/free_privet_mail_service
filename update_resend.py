"""
Script to add Resend API integration to email_service.py

This script updates the email service to use Resend API for sending emails.
Run this once to update your email service.
"""

import re

# Read the current email_service.py
with open('email_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add imports at the top (after existing imports)
if 'import requests' not in content:
    content = content.replace(
        'import smtplib\nimport logging',
        'import smtplib\nimport logging\nimport requests'
    )

# 2. Add Resend API key to __init__ method
init_pattern = r"(self\.app_url = getattr\(config, 'APP_URL', 'http://localhost:5000'\))"
resend_config = """
        
        # Resend API Configuration (preferred - 100% free)
        self.resend_api_key = getattr(config, 'RESEND_API_KEY', '')"""

if 'RESEND_API_KEY' not in content:
    content = re.sub(init_pattern, r'\1' + resend_config, content)

# 3. Update send_submission_notification to try Resend first
send_pattern = r"(def send_submission_notification.*?try:)(.*?)(# Create message)"
resend_send = r"""\1\2# Try Resend first if configured
            if self.resend_api_key:
                return self._send_via_resend(recipient_email, api_key_name, form_data, files)
            # Fall back to SMTP
            else:
                return self._send_via_smtp(recipient_email, api_key_name, form_data, files)
        except Exception as e:
            error_msg = f'Failed to send email: {str(e)}'
            logger.error(error_msg)
            return False, error_msg
    
    def _send_via_resend(self, recipient_email, api_key_name, form_data, files=None):
        """Send email via Resend API."""
        try:
            import base64
            
            # Prepare email data
            email_data = {
                'from': f'{self.from_name} <{self.from_email}>',
                'to': [recipient_email],
                'subject': f'New Form Submission - {api_key_name}',
                'html': self._create_html_body(api_key_name, form_data, files)
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
            
            # Send via Resend API
            response = requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {self.resend_api_key}',
                    'Content-Type': 'application/json'
                },
                json=email_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f'Email sent successfully via Resend to {recipient_email}')
                return True, None
            else:
                error_msg = f'Resend API error: {response.status_code} - {response.text}'
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f'Resend error: {str(e)}'
            logger.error(error_msg)
            return False, error_msg
    
    def _send_via_smtp(self, recipient_email, api_key_name, form_data, files=None):
        """Send email via SMTP (fallback method)."""
        try:
            \3"""

if '_send_via_resend' not in content:
    content = re.sub(send_pattern, resend_send, content, flags=re.DOTALL)

# Write the updated content
with open('email_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ email_service.py updated successfully!")
print("✅ Resend API integration added")
print("\nNext steps:")
print("1. Make sure RESEND_API_KEY is set in your Render environment variables")
print("2. Make sure SMTP_FROM_EMAIL is set (e.g., onboarding@resend.dev)")
print("3. Deploy to Render")
