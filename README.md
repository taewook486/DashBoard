# DashBoard - Smart Money Market Analysis System

**Advanced US Stock Market Analysis Platform with AI-Powered Insights**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/tests-111%20passed-success.svg)](https://github.com/taewook486/DashBoard)
[![Coverage](https://img.shields.io/badge/coverage-67%25-yellow.svg)](https://github.com/taewook486/DashBoard)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## Features

### Smart Money Screening (6-Factor Analysis)
- **Supply/Demand Analysis (25%)**: Volume accumulation patterns
- **Institutional Support (20%)**: 13F holdings tracking
- **Technical Indicators (20%)**: RSI, MACD, Bollinger Bands
- **Fundamental Analysis (15%)**: P/E, PEG ratios
- **Analyst Ratings (10%)**: Wall Street consensus
- **Relative Strength (10%)**: Performance vs S&P 500

### Real-Time Market Data
- **746,233** price records across **492 US stocks**
- 30-second live price updates
- Interactive candlestick charts with technical overlays
- Support/Resistance level detection

### AI-Powered Analysis
- **Google Gemini 3.0**: Macro economic analysis
- **OpenAI GPT-5.2**: Market insights and summaries
- Multi-language support (Korean/English)

### Technical Analysis
- RSI (14-period)
- MACD (12, 26, 9)
- Bollinger Bands (20, 2)
- Support/Resistance with 2% clustering

### Market Visualizations
- 11 major indices tracking
- Sector heatmap (11 sectors)
- ETF flows analysis (24 ETFs)
- Options flow monitoring
- Economic calendar integration

---

## Architecture

### Modular Structure (SPEC-IMPROVE-001)

The application has been refactored into a modular Flask Blueprint architecture:

```
app/
├── __init__.py           # Application factory
├── config.py             # Pydantic Settings configuration
├── models/
│   └── schemas.py        # Pydantic models for validation
├── routes/
│   ├── health.py         # Health check endpoints
│   └── market.py         # Market data endpoints
├── services/
│   ├── cache.py          # Caching service with TTL
│   └── market_data.py    # Market data business logic
└── utils/
    ├── decorators.py     # Request decorators
    ├── errors.py         # Custom error handlers
    ├── logging.py        # Structured logging
    └── validators.py     # Input validation
```

### Key Improvements

1. **Configuration Management**: Pydantic Settings with environment variable support
2. **Structured Logging**: JSON-formatted logs with Structlog
3. **Health Checks**: `/health` endpoint with component status
4. **Security**: Rate limiting, CORS, input validation
5. **Testing**: 111 tests with 67% coverage
6. **Docker Support**: Multi-stage Dockerfile for production
7. **CI/CD**: GitHub Actions pipeline with lint, test, and security scan

---

## Quick Start

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/taewook486/DashBoard.git
cd DashBoard
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
FRED_API_KEY=your_fred_api_key_here
DATA_DIR=./us_market/data
FLASK_ENV=development
LOG_LEVEL=INFO
```

5. **Run the application**
```bash
# Development mode
flask run --port=5001

# Or using the application factory
python -c "from app import create_app; app = create_app(); app.run(port=5001)"
```

6. **Access the application**
```
http://localhost:5001
```

---

## Docker Deployment

### Build and Run with Docker

```bash
# Build the image
docker build -t dashboard:latest .

# Run the container
docker run -p 5001:5001 --env-file .env dashboard:latest
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Testing

### Run All Tests

```bash
# Run all tests with coverage
pytest tests/ --cov=app --cov-report=term-missing -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage HTML report
pytest tests/ --cov=app --cov-report=html
```

### Test Coverage

- **Total Tests**: 111
- **Coverage**: 67%
- **Test Types**: Unit, Integration, Characterization

---

## API Endpoints

### Health Check

#### `GET /health`
Health check endpoint for monitoring.

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

### Market Data

#### `GET /`
Root endpoint - returns main dashboard HTML page.

#### `GET /api/us/indices`
Get major US stock indices data.

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
    }
  ]
}
```

#### `GET /api/us/smart-money`
Get smart money screened stocks with 6-factor scores.

**Query Parameters:**
- `limit` (optional): Number of results (default: 20)

#### `GET /api/us/etf-flows`
Get ETF capital flows data.

#### `GET /api/us/sector-heatmap`
Get sector performance heatmap data.

#### `GET /api/us/options-flow`
Get options flow monitoring data.

#### `GET /api/us/calendar`
Get economic calendar events.

#### `GET /api/us/history/dates`
Get available historical data dates.

### Stock Analysis

#### `GET /api/us/stock/chart`
Get stock chart data with technical indicators.

**Query Parameters:**
- `ticker` (required): Stock symbol (e.g., AAPL)
- `period` (optional): Time period - 1d, 5d, 1mo, 3mo, 6mo, 1y, max

#### `GET /api/us/technical-indicators/<ticker>`
Get technical indicators for a stock.

#### `GET /api/us/macro-analysis`
Get AI-powered macro economic analysis.

**Query Parameters:**
- `lang` (optional): Language - ko, en (default: ko)
- `model` (optional): AI model - gemini, openai (default: gemini)

#### `GET /api/us/ai-summary/<ticker>`
Get AI-powered stock summary.

**Query Parameters:**
- `lang` (optional): Language - ko, en (default: ko)

### Data Management

#### `POST /api/us/update-data`
Trigger data update for all market data.

**Response:**
```json
{
  "success": true,
  "message": "Data update initiated",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | development |
| `LOG_LEVEL` | Logging level | INFO |
| `PORT` | Application port | 5001 |
| `GOOGLE_API_KEY` | Google Gemini API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `FRED_API_KEY` | FRED API key | - |
| `DATA_DIR` | Data directory path | ./us_market/data |
| `CORS_ENABLED` | Enable CORS | True |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | True |
| `RATE_LIMIT_DEFAULT` | Default rate limit | 100 per minute |

### Pydantic Settings

Configuration is managed through `app/config.py` using Pydantic Settings:

```python
from app.config import Config

# Access configuration
config = Config()
api_key = config.GOOGLE_API_KEY
log_level = config.LOG_LEVEL
```

---

## Project Structure (Detailed)

```
DashBoard/
├── app/                          # Modular Flask application
│   ├── __init__.py               # Application factory
│   ├── config.py                 # Pydantic Settings
│   ├── models/                   # Pydantic models
│   │   └── schemas.py            # Request/response schemas
│   ├── routes/                   # Flask Blueprints
│   │   ├── health.py             # Health check endpoints
│   │   └── market.py             # Market data endpoints
│   ├── services/                 # Business logic
│   │   ├── cache.py              # Caching service
│   │   └── market_data.py        # Market data service
│   └── utils/                    # Utilities
│       ├── decorators.py         # Request decorators
│       ├── errors.py             # Error handlers
│       ├── logging.py            # Structured logging
│       └── validators.py         # Input validation
│
├── tests/                        # Test suite (111 tests)
│   ├── test_api.py               # API endpoint tests
│   ├── test_app_factory.py       # App factory tests
│   ├── test_characterization_api.py  # Characterization tests
│   ├── test_coverage.py          # Coverage tests
│   ├── test_routes.py            # Route tests
│   └── test_services.py          # Service tests
│
├── templates/                    # Frontend templates
│   └── index.html                # Main dashboard UI
│
├── static/                       # Static assets
│   ├── js/
│   │   └── app.js                # Frontend logic
│   └── css/
│       └── custom.css            # Custom styling
│
├── us_market/                    # Data collection scripts
│   ├── update_all.py             # Master update script
│   ├── create_us_daily_prices.py # Price data
│   ├── smart_money_screener_v2.py # Smart money screening
│   └── data/                     # CSV data files (gitignored)
│
├── .github/workflows/            # CI/CD pipelines
│   └── ci.yml                    # GitHub Actions workflow
│
├── Dockerfile                    # Multi-stage Docker build
├── docker-compose.yml            # Docker Compose configuration
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Project configuration
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

---

## Technology Stack

### Backend
- **Flask 2.3+**: REST API framework
- **Pydantic**: Data validation and settings
- **Structlog**: Structured JSON logging
- **yfinance**: Market data provider
- **pandas**: Data processing
- **numpy**: Numerical computing

### Security & Performance
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-Limiter**: Rate limiting
- **Gunicorn**: Production WSGI server

### Testing
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking support

### Deployment
- **Docker**: Containerization
- **GitHub Actions**: CI/CD pipeline
- **Render/Vercel**: Cloud hosting (optional)

### Frontend
- **Tailwind CSS**: Utility-first styling
- **Lightweight Charts**: Candlestick charts
- **Chart.js**: Data visualization
- **ApexCharts**: Heatmap visualization
- **jQuery**: DOM manipulation

---

## Development

### Code Quality

Run linting and formatting:
```bash
# Ruff linter
ruff check app/

# Ruff formatter
ruff format app/

# Type checking
mypy app/
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific test file
pytest tests/test_api.py -v

# Specific test
pytest tests/test_api.py::test_root_endpoint -v
```

### Adding New Features

1. **Create a new branch**
```bash
git checkout -b feature/new-feature
```

2. **Make changes and test**
```bash
pytest tests/ -v
```

3. **Commit with conventional commits**
```bash
git commit -m "feat: add new feature"
```

4. **Push and create PR**
```bash
git push origin feature/new-feature
```

---

## Deployment

### Render Deployment

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy automatically on push to main branch

### Docker Deployment

```bash
# Build image
docker build -t dashboard:latest .

# Run container
docker run -p 5001:5001 --env-file .env dashboard:latest
```

### Traditional Hosting

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=production
export PORT=5001

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5001 --workers 2 "app:create_app()"
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for public APIs
- Keep test coverage above 60%

---

## License

This project is licensed under the MIT License.

---

## Top Smart Money Picks (Current)

| Rank | Ticker | Grade | Score | Price |
|------|--------|-------|-------|-------|
| 1 | FITB | 🌟 A (Strong Buy) | 78.8 | $50.22 |
| 2 | FDX | 🌟 A (Strong Buy) | 78.0 | $322.25 |
| 3 | PPG | 🌟 A (Strong Buy) | 76.6 | $115.63 |
| 4 | NOC | 🌟 A (Strong Buy) | 76.6 | $692.26 |
| 5 | CMCSA | 🌟 A (Strong Buy) | 76.5 | $29.75 |

---

## Support

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for smart investors**

**@SPEC:IMPROVE-001** - Modular Architecture Refactoring
