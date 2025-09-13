"""Initialize Flask application and register components."""
from flask import Flask
from flask_cors import CORS
from api.config.config import config
from api.routes.book_routes import book_bp
from api.error_handlers import register_error_handlers

def create_app(config_name='default'):
    """Create and configure the Flask application.
    
    Args:
        config_name (str): Name of configuration to use
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(book_bp, url_prefix='/api')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Home route
    @app.route("/")
    def home():
        return "<h1>Library Management System API is running!</h1>"
    
    return app
