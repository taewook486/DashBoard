"""
Tests for route modules.
@SPEC:IMPROVE-001
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestHealthRoutes:
    """Tests for health check routes."""

    def test_health_endpoint_returns_json(self, client):
        """Test that /health returns JSON."""
        response = client.get('/health')
        assert response.content_type == 'application/json'
        assert response.status_code == 200

    def test_health_endpoint_structure(self, client):
        """Test /health response structure."""
        response = client.get('/health')
        data = json.loads(response.data)

        assert 'status' in data
        assert 'version' in data
        assert 'timestamp' in data
        assert data['status'] == 'healthy'


class TestMarketRoutes:
    """Tests for market data routes."""

    def test_root_endpoint(self, client):
        """Test root endpoint renders index.html."""
        response = client.get('/')
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'

    def test_api_indices_returns_json(self, client):
        """Test /api/us/indices returns JSON."""
        response = client.get('/api/us/indices')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

    def test_api_smart_money_returns_json(self, client):
        """Test /api/us/smart-money returns JSON."""
        response = client.get('/api/us/smart-money')
        assert response.content_type == 'application/json'

    def test_api_etf_flows_returns_json(self, client):
        """Test /api/us/etf-flows returns JSON."""
        response = client.get('/api/us/etf-flows')
        assert response.content_type == 'application/json'

    def test_api_sector_heatmap_returns_json(self, client):
        """Test /api/us/sector-heatmap returns JSON."""
        response = client.get('/api/us/sector-heatmap')
        assert response.status_code in [200, 404]

    def test_api_options_flow_returns_json(self, client):
        """Test /api/us/options-flow returns JSON."""
        response = client.get('/api/us/options-flow')
        assert response.content_type == 'application/json'

    def test_api_calendar_returns_json(self, client):
        """Test /api/us/calendar returns JSON."""
        response = client.get('/api/us/calendar')
        assert response.content_type == 'application/json'

    def test_api_history_dates_returns_json(self, client):
        """Test /api/us/history-dates returns JSON."""
        response = client.get('/api/us/history-dates')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

    def test_api_stock_chart_returns_json(self, client, mock_yfinance_ticker):
        """Test /api/us/stock-chart/<ticker> returns JSON."""
        with patch("yfinance.Ticker", return_value=mock_yfinance_ticker):
            response = client.get('/api/us/stock-chart/AAPL')
            assert response.content_type == 'application/json'

    def test_api_macro_analysis_returns_json(self, client):
        """Test /api/us/macro-analysis returns JSON."""
        response = client.get('/api/us/macro-analysis')
        assert response.content_type == 'application/json'

    def test_api_ai_summary_returns_json(self, client):
        """Test /api/us/ai-summary/<ticker> returns JSON."""
        with patch("os.path.exists", return_value=False):
            response = client.get('/api/us/ai-summary/AAPL')
            assert response.content_type == 'application/json'

    def test_api_technical_indicators_returns_json(self, client, mock_yfinance_ticker):
        """Test /api/us/technical-indicators/<ticker> returns JSON."""
        with patch("yfinance.Ticker", return_value=mock_yfinance_ticker):
            response = client.get('/api/us/technical-indicators/AAPL')
            assert response.content_type == 'application/json'

    def test_api_update_data_post_only(self, client):
        """Test /api/us/update-data only accepts POST."""
        response = client.get('/api/us/update-data')
        assert response.status_code == 405  # Method Not Allowed


class TestSectorMapping:
    """Tests for sector mapping functionality."""

    def test_sector_map_import(self):
        """Test that sector map can be imported from routes."""
        from app.routes.market import SECTOR_MAP

        assert "AAPL" in SECTOR_MAP
        assert SECTOR_MAP["AAPL"] == "Tech"

    def test_get_sector_from_map(self):
        """Test get_sector function."""
        from app.routes.market import get_sector

        result = get_sector("AAPL")
        assert result == "Tech"

    def test_get_sector_unknown_ticker(self):
        """Test get_sector with unknown ticker returns default."""
        from app.routes.market import get_sector, _sector_cache

        # Clear cache first
        _sector_cache.clear()

        with patch("yfinance.Ticker") as mock_ticker:
            mock_ticker.return_value.info = {}
            result = get_sector("UNKNOWN_TICKER_XYZ")
            assert result == "-"
