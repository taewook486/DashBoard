# DashBoard API Documentation

**Base URL**: `http://localhost:5001`

**API Version**: v1.0

**Content Type**: `application/json`

---

## Overview

The DashBoard API provides comprehensive US stock market data, AI-powered analysis, and smart money screening capabilities. All endpoints return JSON responses with consistent structure.

## Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    // Response data here
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

---

## Authentication

Currently, the API does not require authentication. Rate limiting is applied per IP address (default: 100 requests per minute).

---

## Endpoints

### Health Check

#### `GET /health`

Check the health status of the API and its components.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "components": {
    "api": "healthy",
    "data": "healthy"
  }
}
```

**Status Codes:**
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is unhealthy

---

### Root Endpoint

#### `GET /`

Returns the main dashboard HTML page.

**Response:** HTML content

**Status Codes:**
- `200 OK`: Page loaded successfully

---

## Market Data Endpoints

### Get Major Indices

#### `GET /api/us/indices`

Get data for major US stock market indices.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "SPY",
      "name": "S&P 500",
      "price": 478.52,
      "change": 1.23,
      "change_percent": 0.26
    },
    {
      "symbol": "DIA",
      "name": "Dow Jones",
      "price": 378.45,
      "change": -0.56,
      "change_percent": -0.15
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Data retrieved successfully
- `500 Internal Server Error`: Server error

---

### Get Smart Money Screened Stocks

#### `GET /api/us/smart-money`

Get stocks screened using the 6-factor smart money analysis.

**Query Parameters:**
- `limit` (optional, integer): Number of results to return (default: 20, max: 100)

**Example Request:**
```
GET /api/us/smart-money?limit=10
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "price": 185.92,
      "score": 75.5,
      "grade": "A",
      "factors": {
        "supply_demand": 80,
        "institutional": 75,
        "technical": 70,
        "fundamental": 78,
        "analyst": 72,
        "relative_strength": 76
      }
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Data retrieved successfully
- `400 Bad Request`: Invalid limit parameter
- `500 Internal Server Error`: Server error

---

### Get ETF Flows

#### `GET /api/us/etf-flows`

Get capital flows for major ETFs.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "SPY",
      "name": "SPDR S&P 500",
      "flow": 1250000000,
      "flow_percent": 0.5
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Data retrieved successfully
- `500 Internal Server Error`: Server error

---

### Get Sector Heatmap

#### `GET /api/us/sector-heatmap`

Get sector performance heatmap data.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "sector": "Technology",
      "change_percent": 1.5,
      "stocks": [
        {"ticker": "AAPL", "change": 2.3},
        {"ticker": "MSFT", "change": 1.8}
      ]
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Data retrieved successfully
- `500 Internal Server Error`: Server error

---

### Get Options Flow

#### `GET /api/us/options-flow`

Get options flow monitoring data.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "call_volume": 150000,
      "put_volume": 90000,
      "put_call_ratio": 0.6
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Data retrieved successfully
- `500 Internal Server Error`: Server error

---

### Get Economic Calendar

#### `GET /api/us/calendar`

Get upcoming economic calendar events.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-01-18",
      "event": "CPI Release",
      "importance": "high",
      "actual": null,
      "forecast": "3.2%",
      "previous": "3.1%"
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Data retrieved successfully
- `500 Internal Server Error`: Server error

---

### Get Historical Data Dates

#### `GET /api/us/history/dates`

Get available dates for historical data.

**Response:**
```json
{
  "success": true,
  "data": {
    "dates": [
      "2025-01-14",
      "2025-01-13",
      "2025-01-12"
    ],
    "latest": "2025-01-14",
    "count": 252
  }
}
```

**Status Codes:**
- `200 OK`: Data retrieved successfully
- `500 Internal Server Error`: Server error

---

## Stock Analysis Endpoints

### Get Stock Chart Data

#### `GET /api/us/stock/chart`

Get historical price data and technical indicators for a stock.

**Query Parameters:**
- `ticker` (required, string): Stock symbol (e.g., AAPL, MSFT)
- `period` (optional, string): Time period
  - `1d` - 1 day
  - `5d` - 5 days
  - `1mo` - 1 month
  - `3mo` - 3 months
  - `6mo` - 6 months
  - `1y` - 1 year
  - `max` - All available data
  - Default: `1mo`

**Example Request:**
```
GET /api/us/stock/chart?ticker=AAPL&period=1mo
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "period": "1mo",
    "prices": [
      {
        "date": "2025-01-15",
        "open": 185.00,
        "high": 186.50,
        "low": 184.20,
        "close": 185.92,
        "volume": 50000000
      }
    ],
    "technical_indicators": {
      "rsi": 65.5,
      "macd": {
        "value": 1.2,
        "signal": 1.0,
        "histogram": 0.2
      },
      "bollinger_bands": {
        "upper": 188.50,
        "middle": 185.00,
        "lower": 181.50
      }
    }
  }
}
```

**Status Codes:**
- `200 OK`: Data retrieved successfully
- `400 Bad Request`: Invalid ticker or period
- `404 Not Found`: Ticker not found
- `500 Internal Server Error`: Server error

---

### Get Technical Indicators

#### `GET /api/us/technical-indicators/{ticker}`

Get technical indicators for a specific stock.

**URL Parameters:**
- `ticker` (required, string): Stock symbol

**Example Request:**
```
GET /api/us/technical-indicators/AAPL
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "price": 185.92,
    "indicators": {
      "rsi": {
        "value": 65.5,
        "signal": "neutral"
      },
      "macd": {
        "value": 1.2,
        "signal": 1.0,
        "histogram": 0.2,
        "signal": "bullish"
      },
      "bollinger_bands": {
        "upper": 188.50,
        "middle": 185.00,
        "lower": 181.50,
        "width": 3.8
      },
      "support_resistance": {
        "support": [180.00, 175.50],
        "resistance": [190.00, 195.50]
      }
    }
  }
}
```

**Status Codes:**
- `200 OK`: Data retrieved successfully
- `404 Not Found`: Ticker not found
- `500 Internal Server Error`: Server error

---

### Get Macro Analysis

#### `GET /api/us/macro-analysis`

Get AI-powered macro economic analysis.

**Query Parameters:**
- `lang` (optional, string): Language for response
  - `ko` - Korean (default)
  - `en` - English
- `model` (optional, string): AI model to use
  - `gemini` - Google Gemini (default)
  - `openai` - OpenAI GPT

**Example Request:**
```
GET /api/us/macro-analysis?lang=en&model=gemini
```

**Response:**
```json
{
  "success": true,
  "data": {
    "model": "gemini",
    "language": "en",
    "analysis": "The US economy shows signs of moderate growth...",
    "indicators": {
      "gdp_growth": "2.5%",
      "inflation": "3.2%",
      "unemployment": "3.7%"
    },
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

**Status Codes:**
- `200 OK`: Analysis generated successfully
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: AI service error

---

### Get AI Stock Summary

#### `GET /api/us/ai-summary/{ticker}`

Get AI-powered stock summary.

**URL Parameters:**
- `ticker` (required, string): Stock symbol

**Query Parameters:**
- `lang` (optional, string): Language for response
  - `ko` - Korean (default)
  - `en` - English

**Example Request:**
```
GET /api/us/ai-summary/AAPL?lang=en
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "language": "en",
    "summary": "Apple Inc. continues to show strong performance...",
    "key_points": [
      "Strong Q4 earnings beat expectations",
      "iPhone 15 sales exceeding projections"
    ],
    "sentiment": "bullish",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

**Status Codes:**
- `200 OK`: Summary generated successfully
- `404 Not Found`: Ticker not found
- `500 Internal Server Error`: AI service error

---

## Data Management Endpoints

### Update Market Data

#### `POST /api/us/update-data`

Trigger an update of all market data.

**Request Body:**
```json
{
  "force": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Data update initiated",
  "timestamp": "2025-01-15T10:30:00Z",
  "status": "processing"
}
```

**Status Codes:**
- `200 OK`: Update initiated successfully
- `405 Method Not Allowed`: Non-POST request
- `500 Internal Server Error`: Server error

---

## Error Handling

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `NOT_FOUND` | Resource not found |
| `RATE_LIMITED` | Too many requests |
| `API_ERROR` | Internal API error |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid ticker symbol",
    "details": {
      "field": "ticker",
      "value": "INVALID@#"
    }
  }
}
```

---

## Rate Limiting

- **Default Limit**: 100 requests per minute per IP
- **Headers**:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset time (Unix timestamp)

### Rate Limit Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded. Try again in 60 seconds."
  }
}
```

---

## CORS

Cross-Origin Resource Sharing (CORS) is enabled by default.

**Allowed Origins**: Configured via `ALLOWED_ORIGINS` environment variable

**Allowed Methods**: GET, POST, OPTIONS

**Allowed Headers**: Content-Type, Authorization

---

## Caching

Some endpoints use caching to improve performance:

- **Cache Duration**: 5 minutes (300 seconds) by default
- **Cache Key**: Based on endpoint and parameters
- **Cache Headers**:
  - `X-Cache`: `HIT` or `MISS`
  - `X-Cache-Expiry`: Expiry timestamp

---

## SDK Examples

### Python

```python
import requests

BASE_URL = "http://localhost:5001"

# Get indices
response = requests.get(f"{BASE_URL}/api/us/indices")
data = response.json()

# Get stock chart
params = {"ticker": "AAPL", "period": "1mo"}
response = requests.get(f"{BASE_URL}/api/us/stock/chart", params=params)
data = response.json()
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:5001";

// Get indices
fetch(`${BASE_URL}/api/us/indices`)
  .then(response => response.json())
  .then(data => console.log(data));

// Get stock chart
const params = new URLSearchParams({
  ticker: "AAPL",
  period: "1mo"
});

fetch(`${BASE_URL}/api/us/stock/chart?${params}`)
  .then(response => response.json())
  .then(data => console.log(data));
```

### cURL

```bash
# Get indices
curl http://localhost:5001/api/us/indices

# Get stock chart
curl "http://localhost:5001/api/us/stock/chart?ticker=AAPL&period=1mo"

# Update data
curl -X POST http://localhost:5001/api/us/update-data
```

---

## Changelog

### v1.0.0 (2025-01-15)
- Initial API release
- 13 core endpoints
- Smart money screening
- AI-powered analysis
- Real-time market data

### v1.1.0 (2026-02-25) - SPEC-IMPROVE-001
- Modular Blueprint architecture
- Enhanced error handling
- Rate limiting
- CORS support
- Health check endpoint
- Structured logging
- 111 tests with 67% coverage

---

## Support

For API issues or questions, please open an issue on GitHub.

---

**@SPEC:IMPROVE-001** - Modular Architecture Refactoring
