from flask import request, current_app
from flask_mail import Message
from extensions import mail

def send_verification_email(user_email, token):
    """Send email verification to user"""
    try:
        msg = Message(
            'Verify Your Email - EV Scan Platform',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[user_email]
        )
        verification_link = f"{request.host_url}api/auth/verify/{token}"
        msg.body = f"""
        Please click the following link to verify your email:
        {verification_link}
        
        This link will expire in 24 hours.
        """
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present in data"""
    missing_fields = []
    for field in required_fields:
        if not data.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None

def create_error_response(message, status_code=400):
    """Create standardized error response"""
    return {'error': message}, status_code

def create_success_response(data=None, message=None, status_code=200):
    """Create standardized success response"""
    response = {}
    if message:
        response['message'] = message
    if data:
        response.update(data)
    
    return response, status_code