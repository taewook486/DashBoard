"""
DashBoard Flask Application Factory
@SPEC:IMPROVE-001
@MX:ANCHOR: Application entry point - all blueprints registered here
@MX:REASON: Central factory pattern for Flask app configuration
"""

from flask import Flask
import structlog
from typing import Optional

from app.config import Config
from app.utils.logging import configure_logging


def create_app(config_class: Optional[type] = None) -> Flask:
    """
    Application factory for DashBoard Flask app.

    Args:
        config_class: Configuration class to use. Defaults to Config from config.py

    Returns:
        Configured Flask application instance
    """
    if config_class is None:
        config_class = Config

    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # Load configuration
    app.config.from_object(config_class)

    # Configure structured logging
    configure_logging(app.config.get('LOG_LEVEL', 'INFO'))
    logger = structlog.get_logger(__name__)
    logger.info("Initializing DashBoard application",
                env=app.config.get('FLASK_ENV', 'development'))

    # Initialize extensions
    _init_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Register health check endpoint
    _register_health_check(app)

    logger.info("DashBoard application initialized successfully")

    return app


def _init_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    # CORS configuration
    if app.config.get('CORS_ENABLED', True):
        from flask_cors import CORS
        CORS(app, origins=app.config.get('ALLOWED_ORIGINS', '*'))

    # Rate limiting
    if app.config.get('RATE_LIMIT_ENABLED', True):
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[app.config.get('RATE_LIMIT_DEFAULT', '100 per minute')],
            storage_uri=app.config.get('RATE_LIMIT_STORAGE', 'memory://')
        )


def _register_blueprints(app: Flask) -> None:
    """
    Register Flask blueprints.
    @SPEC:IMPROVE-001 REQ-ARCH-002
    """
    from app.routes.market import market_bp
    from app.routes.health import health_bp

    # Register market routes (includes / and /api/*)
    app.register_blueprint(market_bp)

    # Register health check routes
    app.register_blueprint(health_bp)

    logger = structlog.get_logger(__name__)
    logger.info("Blueprints registered", blueprints=['market', 'health'])


def _register_health_check(app: Flask) -> None:
    """Register health check endpoint - now handled by health blueprint."""
    # Health check is now registered via health_bp blueprint
    pass
