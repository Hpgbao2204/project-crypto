"""
Main application entry point for the web application.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from flask import Flask, render_template
from flask_migrate import Migrate
from src.extensions import db, login_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
    
    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register user loader
    from src.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))
    
    # Register blueprints
    from src.routes.auth import auth_bp
    from src.routes.encryption import encryption_bp
    from src.routes.signature import signature_bp
    from src.routes.document import document_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(encryption_bp, url_prefix='/encryption')
    app.register_blueprint(signature_bp, url_prefix='/signature')
    app.register_blueprint(document_bp, url_prefix='/document')
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Register routes
    @app.route('/')
    def index():
        """Render the home page."""
        return render_template('index.html', title='Home')
    
    @app.route('/about')
    def about():
        """Render the about page."""
        return render_template('about.html', title='About')
    
    return app

# Create the application instance
app = create_app()

def create_tables():
    """Create database tables."""
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0')