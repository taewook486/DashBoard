"""
Custom error classes and error handling utilities.
@SPEC:IMPROVE-001 REQ-ERR-001, REQ-ERR-002, REQ-ERR-003
"""

from typing import Optional, Dict, Any
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class ErrorCode(Enum):
    """Standard error codes for the application."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    DATA_NOT_AVAILABLE = "DATA_NOT_AVAILABLE"


class DashBoardError(Exception):
    """
    Base exception class for DashBoard application.
    @SPEC:IMPROVE-001 REQ-ERR-001
    """

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        return {
            'success': False,
            'error': {
                'code': self.code.value,
                'message': self.message,
                'details': self.details
            }
        }


class ValidationError(DashBoardError):
    """
    Exception for input validation errors.
    @SPEC:IMPROVE-001 REQ-SEC-002
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        constraint: Optional[str] = None
    ):
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = str(value)
        if constraint:
            details['constraint'] = constraint

        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            details=details,
            status_code=400
        )


class NotFoundError(DashBoardError):
    """Exception for resource not found errors."""

    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with identifier '{identifier}' not found"

        super().__init__(
            message=message,
            code=ErrorCode.NOT_FOUND,
            details={'resource': resource, 'identifier': identifier},
            status_code=404
        )


class APIError(DashBoardError):
    """Exception for external API errors."""

    def __init__(
        self,
        message: str,
        api_name: Optional[str] = None,
        original_error: Optional[str] = None
    ):
        details = {}
        if api_name:
            details['api_name'] = api_name
        if original_error:
            details['original_error'] = original_error

        super().__init__(
            message=message,
            code=ErrorCode.EXTERNAL_API_ERROR,
            details=details,
            status_code=502
        )


class RateLimitedError(DashBoardError):
    """Exception for rate limiting."""

    def __init__(self, retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details['retry_after'] = retry_after

        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            code=ErrorCode.RATE_LIMITED,
            details=details,
            status_code=429
        )


def log_exception(exc: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an exception with full context.
    @SPEC:IMPROVE-001 REQ-ERR-001
    """
    context = context or {}

    if isinstance(exc, DashBoardError):
        logger.error(
            "Application error occurred",
            error_type=exc.__class__.__name__,
            error_code=exc.code.value,
            message=exc.message,
            details=exc.details,
            status_code=exc.status_code,
            **context
        )
    else:
        logger.exception(
            "Unexpected error occurred",
            error_type=exc.__class__.__name__,
            message=str(exc),
            **context
        )


def create_error_response(exc: Exception, request_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized error response.
    @SPEC:IMPROVE-001 REQ-ERR-003
    """
    if isinstance(exc, DashBoardError):
        response = exc.to_dict()
    else:
        response = {
            'success': False,
            'error': {
                'code': ErrorCode.INTERNAL_ERROR.value,
                'message': 'An unexpected error occurred',
                'details': {}
            }
        }

    if request_id:
        response['request_id'] = request_id

    return response
