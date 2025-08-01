from urllib.parse import urlparse
from flask import jsonify
import re
import string
import random

def validate_url(url):
    """Validate URL format using urlparse"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def validate_email(email):
    """Validate email format using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def error_response(status_code, message):
    """Standard error response format"""
    return jsonify({
        'error': status_code,
        'message': message,
        'success': False
    }), status_code

def generate_short_code(length=6):
    """Generate random alphanumeric short code"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))