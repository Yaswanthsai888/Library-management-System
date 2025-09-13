"""Error handlers for the API."""
from flask import jsonify
from marshmallow import ValidationError

def register_error_handlers(app):
    """Register error handlers with the Flask app.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return jsonify({
            "error": "Bad request",
            "message": str(error)
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            "error": "Resource not found"
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error."""
        return jsonify({
            "error": "Internal server error"
        }), 500

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle Marshmallow validation errors."""
        return jsonify({
            "error": "Validation error",
            "messages": error.messages
        }), 400
