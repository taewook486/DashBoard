# DashBoard Architecture Documentation

**@SPEC:IMPROVE-001** - Modular architecture overview and design decisions

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Design Principles](#design-principles)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Security Architecture](#security-architecture)
6. [Scaling Strategy](#scaling-strategy)

---

## Architecture Overview

### High-Level Architecture

The DashBoard application follows a **modular monolithic architecture** using Flask Blueprints for separation of concerns.

```mermaid
graph TB
    Client[Client Browser]

    subgraph "Load Balancer / Reverse Proxy"
        LB[Nginx / Caddy]
    end

    subgraph "Application Layer"
        App[Flask App Factory]

        subgraph "Blueprints"
            Health[Health Blueprint]
            Market[Market Blueprint]
        end

        subgraph "Services Layer"
            Cache[Cache Service]
            MarketData[Market Data Service]
        end

        subgraph "Utilities"
            Logging[Structured Logging]
            Validators[Input Validators]
            Errors[Error Handlers]
        end
    end

    subgraph "Data Layer"
        Files[CSV Files]
        CacheStore[In-Memory Cache]
    end

    subgraph "External Services"
        Gemini[Google Gemini API]
        OpenAI[OpenAI API]
        YFinance[YFinance API]
    end

    Client --> LB
    LB --> App
    App --> Health
    App --> Market
    Market --> Cache
    Market --> MarketData
    MarketData --> Files
    MarketData --> YFinance
    Market --> Gemini
    Market --> OpenAI
    Cache --> CacheStore

    App --> Logging
    App --> Validators
    App --> Errors
```

---

## Design Principles

### 1. Separation of Concerns

Each module has a single responsibility:

- **Routes (`app/routes/`)**: HTTP request handling
- **Services (`app/services/`)**: Business logic
- **Utils (`app/utils/`)**: Shared utilities
- **Models (`app/models/`)**: Data validation

### 2. Dependency Injection

Services are injected into routes, not instantiated directly:

```python
# Good: Service dependency
from app.services.market_data import market_data_service

# Routes use the service, not create it
@market_bp.route('/api/us/indices')
def get_indices():
    return market_data_service.get_index_data()
```

### 3. Configuration Management

Centralized configuration via Pydantic Settings:

```python
from app.config import Config

config = Config()
api_key = config.GOOGLE_API_KEY
```

### 4. Error Handling

Consistent error responses across all endpoints:

```python
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

### 5. Logging Strategy

Structured JSON logging for better observability:

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "info",
  "event": "api_request",
  "endpoint": "/api/us/indices",
  "duration_ms": 45
}
```

---

## Component Architecture

### Application Factory Pattern

The application uses the factory pattern for flexibility:

```mermaid
graph LR
    A[create_app] --> B[Load Config]
    B --> C[Configure Logging]
    C --> D[Init Extensions]
    D --> E[Register Blueprints]
    E --> F[Register Health Check]
    F --> G[Return App]
```

**Benefits:**
- Multiple app instances (testing, production)
- Easy configuration switching
- Extension initialization control

### Blueprint Structure

```mermaid
graph TB
    subgraph "Health Blueprint"
        H1[GET /health]
        H2[Component Status Check]
    end

    subgraph "Market Blueprint"
        M1[GET / - Root]
        M2[GET /api/us/indices]
        M3[GET /api/us/smart-money]
        M4[GET /api/us/etf-flows]
        M5[GET /api/us/sector-heatmap]
        M6[GET /api/us/options-flow]
        M7[GET /api/us/calendar]
        M8[GET /api/us/history/dates]
        M9[GET /api/us/stock/chart]
        M10[GET /api/us/technical-indicators]
        M11[GET /api/us/macro-analysis]
        M12[GET /api/us/ai-summary]
        M13[POST /api/us/update-data]
    end
```

### Service Layer Architecture

```mermaid
graph TB
    subgraph "Cache Service"
        CS1[cache.get]
        CS2[cache.set]
        CS3[cache.delete]
        CS4[cache.clear]
        CS5[@cached decorator]
    end

    subgraph "Market Data Service"
        MDS1[get_ticker_data]
        MDS2[get_index_data]
        MDS3[get_sector_info]
        MDS4[get_etf_flows]
        MDS5[calculate_technical_indicators]
    end

    CS5 -.-> MDS1
    CS5 -.-> MDS2
    CS5 -.-> MDS3
```

**Cache Service Features:**
- In-memory storage with TTL
- Thread-safe operations
- Decorator-based caching
- Automatic cleanup

**Market Data Service Features:**
- CSV file parsing
- Technical indicator calculation
- Sector mapping
- Fallback mechanisms

### Utility Modules

```mermaid
graph TB
    subgraph "Logging Utility"
        LU1[configure_logging]
        LU2[get_logger]
        LU3[log_request]
        LU4[log_exception]
    end

    subgraph "Validators Utility"
        VU1[validate_ticker]
        VU2[validate_period]
        VU3[validate_chart_request]
        VU4[validate_ai_summary_request]
    end

    subgraph "Errors Utility"
        EU1[DashboardError]
        EU2[NotFoundError]
        EU3[ValidationError]
        EU4[RateLimitedError]
        EU5[APIError]
    end

    subgraph "Decorators Utility"
        DU1[@validate_ticker_param]
        DU2[@log_request]
    end
```

---

## Data Flow

### Request Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Reverse Proxy
    participant F as Flask App
    participant B as Blueprint
    participant S as Service
    participant D as Data Layer
    participant E as External API

    C->>R: HTTP Request
    R->>F: Forward Request
    F->>B: Route to Blueprint
    B->>B: Validate Input
    B->>S: Call Service
    S->>D: Read Data
    D-->>S: Return Data
    S->>S: Process Data
    S-->>B: Return Result
    B->>B: Format Response
    B-->>F: Return Response
    F-->>R: HTTP Response
    R-->>C: Send Response

    Note over S,E: For AI features
    S->>E: API Request
    E-->>S: AI Response
```

### Caching Flow

```mermaid
graph TB
    A[Request] --> B{Cache Hit?}
    B -->|Yes| C[Return Cached Data]
    B -->|No| D[Fetch from Source]
    D --> E[Process Data]
    E --> F[Store in Cache]
    F --> G[Return Data]
    C --> H[Response]
    G --> H

    style C fill:#90EE90
    style H fill:#90EE90
```

### Error Handling Flow

```mermaid
graph TB
    A[Request] --> B{Validation}
    B -->|Fail| C[ValidationError]
    B -->|Pass| D{Processing}
    D -->|Error| E[Service Error]
    D -->|Success| F[Response]
    C --> G[Error Handler]
    E --> G
    G --> H[JSON Error Response]
    F --> I[JSON Success Response]
```

---

## Security Architecture

### Security Layers

```mermaid
graph TB
    subgraph "Layer 1: Network Security"
        NS1[HTTPS/TLS]
        NS2[Firewall Rules]
    end

    subgraph "Layer 2: Application Security"
        AS1[CORS Policy]
        AS2[Rate Limiting]
        AS3[Input Validation]
    end

    subgraph "Layer 3: Data Security"
        DS1[Environment Variables]
        DS2[No Secrets in Code]
        DS3[Secure Logging]
    end

    subgraph "Layer 4: API Security"
        API1[Error Handling]
        API2[Rate Limiting]
        API3[Input Sanitization]
    end
```

### Rate Limiting Strategy

```mermaid
graph LR
    A[Request] --> B{Rate Limit Check}
    B -->|Under Limit| C[Process Request]
    B -->|Over Limit| D[Return 429]
    C --> E[Update Counter]
    E --> F[Response]

    style D fill:#FFB6C1
    style C fill:#90EE90
    style F fill:#90EE90
```

### CORS Configuration

```mermaid
graph TB
    A[Incoming Request] --> B{Origin Check}
    B -->|Allowed| C[Process Request]
    B -->|Blocked| D[Return 403]
    C --> E[Add CORS Headers]
    E --> F[Response]

    style D fill:#FFB6C1
    style C fill:#90EE90
```

---

## Scaling Strategy

### Horizontal Scaling

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx / HAProxy]
    end

    subgraph "Application Instances"
        A1[App Instance 1]
        A2[App Instance 2]
        A3[App Instance 3]
    end

    subgraph "Shared Storage"
        FS[Shared File System]
        R[Redis Cache - Optional]
    end

    LB --> A1
    LB --> A2
    LB --> A3

    A1 --> FS
    A2 --> FS
    A3 --> FS

    A1 -.-> R
    A2 -.-> R
    A3 -.-> R
```

### Vertical Scaling

**Current Configuration:**
- Workers: 2
- Threads per worker: 4
- Total concurrent requests: 8

**Scaling Up:**
- Increase workers (CPU cores)
- Increase threads (I/O bound)
- Add more memory

### Caching Strategy

```mermaid
graph TB
    subgraph "Level 1: In-Memory Cache"
        L1[Local Cache]
    end

    subgraph "Level 2: Redis Cache - Future"
        L2[Redis Cluster]
    end

    subgraph "Level 3: CDN - Future"
        L3[Cloudflare CDN]
    end

    A[Request] --> L1
    L1 -->|Miss| L2
    L2 -->|Miss| L3
    L3 -->|Miss| D[Database/API]

    style L1 fill:#90EE90
    style L2 fill:#FFD700
    style L3 fill:#87CEEB
```

---

## Technology Stack

### Backend

| Component | Technology | Version |
|-----------|-----------|---------|
| Web Framework | Flask | 2.3+ |
| WSGI Server | Gunicorn | Latest |
| Data Validation | Pydantic | 2.x |
| Logging | Structlog | Latest |
| Data Processing | pandas | Latest |
| Numerical Computing | numpy | Latest |

### Security

| Component | Technology | Purpose |
|-----------|-----------|---------|
| CORS | Flask-CORS | Cross-origin requests |
| Rate Limiting | Flask-Limiter | DDoS protection |
| Validation | Pydantic | Input validation |

### Testing

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Testing Framework | pytest | Unit/integration tests |
| Coverage | pytest-cov | Code coverage |
| Mocking | pytest-mock | Mock external services |

### Deployment

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containerization | Docker | Image building |
| Orchestration | Docker Compose | Local deployment |
| CI/CD | GitHub Actions | Automated testing |
| Hosting | Render/Vercel | Cloud deployment |

---

## File Structure

```
app/
├── __init__.py              # Application factory
├── config.py                # Pydantic Settings
├── models/
│   └── schemas.py           # Pydantic models
├── routes/
│   ├── __init__.py
│   ├── health.py            # Health check endpoints
│   └── market.py            # Market data endpoints
├── services/
│   ├── __init__.py
│   ├── cache.py             # Caching service
│   └── market_data.py       # Market data service
└── utils/
    ├── __init__.py
    ├── decorators.py        # Request decorators
    ├── errors.py            # Error handlers
    ├── logging.py           # Structured logging
    └── validators.py        # Input validation
```

---

## Design Decisions

### Why Flask Blueprint?

**Pros:**
- Modular route organization
- Easy to add new features
- Clear separation of concerns
- Testable components

**Cons:**
- More files than monolithic approach
- Slightly more complex setup

**Decision:** Blueprint architecture chosen for better maintainability and scalability.

### Why Pydantic Settings?

**Pros:**
- Type-safe configuration
- Environment variable validation
- Default values support
- IDE autocompletion

**Cons:**
- Additional dependency
- Learning curve

**Decision:** Pydantic provides robust configuration management with type safety.

### Why Structured Logging?

**Pros:**
- JSON format for parsing
- Better observability
- Easier debugging
- Tool integration

**Cons:**
- Less human-readable
- Requires log aggregators

**Decision:** Structured logging essential for production debugging and monitoring.

### Why In-Memory Cache?

**Pros:**
- Fast access
- Simple implementation
- No external dependencies

**Cons:**
- Not shared across instances
- Lost on restart
- Limited memory

**Decision:** Suitable for single-instance deployment. Can upgrade to Redis for scaling.

---

## Future Improvements

### Phase 2 Enhancements

1. **Redis Cache**: Shared cache across instances
2. **Database**: PostgreSQL for persistent storage
3. **Message Queue**: Celery for async tasks
4. **Monitoring**: Prometheus + Grafana
5. **Tracing**: OpenTelemetry integration

### Phase 3 Enhancements

1. **Microservices**: Split into separate services
2. **Event Sourcing**: Event-driven architecture
3. **CQRS**: Command Query Responsibility Segregation
4. **gRPC**: Internal service communication

---

## References

- [Flask Blueprint Documentation](https://flask.palletsprojects.com/en/2.3.x/blueprints/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Structlog](https://www.structlog.org/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

---

**@SPEC:IMPROVE-001** - Modular Architecture Refactoring
