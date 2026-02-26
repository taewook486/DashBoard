# DashBoard 프로젝트 구조 (Project Structure)

**모듈형 Flask 아키텍처 (Modular Flask Architecture)**

---

## 디렉터리 구조 (Directory Structure)

```
DashBoard/
├── app/                              # Flask 애플리케이션 (Modular Architecture)
│   ├── __init__.py                   # Application Factory Pattern
│   ├── config.py                     # Pydantic Settings Configuration
│   │
│   ├── models/                       # Pydantic 데이터 모델
│   │   ├── __init__.py
│   │   └── schemas.py                # Request/Response 스키마
│   │
│   ├── routes/                       # Flask Blueprint 라우트
│   │   ├── __init__.py
│   │   ├── health.py                 # Health Check 엔드포인트
│   │   └── market.py                 # Market Data 엔드포인트
│   │
│   ├── services/                     # 비즈니스 로직 계층
│   │   ├── __init__.py
│   │   ├── cache.py                  # 캐싱 서비스 (TTL 기반)
│   │   └── market_data.py            # 시장 데이터 비즈니스 로직
│   │
│   └── utils/                        # 유틸리티 모듈
│       ├── __init__.py
│       ├── decorators.py             # 요청 데코레이터
│       ├── errors.py                 # 커스텀 에러 핸들러
│       ├── logging.py                # Structured Logging (JSON)
│       └── validators.py             # 입력 검증
│
├── tests/                            # 테스트 스위트 (316 tests, 87% coverage)
│   ├── conftest.py                   # Pytest Fixtures
│   ├── test_api.py                   # API 엔드포인트 테스트
│   ├── test_app_factory.py           # Application Factory 테스트
│   ├── test_characterization_api.py  # Characterization 테스트
│   ├── test_coverage.py              # 커버리지 테스트
│   ├── test_routes.py                # 라우트 테스트
│   └── test_services.py              # 서비스 테스트
│
├── templates/                        # 프론트엔드 템플릿
│   └── index.html                    # 메인 대시보드 UI
│
├── static/                           # 정적 리소스
│   ├── js/
│   │   └── app.js                    # 프론트엔드 로직
│   └── css/
│       └── custom.css                # 커스텀 스타일링
│
├── us_market/                        # 데이터 수집 스크립트
│   ├── update_all.py                 # 마스터 업데이트 스크립트
│   ├── create_us_daily_prices.py     # 가격 데이터 수집
│   └── smart_money_screener_v2.py    # 스마트 머니 스크리닝
│
├── .github/workflows/                # CI/CD 파이프라인
│   └── ci.yml                        # GitHub Actions
│
├── .moai/                            # MoAI-ADK 설정
│   ├── config/                       # 프로젝트 설정
│   ├── specs/                        # SPEC 문서
│   └── project/                      # 프로젝트 문서 (이 파일)
│
├── Dockerfile                        # Multi-stage Docker Build
├── docker-compose.yml                # Docker Compose 설정
├── requirements.txt                  # Python 의존성
├── pyproject.toml                    # 프로젝트 설정 (Ruff, Mypy)
├── .env.example                      # 환경변수 템플릿
└── README.md                         # 프로젝트 문서
```

---

## 모듈 상세 (Module Details)

### 1. Application Factory Pattern (`app/__init__.py`)

**목적**: 중앙 집중식 Flask 애플리케이션 생성

**핵심 함수**:
- `create_app()`: Flask 애플리케이션 인스턴스 생성
- `_init_extensions()`: CORS, Rate Limiting 초기화
- `_register_blueprints()`: Blueprint 등록
- `_register_health_check()`: Health Check 엔드포인트 등록

**의존성**:
- `app.config.Config`: Pydantic 설정
- `app.utils.logging.configure_logging()`: Structlog 설정
- `app.routes.market.market_bp`: Market Blueprint
- `app.routes.health.health_bp`: Health Blueprint

### 2. Configuration Layer (`app/config.py`)

**목적**: Pydantic Settings 기반 설정 관리

**설정 항목**:
- `FLASK_ENV`: Flask 환경 (development/production)
- `LOG_LEVEL`: 로깅 레벨 (DEBUG/INFO/WARNING/ERROR)
- `PORT`: 애플리케이션 포트 (기본: 5001)
- `GOOGLE_API_KEY`: Google Gemini API 키
- `OPENAI_API_KEY`: OpenAI API 키
- `FRED_API_KEY`: FRED 경제 데이터 API 키
- `DATA_DIR`: 데이터 디렉터리 경로
- `CORS_ENABLED`: CORS 활성화 여부
- `RATE_LIMIT_ENABLED`: Rate Limiting 활성화 여부

### 3. Models Layer (`app/models/schemas.py`)

**목적**: Pydantic 기반 데이터 검증

**스키마 타입**:
- Request 스키마: 입력 데이터 검증
- Response 스키마: 출력 데이터 직렬화
- Domain 스키마: 비즈니스 모델

**주요 스키마**:
- `StockInfo`: 종목 기본 정보
- `TechnicalIndicators`: 기술적 지표
- `SmartMoneyScore`: 스마트 머니 점수
- `HealthResponse`: Health Check 응답

### 4. Routes Layer (`app/routes/`)

**Health Blueprint (`health.py`)**:
- `GET /health`: Health Check 엔드포인트
- 컴포넌트 상태 확인

**Market Blueprint (`market.py`)**:
- `GET /`: 메인 대시보드 페이지
- `GET /api/us/indices`: 미국 주요 지수
- `GET /api/us/smart-money`: 스마트 머니 스크리닝
- `GET /api/us/etf-flows`: ETF 자금 흐름
- `GET /api/us/sector-heatmap`: 섹터 히트맵
- `GET /api/us/options-flow`: 옵션 플로우
- `GET /api/us/calendar`: 경제 캘린더
- `GET /api/us/stock/chart`: 종목 차트 데이터
- `GET /api/us/technical-indicators/<ticker>`: 기술적 지표
- `GET /api/us/macro-analysis`: AI 매크로 분석
- `GET /api/us/ai-summary/<ticker>`: AI 종목 요약
- `POST /api/us/update-data`: 데이터 업데이트 트리거

### 5. Services Layer (`app/services/`)

**Cache Service (`cache.py`)**:
- TTL 기반 캐싱 (Time-To-Live)
- 메모리 캐시 또는 Redis 지원
- 캐시 키 생성 및 관리

**Market Data Service (`market_data.py`)**:
- yfinance 데이터 수집
- 기술적 지표 계산
- 스마트 머니 점수 계산
- 데이터 필터링 및 정렬

### 6. Utils Layer (`app/utils/`)

**Decorators (`decorators.py`)**:
- `@validate_request()`: 요청 검증 데코레이터
- `@cache_response()`: 응답 캐싱 데코레이터
- `@handle_errors()`: 에러 핸들링 데코레이터

**Errors (`errors.py`)**:
- 커스텀 에러 클래스
- 에러 응답 포맷팅
- HTTP 상태 코드 관리

**Logging (`logging.py`)**:
- Structlog 설정
- JSON 포맷 로깅
- 로그 레벨별 필터링

**Validators (`validators.py`)**:
- 입력 데이터 검증
- 티커 심볼 검증
- 날짜 범위 검증

---

## 아키텍처 원칙 (Architecture Principles)

### 1. 계층형 아키텍처 (Layered Architecture)

```
[ Routes Layer ]     ← HTTP 요청/응답 처리
     ↓
[ Services Layer ]   ← 비즈니스 로직
     ↓
[ Utils Layer ]      ← 공통 유틸리티
     ↓
[ Data Layer ]       ← 데이터 소스 (CSV, API)
```

### 2. Blueprint Pattern (Blueprint Pattern)

- 모듈별 라우트 분리
- 독립적인 기능 개발
- 재사용 가능한 컴포넌트

### 3. Dependency Injection (의존성 주입)

- Configuration 주입
- Service 주입
- 테스트 가능한 설계

### 4. Separation of Concerns (관심사 분리)

- Routes: HTTP 처리만 담당
- Services: 비즈니스 로직만 담당
- Models: 데이터 검증만 담당

---

## 데이터 흐름 (Data Flow)

### 1. 시장 데이터 조회 요청

```
Client Request
    ↓
[Route] /api/us/stock/chart
    ↓
[Service] market_data.get_stock_chart()
    ↓
[Cache] cache.get_or_fetch()
    ↓
[Data Source] CSV File / yfinance API
    ↓
[Response] JSON formatted data
```

### 2. AI 분석 요청

```
Client Request
    ↓
[Route] /api/us/macro-analysis
    ↓
[Service] market_data.get_macro_analysis()
    ↓
[AI Engine] Gemini / OpenAI API
    ↓
[Response] Formatted analysis text
```

---

## 테스트 구조 (Test Structure)

### 테스트 유형

1. **Unit Tests**: 개별 함수/메서드 테스트
2. **Integration Tests**: 엔드포인트 테스트
3. **Characterization Tests**: 기존 동작 보호 테스트

### 테스트 커버리지

- 전체 테스트: 316개 (315 passed, 1 skipped)
- 커버리지: 87% (목표 85% 초과 달성 ✅)
- 테스트 유형:
  - Unit Tests (단위 테스트)
  - Integration Tests (통합 테스트)
  - Characterization Tests (특성화 테스트)
  - Coverage Tests (커버리지 전용 테스트)

---

## CI/CD 파이프라인 (CI/CD Pipeline)

### GitHub Actions Workflow (`.github/workflows/ci.yml`)

**단계**:
1. **Lint**: Ruff 린팅
2. **Format**: Ruff 포맷 검증
3. **Type Check**: Mypy 타입 검사
4. **Test**: Pytest 실행 (커버리지 리포트)
5. **Security**: 보안 스캔

**트리거**:
- Pull Request 생성 시
- Main 브랜치 Push 시

---

## 컨테이너화 (Containerization)

### Dockerfile (Multi-stage Build)

**Stage 1: Builder**
- Python 3.11-slim 베이스 이미지
- 의존성 설치

**Stage 2: Runtime**
- Gunicorn WSGI 서버
- 최소한의 런타임 의존성

### Docker Compose

**Services**:
- `web`: Flask 애플리케이션
- `redis`: 캐시 서버 (옵션)

---

## 설정 관리 (Configuration Management)

### 환경별 설정

**Development**:
- `FLASK_ENV=development`
- Debug 모드 활성화
- 로컬 데이터베이스

**Production**:
- `FLASK_ENV=production`
- Gunicorn WSGI 서버
- 환경변수 기반 설정

---

**@SPEC:STRUCTURE-001** - 아키텍처 문서
**@SPEC:IMPROVE-001** - 모듈형 리팩토링 완료 (87% 커버리지 달성)
**최종 업데이트**: 2026-02-27
