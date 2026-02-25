"""
Route modules for DashBoard application.
@SPEC:IMPROVE-001
"""

from app.routes.market import market_bp
from app.routes.health import health_bp

__all__ = [
    'market_bp',
    'health_bp',
]
