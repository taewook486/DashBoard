"""
Tests for service modules.
@SPEC:IMPROVE-001
"""

import pytest
from unittest.mock import patch, MagicMock
import time


class TestCacheService:
    """Tests for CacheService."""

    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        from app.services.cache import CacheService

        cache = CacheService(default_ttl=60)
        cache.set('test_key', 'test_value')

        result = cache.get('test_key')
        assert result == 'test_value'

    def test_cache_miss(self):
        """Test cache miss returns None."""
        from app.services.cache import CacheService

        cache = CacheService()
        result = cache.get('nonexistent_key')
        assert result is None

    def test_cache_expiration(self):
        """Test cache entry expires after TTL."""
        from app.services.cache import CacheService

        cache = CacheService(default_ttl=1)  # 1 second TTL
        cache.set('test_key', 'test_value')

        # Should exist immediately
        assert cache.get('test_key') == 'test_value'

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get('test_key') is None

    def test_cache_delete(self):
        """Test cache delete operation."""
        from app.services.cache import CacheService

        cache = CacheService()
        cache.set('test_key', 'test_value')

        assert cache.delete('test_key') is True
        assert cache.get('test_key') is None
        assert cache.delete('test_key') is False  # Already deleted

    def test_cache_clear(self):
        """Test cache clear operation."""
        from app.services.cache import CacheService

        cache = CacheService()
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')

        cache.clear()

        assert cache.get('key1') is None
        assert cache.get('key2') is None

    def test_cache_generate_key(self):
        """Test cache key generation."""
        from app.services.cache import CacheService

        key1 = CacheService.generate_key('a', 'b', c='d')
        key2 = CacheService.generate_key('a', 'b', c='d')
        key3 = CacheService.generate_key('x', 'y', z='w')

        assert key1 == key2  # Same args = same key
        assert key1 != key3  # Different args = different key

    def test_cached_decorator(self):
        """Test @cached decorator."""
        from app.services.cache import cached

        call_count = 0

        @cached(ttl=60, key_prefix='test')
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call with same args should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented

        # Different args should execute function
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2


class TestMarketDataService:
    """Tests for MarketDataService."""

    def test_get_ticker_data_success(self):
        """Test successful ticker data fetch."""
        from app.services.market_data import MarketDataService

        mock_hist = MagicMock()
        mock_hist.empty = False
        mock_hist.__len__ = lambda self: 5
        mock_hist.__getitem__ = lambda self, key: MagicMock(
            iloc=[100.0, 101.0, 102.0, 103.0, 104.0]
        )
        mock_hist['Close'] = MagicMock(iloc=MagicMock(
            __getitem__=lambda s, i: 104.0 - i
        ))
        mock_hist['Open'] = MagicMock(iloc=MagicMock(
            __getitem__=lambda s, i: 103.0 - i
        ))
        mock_hist['High'] = MagicMock(iloc=MagicMock(
            __getitem__=lambda s, i: 105.0 - i
        ))
        mock_hist['Low'] = MagicMock(iloc=MagicMock(
            __getitem__=lambda s, i: 102.0 - i
        ))
        mock_hist['Volume'] = MagicMock(iloc=MagicMock(
            __getitem__=lambda s, i: 1000000
        ))

        with patch('yfinance.Ticker') as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = mock_hist
            mock_ticker_class.return_value = mock_ticker

            service = MarketDataService()
            result = service.get_ticker_data('AAPL')

            # Should have called yfinance
            mock_ticker.history.assert_called()

    def test_get_ticker_data_empty(self):
        """Test ticker data fetch with empty response."""
        from app.services.market_data import MarketDataService

        mock_hist = MagicMock()
        mock_hist.empty = True

        with patch('yfinance.Ticker') as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = mock_hist
            mock_ticker_class.return_value = mock_ticker

            service = MarketDataService()
            result = service.get_ticker_data('INVALID')

            assert result is None

    def test_get_index_data(self):
        """Test index data fetch."""
        from app.services.market_data import MarketDataService

        with patch.object(MarketDataService, 'get_ticker_data') as mock_get:
            mock_get.return_value = {
                'current_price': 5000.0,
                'previous_price': 4950.0,
                'change': 50.0,
                'change_pct': 1.01,
            }

            service = MarketDataService()
            result = service.get_index_data([
                ('^GSPC', 'S&P 500'),
            ])

            assert len(result) == 1
            assert result[0]['name'] == 'S&P 500'
            assert result[0]['symbol'] == '^GSPC'

    def test_get_sector_info(self):
        """Test sector info retrieval."""
        from app.services.market_data import MarketDataService

        mock_info = {'sector': 'Technology'}

        with patch('yfinance.Ticker') as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.info = mock_info
            mock_ticker_class.return_value = mock_ticker

            service = MarketDataService()
            result = service.get_sector_info('AAPL')

            assert result == 'Tech'
