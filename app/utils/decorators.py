"""
Security decorators for route protection.
@SPEC:IMPROVE-001 REQ-SEC-002
"""

from functools import wraps
from flask import jsonify, request
import structlog

from app.utils.errors import ValidationError, create_error_response
from app.utils.validators import validate_ticker, validate_period

logger = structlog.get_logger(__name__)


def validate_ticker_param(f):
    """
    Decorator to validate ticker parameter in URL.
    @SPEC:IMPROVE-001 REQ-SEC-002

    Usage:
        @market_bp.route("/api/us/stock-chart/<ticker>")
        @validate_ticker_param
        def get_stock_chart(ticker):
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ticker = kwargs.get('ticker')
        if ticker:
            try:
                # Validate and normalize ticker
                kwargs['ticker'] = validate_ticker(ticker)
            except ValidationError as e:
                logger.warning(
                    "Invalid ticker parameter",
                    ticker=ticker,
                    error=e.message
                )
                return jsonify(create_error_response(e)), 400
        return f(*args, **kwargs)
    return decorated_function


def validate_period_param(f):
    """
    Decorator to validate period query parameter.
    @SPEC:IMPROVE-001 REQ-SEC-002

    Usage:
        @market_bp.route("/api/us/stock-chart/<ticker>")
        @validate_period_param
        def get_stock_chart(ticker):
            period = request.validated_period  # Access validated period
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        period = request.args.get('period', '1y')
        request.validated_period = validate_period(period)
        return f(*args, **kwargs)
    return decorated_function


def require_json(f):
    """
    Decorator to require JSON content type for POST requests.
    @SPEC:IMPROVE-001 REQ-SEC-002
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_CONTENT_TYPE',
                        'message': 'Content-Type must be application/json'
                    }
                }), 415
        return f(*args, **kwargs)
    return decorated_function


def log_request(f):
    """
    Decorator to log request details.
    @SPEC:IMPROVE-001 REQ-LOG-003
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(
            "API request received",
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr
        )
        return f(*args, **kwargs)
    return decorated_function
