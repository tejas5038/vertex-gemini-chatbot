"""
Decorators for error handling and request validation.
"""

from functools import wraps
from flask import request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_errors(f):
    """
    Decorator to handle errors gracefully in Flask routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({
                'error': True,
                'message': f'Validation error: {str(e)}'
            }), 400
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return jsonify({
                'error': True,
                'message': 'An unexpected error occurred. Please try again.'
            }), 500
    
    return decorated_function


def validate_json(f):
    """
    Decorator to validate that request contains JSON data.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                'error': True,
                'message': 'Request must be JSON'
            }), 400
        return f(*args, **kwargs)
    
    return decorated_function


def log_request(f):
    """
    Decorator to log incoming requests.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Request to {request.endpoint}: {request.method} {request.path}")
        return f(*args, **kwargs)
    
    return decorated_function
