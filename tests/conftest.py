"""
Pytest fixtures and configuration for DashBoard tests.
@SPEC:IMPROVE-001
"""

import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app():
    """Create Flask app for testing using the new app factory."""
    # Set testing environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['SECRET_KEY'] = 'test-secret-key'

    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    yield app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the Flask app."""
    return app.test_cli_runner()


@pytest.fixture
def mock_yfinance_ticker(mocker):
    """Mock yfinance Ticker for testing without network calls."""
    mock_ticker = mocker.MagicMock()
    mock_hist = mocker.MagicMock()
    mock_hist.empty = False
    mock_hist.__len__ = lambda self: 5
    mock_hist.__getitem__ = lambda self, key: {
        "Close": [100.0, 101.0, 102.0, 103.0, 104.0],
        "Open": [99.0, 100.0, 101.0, 102.0, 103.0],
        "High": [101.0, 102.0, 103.0, 104.0, 105.0],
        "Low": [98.0, 99.0, 100.0, 101.0, 102.0],
    }.get(key, [])
    mock_hist.iloc = mocker.MagicMock()
    mock_hist.iloc.__getitem__ = lambda self, idx: mocker.MagicMock(
        Close=104.0 - idx,
        Open=103.0 - idx,
        High=105.0 - idx,
        Low=102.0 - idx
    )
    mock_ticker.history.return_value = mock_hist
    mock_ticker.info = {"sector": "Technology"}
    return mock_ticker


@pytest.fixture
def sample_market_indices():
    """Sample market indices response data."""
    return {
        "market_indices": [
            {
                "name": "S&P 500",
                "price": "5,000.00",
                "change": "50.00",
                "change_pct": 1.0,
                "color": "green",
            }
        ],
        "top_holdings": [],
        "style_box": {},
    }


@pytest.fixture
def sample_smart_money_data():
    """Sample smart money picks data."""
    return {
        "analysis_date": "2026-02-25",
        "analysis_timestamp": "2026-02-25T10:00:00",
        "top_picks": [
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "sector": "Tech",
                "final_score": 85.5,
                "current_price": 180.0,
                "price_at_rec": 175.0,
                "change_since_rec": 2.86,
            }
        ],
        "summary": {"total_analyzed": 1, "avg_score": 85.5},
    }


@pytest.fixture
def sample_etf_flows_data():
    """Sample ETF flows data."""
    return {
        "market_sentiment_score": 65.0,
        "sector_flows": [],
        "top_inflows": [],
        "top_outflows": [],
        "all_etfs": [],
        "ai_analysis": "Sample AI analysis text",
    }


@pytest.fixture
def sample_sector_heatmap_data():
    """Sample sector heatmap data."""
    return {
        "sectors": [
            {"name": "Technology", "change": 2.5, "volume": 1000000},
            {"name": "Healthcare", "change": -1.2, "volume": 500000},
        ]
    }


@pytest.fixture
def sample_options_flow_data():
    """Sample options flow data."""
    return {
        "flow_data": [
            {"ticker": "AAPL", "call_volume": 10000, "put_volume": 5000}
        ]
    }


@pytest.fixture
def sample_calendar_data():
    """Sample economic calendar data."""
    return {
        "events": [
            {
                "date": "2026-02-25",
                "event": "Fed Meeting",
                "impact": "High",
            }
        ]
    }
