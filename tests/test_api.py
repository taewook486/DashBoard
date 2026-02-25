"""
Basic API Tests for DashBoard Flask Application
"""

import pytest
from flask_app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200


def test_api_indices(client):
    """Test /api/us/indices endpoint"""
    response = client.get("/api/us/indices")
    # Returns JSON data
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_api_smart_money(client):
    """Test /api/us/smart-money endpoint"""
    response = client.get("/api/us/smart-money")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_api_etf_flows(client):
    """Test /api/us/etf-flows endpoint"""
    response = client.get("/api/us/etf-flows")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_api_sector_heatmap(client):
    """Test /api/us/sector-heatmap endpoint
    @SPEC:IMPROVE-001
    Note: Returns 404 when data file not found (current behavior)
    """
    response = client.get("/api/us/sector-heatmap")
    # Current behavior: Returns 404 when sector_heatmap.json not found
    # Returns JSON error response on 404
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.content_type == "application/json"


def test_api_options_flow(client):
    """Test /api/us/options-flow endpoint"""
    response = client.get("/api/us/options-flow")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_api_calendar(client):
    """Test /api/us/calendar endpoint"""
    response = client.get("/api/us/calendar")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_api_history_dates(client):
    """Test /api/us/history-dates endpoint"""
    response = client.get("/api/us/history-dates")
    assert response.status_code == 200
    assert response.content_type == "application/json"
