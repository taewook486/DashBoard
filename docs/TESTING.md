# DashBoard Testing Documentation

**@SPEC:IMPROVE-001** - Testing strategy and guidelines

---

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Coverage](#test-coverage)
5. [Writing Tests](#writing-tests)
6. [Test Types](#test-types)

---

## Testing Overview

### Test Statistics

- **Total Tests**: 111
- **Code Coverage**: 67%
- **Test Files**: 6
- **Test Duration**: ~15 seconds

### Test Categories

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **Characterization Tests**: Capture existing behavior
4. **Edge Case Tests**: Test boundary conditions

---

## Test Structure

### Test File Organization

```
tests/
├── test_api.py                    # API endpoint tests (15 tests)
├── test_app_factory.py            # Application factory tests (23 tests)
├── test_characterization_api.py   # Characterization tests (26 tests)
├── test_coverage.py               # Coverage tests (28 tests)
├── test_routes.py                 # Route tests (17 tests)
└── test_services.py               # Service tests (7 tests)
```

### Test File Descriptions

#### test_api.py
Tests for API endpoints:
- Root endpoint
- Market data endpoints
- Smart money screening
- ETF flows
- Sector heatmap
- Options flow
- Calendar
- History dates

#### test_app_factory.py
Tests for application factory:
- App creation
- Configuration loading
- Logging setup
- Error handling
- Validators

#### test_characterization_api.py
Characterization tests for existing behavior:
- Root endpoint behavior
- API response structures
- Error handling patterns
- File not found scenarios

#### test_coverage.py
Coverage tests for:
- Pydantic models
- Decorators
- Error handling
- Cache edge cases
- Market data service edge cases

#### test_routes.py
Route-specific tests:
- Health endpoints
- Market endpoints
- Sector mapping
- Services

#### test_services.py
Service layer tests:
- Cache operations
- Market data retrieval
- Data processing

---

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=term-missing -v
```

### Run Specific Test File

```bash
pytest tests/test_api.py -v
```

### Run Specific Test

```bash
pytest tests/test_api.py::test_root_endpoint -v
```

### Run with HTML Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Run Failed Tests Only

```bash
pytest tests/ --lf
```

### Run with Verbose Output

```bash
pytest tests/ -vv -s
```

---

## Test Coverage

### Coverage Report

```
Name                          Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------------------------
app\__init__.py                  35      0      6      2    95%
app\config.py                    78     14      6      0    81%
app\models\schemas.py            78      3      6      3    93%
app\routes\health.py              8      0      0      0   100%
app\routes\market.py            440    200    126     25    51%
app\services\cache.py            80      6     16      2    92%
app\services\market_data.py      85     28     20      2    62%
app\utils\decorators.py          39     16      6      1    53%
app\utils\errors.py              64      2     20     10    86%
app\utils\logging.py             46     13     10      4    66%
app\utils\validators.py          63      6      8      2    86%
-------------------------------------------------------------------------
TOTAL                          1027    288    224     51    67%
```

### Coverage Goals

| Component | Current | Target | Priority |
|-----------|---------|--------|----------|
| Routes | 51% | 80% | High |
| Services | 62-92% | 85% | High |
| Utils | 53-86% | 80% | Medium |
| Config | 81% | 90% | Low |

---

## Writing Tests

### Test Structure Template

```python
import pytest
from app import create_app
from app.services.cache import cache_service

class TestFeature:
    """Test suite for feature X."""

    @pytest.fixture
    def app(self):
        """Create test application instance."""
        app = create_app()
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_specific_behavior(self, client):
        """Test specific behavior."""
        # Arrange
        expected_value = "result"

        # Act
        response = client.get('/api/endpoint')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
```

### Best Practices

1. **AAA Pattern**: Arrange, Act, Assert
2. **Descriptive Names**: Test names should describe what they test
3. **One Assertion**: Focus on one behavior per test
4. **Fixtures**: Use fixtures for common setup
5. **Mocks**: Mock external dependencies

### Example Tests

#### Unit Test

```python
def test_cache_set_and_get():
    """Test cache set and get operations."""
    # Arrange
    key = "test_key"
    value = {"data": "test_value"}

    # Act
    cache_service.set(key, value, ttl=60)
    result = cache_service.get(key)

    # Assert
    assert result == value
```

#### Integration Test

```python
def test_api_indices_returns_json(client):
    """Test /api/us/indices returns JSON data."""
    # Act
    response = client.get('/api/us/indices')

    # Assert
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = response.get_json()
    assert 'success' in data
    assert data['success'] is True
```

#### Characterization Test

```python
def test_characterize_root_returns_html():
    """Characterize root endpoint returns HTML."""
    # Act
    response = client.get('/')

    # Assert
    assert response.status_code == 200
    assert response.content_type.startswith('text/html')
    assert b'DashBoard' in response.data
```

---

## Test Types

### Unit Tests

Test individual functions and classes in isolation.

**Example**: Cache service operations

```python
def test_cache_set_and_get():
    """Test cache set and get operations."""
    cache_service.set("key", "value", ttl=60)
    assert cache_service.get("key") == "value"
```

### Integration Tests

Test how multiple components work together.

**Example**: API endpoint with cache

```python
def test_api_indices_uses_cache(client, monkeypatch):
    """Test API endpoint uses cache."""
    # Mock cache
    mock_data = {"data": "cached"}
    monkeypatch.setattr(cache_service, 'get', lambda x: mock_data)

    response = client.get('/api/us/indices')

    assert response.get_json() == mock_data
```

### Characterization Tests

Capture and verify existing behavior.

**Purpose**:
- Document current behavior
- Prevent regressions
- Refactor safely

**Example**:

```python
def test_characterize_indices_structure():
    """Characterize indices response structure."""
    response = client.get('/api/us/indices')
    data = response.get_json()

    # Verify structure (not values)
    assert 'success' in data
    assert 'data' in data
    assert isinstance(data['data'], list)
```

### Edge Case Tests

Test boundary conditions and error scenarios.

**Examples**:

```python
def test_validate_ticker_invalid():
    """Test ticker validation with invalid input."""
    result = validate_ticker("INVALID@#")
    assert result is False

def test_cache_miss():
    """Test cache returns None for missing key."""
    result = cache_service.get("nonexistent")
    assert result is None
```

---

## Test Fixtures

### Common Fixtures

```python
@pytest.fixture
def app():
    """Create test application."""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()
```

### Custom Fixtures

```python
@pytest.fixture
def sample_market_data():
    """Provide sample market data."""
    return {
        "symbol": "AAPL",
        "price": 185.92,
        "change": 1.23
    }

@pytest.fixture
def mock_cache(monkeypatch):
    """Mock cache service."""
    mock_data = {}
    monkeypatch.setattr(
        cache_service,
        'get',
        lambda x: mock_data.get(x)
    )
    monkeypatch.setattr(
        cache_service,
        'set',
        lambda k, v, ttl: mock_data.update({k: v})
    )
    return mock_data
```

---

## Mocking

### Mock External Services

```python
from unittest.mock import patch, MagicMock

def test_with_mocked_api():
    """Test with mocked external API."""
    with patch('app.services.market_data.requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"data": "test"}

        result = market_data_service.fetch_data()

        assert result == {"data": "test"}
        mock_get.assert_called_once()
```

### Mock File Operations

```python
def test_with_mocked_file(monkeypatch):
    """Test with mocked file read."""
    mock_data = "file,content"

    with monkeypatch.context() as m:
        m.setattr('builtins.open', lambda x: StringIO(mock_data))

        result = read_file("test.csv")

        assert result == "file,content"
```

---

## Pytest Configuration

### pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-report=html"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests"
]
```

### Running Marked Tests

```bash
# Run only unit tests
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration

# Skip slow tests
pytest tests/ -m "not slow"
```

---

## Continuous Integration

### GitHub Actions Workflow

The project uses GitHub Actions for CI/CD:

```yaml
test:
  name: Test (Python ${{ matrix.python }})
  runs-on: ubuntu-latest
  strategy:
    matrix:
      python: ['3.10', '3.11', '3.12']

  steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python }}

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-mock

    - name: Run tests
      run: |
        pytest tests/ --cov=app --cov-report=xml --cov-report=term-missing -v

    - name: Upload coverage
      uses: codecov/codecov-action@v4
```

### Test Matrix

Tests run on:
- Python 3.10
- Python 3.11
- Python 3.12

---

## Debugging Tests

### Debug with PDB

```bash
# Run tests with debugger
pytest tests/ --pdb

# Drop into debugger on failure
pytest tests/ --pdb-trace
```

### Print Debugging

```bash
# Show print statements
pytest tests/ -s
```

### Verbose Output

```bash
# Show detailed test output
pytest tests/ -vv
```

---

## Test Maintenance

### When Tests Fail

1. **Identify the Issue**: Read error message carefully
2. **Isolate the Test**: Run the specific failing test
3. **Debug**: Use pdb or print statements
4. **Fix**: Fix the code or update the test
5. **Verify**: Run all tests to ensure no regressions

### Updating Tests

When changing code:
1. Update related tests
2. Add new tests for new features
3. Remove obsolete tests
4. Verify coverage hasn't decreased

### Test Smells

**Warning Signs**:
- Fragile tests (break often)
- Slow tests (take too long)
- Complex tests (hard to understand)
- Duplicated code in tests

**Solutions**:
- Use fixtures for setup
- Mock external dependencies
- Keep tests simple and focused
- Extract common patterns

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Coverage](https://pytest-cov.readthedocs.io/)
- [Pytest Mock](https://pytest-mock.readthedocs.io/)

---

**@SPEC:IMPROVE-001** - Modular Architecture Refactoring
