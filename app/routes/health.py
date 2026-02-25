"""
Health check routes.
@SPEC:IMPROVE-001 REQ-HEALTH-001
"""

from flask import Blueprint, jsonify, current_app
import time
import structlog

logger = structlog.get_logger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    @SPEC:IMPROVE-001 REQ-HEALTH-001

    Returns:
        JSON response with health status, version, and timestamp
    """
    return jsonify({
        'status': 'healthy',
        'version': current_app.config.get('VERSION', '1.0.0'),
        'timestamp': time.time(),
        'environment': current_app.config.get('FLASK_ENV', 'development')
    })
