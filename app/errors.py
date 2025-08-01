from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Register all error handlers for the application"""
    
    # Handle 400 Bad Request
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request',
            'details': str(error.description) if hasattr(error, 'description') else None
        }), 400

    # Handle 401 Unauthorized
    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({
            'success': False,
            'error': 401,
            'message': 'Unauthorized',
            'details': 'Authentication required'
        }), 401

    # Handle 404 Not Found
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource Not Found'
        }), 404

    # Handle 500 Internal Server Error
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error',
            'details': 'An unexpected error occurred'
        }), 500

    # Handle all other HTTP exceptions
    @app.errorhandler(HTTPException)
    def http_error_handler(error):
        return jsonify({
            'success': False,
            'error': error.code,
            'message': error.name,
            'details': error.description
        }), error.code

    # Handle generic Python exceptions
    @app.errorhandler(Exception)
    def handle_exception(error):
        # Pass through HTTP errors
        if isinstance(error, HTTPException):
            return error
        
        # Log the error here if you have logging setup
        
        # Return JSON instead of HTML for API errors
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error',
            'details': str(error)
        }), 500