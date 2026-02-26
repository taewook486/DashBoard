# 진입점 카탤로그

## Application Factory

### `app.create_app()`

**위치**: `app/__init__.py`

**목적**: Flask 애플리케이션 인스턴스 생성

**서명**:
```python
def create_app(config_class: Optional[type] = None) -> Flask
```

**매개변수**:
- `config_class` (Optional[type]): 설정 클래스. 기본값은 `Config` from `app/config.py`

**반환값**:
- `Flask`: 구성된 Flask 애플리케이션 인스턴스

**초기화 순서**:
1. Flask 인스턴스 생성 (template_folder, static_folder 설정)
2. 설정 로드 (`app.config.from_object`)
3. 구조화된 로깅 설정 (`configure_logging`)
4. 확장 초기화 (CORS, Rate Limiting)
5. Blueprint 등록 (market_bp, health_bp)

**호출 패턴**:
```python
# 개발 서버
from app import create_app
app = create_app()
app.run(port=5001)

# Gunicorn (프로덕션)
gunicorn --bind 0.0.0.0:5001 "app:create_app()"
```

**환경별 설정**:
- `development`: DevelopmentConfig (디버그 모드 활성화)
- `production`: ProductionConfig (SECRET_KEY 검증)
- `testing`: TestingConfig (테스트 최적화)

---

## Flask Routes (Blueprint)

### 1. 루트 경로

#### `GET /`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.index()`

**목적**: 메인 대시보드 페이지 렌더링

**응답**:
- `text/html`: `templates/index.html` 렌더링

**구현**:
```python
@market_bp.route("/")
def index():
    return render_template("index.html")
```

---

### 2. 시장 데이터 엔드포인트

#### `GET /api/us/indices`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_us_indices()`

**목적**: 미국 주요 시장 지수 데이터 조회

**쿼리 매개변수**: 없음

**응답** (JSON):
```json
{
  "indices": [
    {
      "name": "S&P 500",
      "symbol": "^GSPC",
      "price": 4785.52,
      "change": 1.23
    },
    {
      "name": "NASDAQ",
      "symbol": "^IXIC",
      "price": 15234.67,
      "change": -0.45
    }
  ]
}
```

**데이터 소스**: yfinance API (실시간)

**캐싱**: 없음 (실시간 조회)

---

#### `GET /api/us/portfolio`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_us_portfolio_data()`

**목적**: 미국 포트폴리오 데이터 (지수, 자산 클래스)

**응답** (JSON):
```json
{
  "market_indices": [
    {
      "name": "S&P 500",
      "price": "4,785.52",
      "change": "+12.34",
      "change_pct": 0.26,
      "color": "green"
    }
  ],
  "top_holdings": [],
  "style_box": {}
}
```

---

#### `GET /api/us/smart-money`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_us_smart_money()`

**목적**: 스마트 머니 픽 데이터

**쿼리 매개변수**: 없음

**응답** (JSON):
```json
{
  "analysis_date": "2025-01-15",
  "analysis_timestamp": "2025-01-15T10:30:00Z",
  "top_picks": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "sector": "Tech",
      "final_score": 78.5,
      "current_price": 185.92,
      "price_at_rec": 180.50,
      "change_since_rec": 3.0,
      "category": "Strong Buy"
    }
  ],
  "summary": {
    "total_analyzed": 492,
    "avg_score": 72.3
  }
}
```

**데이터 소스**:
1. `us_market/smart_money_current.json` (우선)
2. `us_market/data/smart_money_picks_v2.csv` (fallback)

---

#### `GET /api/us/etf-flows`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_us_etf_flows()`

**목적**: ETF 자금 흐름 데이터

**@MX:ANCHOR**: ETF flows endpoint returns market sentiment score and sector data

**응답** (JSON):
```json
{
  "market_sentiment_score": 65.5,
  "sector_flows": [...],
  "top_inflows": [...],
  "top_outflows": [...],
  "all_etfs": [...],
  "ai_analysis": "Bullish sentiment detected in Technology sector..."
}
```

**데이터 소스**: `us_market/data/us_etf_flows.csv`

---

#### `GET /api/us/sector-heatmap`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_us_sector_heatmap()`

**목적**: 섹터 히트맵 데이터

**응답** (JSON):
```json
{
  "sectors": [
    {
      "name": "Technology",
      "change_pct": 2.5,
      "color": "green"
    },
    {
      "name": "Energy",
      "change_pct": -1.2,
      "color": "red"
    }
  ],
  "updated": "2025-01-15T10:30:00Z"
}
```

**데이터 소스**: `us_market/sector_heatmap.json`

---

#### `GET /api/us/options-flow`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_us_options_flow()`

**목적**: 옵션 플로우 모니터링 데이터

**응답** (JSON):
```json
{
  "total_call_volume": 1250000,
  "total_put_volume": 980000,
  "put_call_ratio": 0.78,
  "max_pain": 185.00,
  "updated": "2025-01-15T10:30:00Z"
}
```

**데이터 소스**: `us_market/options_flow.json`

---

#### `GET /api/us/calendar`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_us_calendar()`

**목적**: 주간 경제 캘린더

**응답** (JSON):
```json
{
  "events": [
    {
      "date": "2025-01-15",
      "time": "10:00 AM",
      "name": "CPI Release",
      "impact": "high"
    }
  ],
  "week_of": "2025-01-15"
}
```

**데이터 소스**: `us_market/weekly_calendar.json`

---

### 3. 주식 분석 엔드포인트

#### `GET /api/us/stock-chart/<ticker>`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_us_stock_chart(ticker)`

**목적**: 주식 캔들 차트 데이터

**경로 매개변수**:
- `ticker`: 주식 티커 심볼 (예: AAPL)

**쿼리 매개변수**:
- `period`: 기간 (1mo, 3mo, 6mo, 1y, 2y, 5y, max) - 기본값: "1y"

**응답** (JSON):
```json
{
  "ticker": "AAPL",
  "period": "1y",
  "candles": [
    {
      "time": 1704067200,
      "open": 185.50,
      "high": 187.20,
      "low": 184.80,
      "close": 186.75
    }
  ]
}
```

**데이터 소스**: yfinance API

---

#### `GET /api/us/technical-indicators/<ticker>`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_technical_indicators(ticker)`

**목적**: 기술적 지표 데이터 (RSI, MACD, 볼린저 밴드, 지지/저항)

**경로 매개변수**:
- `ticker`: 주식 티커 심볼

**쿼리 매개변수**:
- `period`: 기간 - 기본값: "1y"

**응답** (JSON):
```json
{
  "ticker": "AAPL",
  "period": "1y",
  "rsi": [
    {"time": 1704067200, "value": 65.43}
  ],
  "macd": {
    "macd_line": [...],
    "signal_line": [...],
    "histogram": [...]
  },
  "bollinger": {
    "upper": [...],
    "middle": [...],
    "lower": [...]
  },
  "support_resistance": {
    "support": [180.50, 178.20, 175.00],
    "resistance": [190.00, 192.50, 195.00]
  }
}
```

**데이터 소스**: yfinance API

**계산 로직**:
- RSI: 14-period Relative Strength Index
- MACD: (12, 26, 9) Moving Average Convergence Divergence
- Bollinger Bands: 20-period, 2 standard deviation
- Support/Resistance: 10-period window, 2% clustering

---

#### `GET /api/us/ai-summary/<ticker>`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_us_ai_summary(ticker)`

**목적**: AI 생성 주식 요약

**경로 매개변수**:
- `ticker`: 주식 티커 심볼

**쿼리 매개변수**:
- `lang`: 언어 (ko, en) - 기본값: "ko"

**응답** (JSON):
```json
{
  "ticker": "AAPL",
  "summary": "Apple Inc. is showing strong momentum...",
  "lang": "ko",
  "news_count": 5,
  "updated": "2025-01-15T10:30:00Z",
  "sentiment": "Positive"
}
```

**데이터 소스**: `us_market/ai_summaries.json`

---

### 4. 매크로 분석 엔드포인트

#### `GET /api/us/macro-analysis`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_us_macro_analysis()`

**목적**: 매크로 경제 분석

**쿼리 매개변수**:
- `lang`: 언어 (ko, en) - 기본값: "ko"
- `model`: AI 모델 (gemini, openai/gpt) - 기본값: "gemini"

**응답** (JSON):
```json
{
  "macro_indicators": {
    "VIX": {
      "current": 13.50,
      "change_1d": -0.25
    },
    "SPY": {
      "current": 478.52,
      "change_1d": 0.26
    },
    "QQQ": {
      "current": 412.35,
      "change_1d": 0.45
    },
    "BTC": {
      "current": 42500.00,
      "change_1d": 1.2
    },
    "GOLD": {
      "current": 2050.50,
      "change_1d": -0.15
    }
  },
  "ai_analysis": "Current market conditions suggest...",
  "model": "gemini",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**데이터 소스**:
- 실시간 지표: yfinance API
- AI 분석: `us_market/macro_analysis_*.json`

---

### 5. 히스토리 엔드포인트

#### `GET /api/us/history-dates`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_us_history_dates()`

**목적**: 사용 가능한 히스토리 날짜 목록

**응답** (JSON):
```json
{
  "dates": ["2025-01-15", "2025-01-14", "2025-01-13"],
  "count": 3
}
```

**데이터 소스**: `us_market/history/picks_*.json` 파일 스캔

---

#### `GET /api/us/history/<date>`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.get_us_history_by_date(date)`

**목적**: 특정 날짜의 히스토리 픽

**경로 매개변수**:
- `date`: 날짜 (YYYY-MM-DD 형식)

**응답** (JSON):
```json
{
  "analysis_date": "2025-01-15",
  "analysis_timestamp": "2025-01-15T10:30:00Z",
  "top_picks": [...],
  "summary": {
    "total": 20,
    "avg_performance": 2.5
  }
}
```

**데이터 소스**: `us_market/history/picks_{date}.json`

---

### 6. 데이터 관리 엔드포인트

#### `POST /api/us/update-data`

**Blueprint**: `market_bp`

**처리 함수**: `app.routes.market.update_market_data()`

**목적**: 데이터 업데이트 트리거 (백그라운드 실행)

**요청 본문**: 없음

**응답** (JSON):
```json
{
  "success": true,
  "message": "Data update started in background. This may take 30-40 minutes to complete.",
  "note": "For faster updates, please use GitHub Actions or run scripts locally.",
  "status": "started",
  "script": "/path/to/us_market/update_all.py"
}
```

**구현**:
- `subprocess.Popen`으로 백그라운드 프로세스 실행
- `us_market/update_all.py` 스크립트 호출
- 비동기 실행 (즉시 응답 반환)

---

## 헬스 체크 엔드포인트

### `GET /health`

**Blueprint**: `health_bp`

**처리 함수**: `app.routes.health.health_check()`

**목적**: 시스템 상태 확인

**응답** (JSON):
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

**용도**:
- Kubernetes/Render 헬스 체크
-负载均衡器 상태 확인
- 모니터링 시스템 연동

---

## 데이터 수집 스크립트 진입점

### `us_market/update_all.py`

**목적**: 마스터 데이터 업데이트 스크립트

**실행 방법**:
```bash
python us_market/update_all.py
```

**역할**:
- 모든 데이터 수집 스크립트 순차적 실행
- 진행률 추적 및 로깅
- 에러 처리와 재시도

**호출하는 스크립트**:
1. create_us_daily_prices.py
2. smart_money_screener_v2.py
3. analyze_etf_flows.py
4. sector_heatmap.py
5. macro_analyzer.py
6. ai_summary_generator.py
7. economic_calendar.py
8. options_flow.py

---

### `us_market/create_us_daily_prices.py`

**목적**: 일일 가격 데이터 생성

**실행 방법**:
```bash
python us_market/create_us_daily_prices.py
```

**출력 파일**:
- `us_market/data/us_daily_prices_{date}.csv`

---

### `us_market/smart_money_screener_v2.py`

**목적**: 6-요인 스마트 머니 스크리닝

**실행 방법**:
```bash
python us_market/smart_money_screener_v2.py
```

**출력 파일**:
- `us_market/smart_money_current.json`
- `us_market/data/smart_money_picks_v2.csv`

---

### `us_market/macro_analyzer.py`

**목적**: Gemini 기반 매크로 분석

**실행 방법**:
```bash
python us_market/macro_analyzer.py
```

**환경 변수 필요**:
- `GOOGLE_API_KEY` 또는 `GEMINI_API_KEY`

**출력 파일**:
- `us_market/macro_analysis.json` (한국어)
- `us_market/macro_analysis_en.json` (영어)

---

### `us_market/macro_analyzer_gpt.py`

**목적**: OpenAI GPT 기반 매크로 분석

**실행 방법**:
```bash
python us_market/macro_analyzer_gpt.py
```

**환경 변수 필요**:
- `OPENAI_API_KEY`

**출력 파일**:
- `us_market/macro_analysis_gpt.json`
- `us_market/macro_analysis_gpt_en.json`

---

### `us_market/ai_summary_generator.py`

**목적**: AI 기반 종목 요약 생성

**실행 방법**:
```bash
python us_market/ai_summary_generator.py
```

**환경 변수 필요**:
- `GOOGLE_API_KEY` (Gemini) 또는 `OPENAI_API_KEY`

**출력 파일**:
- `us_market/ai_summaries.json`

---

## 호출 패턴

### 웹 요청 흐름

```
Client Browser
    ↓ HTTP GET/POST
Flask Application (create_app)
    ↓ Routing
Blueprint (market_bp / health_bp)
    ↓ Handler
Route Handler Function
    ↓ Business Logic
Service Layer (optional)
    ↓ Data Access
yfinance API / File I/O
    ↓ Response
JSON / HTML Response
    ↓
Client Browser
```

### 백그라운드 작업 흐름

```
Admin User / GitHub Actions
    ↓ Trigger
update_all.py
    ↓ Sequential Execution
Individual Scripts
    ↓ Data Collection
yfinance API / AI APIs
    ↓ Save Results
CSV / JSON Files
    ↓
API Endpoints (updated data)
```

---

## CLI 실행 패턴

### 개발 서버 시작

```bash
# 방법 1: Flask CLI
flask run --port=5001

# 방법 2: Python 직접 실행
python -c "from app import create_app; app = create_app(); app.run(port=5001)"

# 방법 3: 환경 변수 설정
export FLASK_APP=app
export FLASK_ENV=development
flask run --port=5001
```

### 프로덕션 서버 시작

```bash
# Gunicorn (4 workers)
gunicorn --bind 0.0.0.0:5001 --workers 4 "app:create_app()"

# Docker
docker run -p 5001:5001 --env-file .env dashboard:latest
```

### 데이터 업데이트 실행

```bash
# 전체 업데이트
python us_market/update_all.py

# 개별 스크립트 실행
python us_market/smart_money_screener_v2.py
python us_market/macro_analyzer.py
```

### 테스트 실행

```bash
# 전체 테스트
pytest tests/ -v

# 커버리지 포함
pytest tests/ --cov=app --cov-report=html

# 특정 테스트 파일
pytest tests/test_api.py -v
```
