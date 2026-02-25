"""
Additional tests for improved coverage.
@SPEC:IMPROVE-001
"""

import pytest
import json
from unittest.mock import patch, MagicMock, mock_open


class TestConfigModels:
    """Tests for configuration and Pydantic models."""

    def test_chart_period_enum(self):
        """Test ChartPeriod enum values."""
        from app.models.schemas import ChartPeriod

        assert ChartPeriod.ONE_YEAR.value == "1y"
        assert ChartPeriod.ONE_MONTH.value == "1mo"
        assert ChartPeriod.MAX.value == "max"

    def test_language_enum(self):
        """Test Language enum values."""
        from app.models.schemas import Language

        assert Language.KOREAN.value == "ko"
        assert Language.ENGLISH.value == "en"

    def test_ai_model_enum(self):
        """Test AIModel enum values."""
        from app.models.schemas import AIModel

        assert AIModel.GEMINI.value == "gemini"
        assert AIModel.GPT.value == "gpt"

    def test_ticker_request_validation(self):
        """Test TickerRequest validation."""
        from app.models.schemas import TickerRequest

        # Valid ticker
        req = TickerRequest(ticker="aapl")
        assert req.ticker == "AAPL"

        # Invalid ticker
        with pytest.raises(ValueError):
            TickerRequest(ticker="INVALID@TICKER!")

    def test_chart_request_validation(self):
        """Test ChartRequest validation."""
        from app.models.schemas import ChartRequest, ChartPeriod

        req = ChartRequest(ticker="msft", period=ChartPeriod.SIX_MONTHS)
        assert req.ticker == "MSFT"
        assert req.period == "6mo"

    def test_ai_summary_request_validation(self):
        """Test AISummaryRequest validation."""
        from app.models.schemas import AISummaryRequest, Language

        req = AISummaryRequest(ticker="googl", lang=Language.ENGLISH)
        assert req.ticker == "GOOGL"
        assert req.lang == "en"

    def test_error_response_model(self):
        """Test ErrorResponse model."""
        from app.models.schemas import ErrorResponse, ErrorDetail

        response = ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Invalid ticker",
                details={"field": "ticker"}
            ),
            request_id="test-123"
        )

        assert response.success is False
        assert response.error.code == "VALIDATION_ERROR"
        assert response.request_id == "test-123"

    def test_api_response_model(self):
        """Test ApiResponse model."""
        from app.models.schemas import ApiResponse

        response = ApiResponse(
            data={"price": 100.0},
            meta={"cached": True}
        )

        assert response.success is True
        assert response.data["price"] == 100.0


class TestDecorators:
    """Tests for security decorators."""

    def test_validate_ticker_param_valid(self):
        """Test validate_ticker_param with valid ticker."""
        from app.utils.decorators import validate_ticker_param
        from flask import Flask, jsonify

        app = Flask(__name__)

        @app.route('/test/<ticker>')
        @validate_ticker_param
        def test_route(ticker):
            return jsonify({'ticker': ticker})

        with app.test_client() as client:
            response = client.get('/test/aapl')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['ticker'] == 'AAPL'

    def test_log_request_decorator(self):
        """Test log_request decorator."""
        from app.utils.decorators import log_request
        from flask import Flask, jsonify

        app = Flask(__name__)

        @app.route('/test-log')
        @log_request
        def test_route():
            return jsonify({'ok': True})

        with app.test_client() as client:
            response = client.get('/test-log')
            assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling utilities."""

    def test_log_exception(self):
        """Test log_exception utility."""
        from app.utils.errors import log_exception, DashBoardError, ErrorCode

        error = DashBoardError(
            message="Test error",
            code=ErrorCode.VALIDATION_ERROR,
            details={'field': 'test'}
        )

        # Should not raise
        log_exception(error, {'context': 'test'})

    def test_not_found_error(self):
        """Test NotFoundError."""
        from app.utils.errors import NotFoundError

        error = NotFoundError("Stock", "AAPL")
        assert error.status_code == 404
        assert "Stock" in error.message
        assert "AAPL" in error.message

    def test_api_error(self):
        """Test APIError."""
        from app.utils.errors import APIError

        error = APIError(
            message="API failed",
            api_name="yfinance",
            original_error="Network timeout"
        )

        assert error.status_code == 502
        assert error.details['api_name'] == "yfinance"

    def test_rate_limited_error(self):
        """Test RateLimitedError."""
        from app.utils.errors import RateLimitedError

        error = RateLimitedError(retry_after=60)
        assert error.status_code == 429
        assert error.details['retry_after'] == 60


class TestCacheEdgeCases:
    """Tests for cache service edge cases."""

    def test_cleanup_expired_with_no_expired(self):
        """Test cleanup_expired when no entries are expired."""
        from app.services.cache import CacheService

        cache = CacheService(default_ttl=300)
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')

        removed = cache.cleanup_expired()
        assert removed == 0

    def test_generate_key_with_complex_args(self):
        """Test generate_key with complex arguments."""
        from app.services.cache import CacheService

        key1 = CacheService.generate_key([1, 2, 3], {'a': 'b'})
        key2 = CacheService.generate_key([1, 2, 3], {'a': 'b'})
        key3 = CacheService.generate_key([1, 2, 4], {'a': 'b'})

        assert key1 == key2
        assert key1 != key3

    def test_cached_decorator_cache_clear(self):
        """Test cached decorator cache_clear method."""
        from app.services.cache import cached

        @cached(ttl=60)
        def test_func(x):
            return x * 2

        test_func(5)
        test_func.cache_clear()

        # Should work after clear
        result = test_func(5)
        assert result == 10


class TestMarketDataServiceEdgeCases:
    """Tests for market data service edge cases."""

    def test_get_ticker_data_batch_empty_list(self):
        """Test batch fetch with empty list."""
        from app.services.market_data import MarketDataService

        service = MarketDataService()
        result = service.get_ticker_data_batch([])
        assert result == {}

    def test_get_sector_info_error(self):
        """Test sector info with yfinance error."""
        from app.services.market_data import MarketDataService

        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.side_effect = Exception("API Error")

            service = MarketDataService()
            result = service.get_sector_info('UNKNOWN')

            assert result == '-'

    def test_get_index_data_with_fallback(self):
        """Test index data with fallback for failed fetch."""
        from app.services.market_data import MarketDataService

        with patch.object(MarketDataService, 'get_ticker_data') as mock_get:
            mock_get.return_value = None  # Simulate failed fetch

            service = MarketDataService()
            result = service.get_index_data([('^GSPC', 'S&P 500')])

            assert len(result) == 1
            assert result[0]['price'] == 0  # Fallback value
