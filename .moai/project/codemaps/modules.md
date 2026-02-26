# 모듈 카탤로그

## app/__init__.py

**목적**: Application Factory 패턴으로 Flask 애플리케이션 생성

**책임**:
- Flask 애플리케이션 인스턴스 생성 및 반환
- 확장 초기화 (CORS, Rate Limiting)
- Blueprint 등록 (market_bp, health_bp)
- 구조화된 로깅 설정
- 환경별 설정 로딩 (development, production, testing)

**공개 인터페이스**:
- `create_app(config_class=None) -> Flask`: 애플리케이션 팩토리 함수

**내부 조직**:
- `_init_extensions(app)`: Flask 확장 초기화 (비공개)
- `_register_blueprints(app)`: Blueprint 등록 (비공개)
- `_register_health_check(app)`: 헬스 체크 등록 (비공개)

**의존성**:
- app.config.Config (Pydantic Settings)
- app.routes.market.market_bp
- app.routes.health.health_bp
- app.utils.logging.configure_logging

---

## app/config.py

**목적**: Pydantic Settings를 통한 중앙 집중식 설정 관리

**책임**:
- 환경 변수 로드 및 검증
- 타입 변환과 기본값 제공
- 설정 불변성(immutability) 보장
- 환경별 설정 클래스 제공

**공개 인터페이스**:
- `Settings`: Pydantic BaseSettings 기반 설정 클래스
- `Config`: Flask 호환 설정 래퍼
- `DevelopmentConfig`: 개발 환경 설정
- `ProductionConfig`: 프로덕션 환경 설정
- `TestingConfig`: 테스트 환경 설정
- `get_config()`: 환경별 설정 팩토리 함수

**설정 카테고리**:
1. Flask 설정: FLASK_ENV, FLASK_DEBUG, SECRET_KEY
2. 서버 설정: HOST, PORT
3. 로깅 설정: LOG_LEVEL, LOG_FORMAT
4. CORS 설정: CORS_ENABLED, ALLOWED_ORIGINS
5. 속도 제한: RATE_LIMIT_ENABLED, RATE_LIMIT_DEFAULT
6. 캐시 설정: CACHE_TTL_SECONDS, CACHE_ENABLED
7. 외부 API 키: OPENAI_API_KEY, GEMINI_API_KEY, GOOGLE_API_KEY, FRED_API_KEY

**내부 조직**:
- 필드 검증기: `validate_env()`, `validate_log_level()`
- Flask 프로퍼티: DEBUG, SECRET_KEY, ENV, TESTING

---

## app/models/schemas.py

**목적**: Pydantic 데이터 모델 정의

**책임**:
- 요청/응답 데이터 스키마 정의
- 데이터 검증과 타입 강제
- 직렬화/역직렬화

**공개 인터페이스**:
- (현재 프로젝트에서는 사용되지 않지만 모듈 구조로 존재)

---

## app/routes/market.py

**목적**: 시장 데이터 엔드포인트 라우팅

**책임**:
- HTTP 요청 처리 및 응답 반환
- yfinance API를 통한 실시간 데이터 조회
- 파일 기반 데이터 로드 (CSV, JSON)
- 섹터 매핑 및 캐싱

**공개 인터페이스** (Blueprint 경로):
1. `GET /`: 메인 페이지 렌더링
2. `GET /api/us/indices`: 미국 주요 지수 데이터
3. `GET /api/us/portfolio`: 미국 포트폴리오 데이터
4. `GET /api/us/smart-money`: 스마트 머니 픽
5. `GET /api/us/etf-flows`: ETF 자금 흐름
6. `GET /api/us/stock-chart/<ticker>`: 주식 차트 데이터
7. `GET /api/us/history-dates`: 사용 가능한 히스토리 날짜
8. `GET /api/us/history/<date>`: 특정 날짜의 히스토리
9. `GET /api/us/macro-analysis`: 매크로 경제 분석
10. `GET /api/us/sector-heatmap`: 섹터 히트맵
11. `GET /api/us/options-flow`: 옵션 플로우
12. `GET /api/us/calendar`: 경제 캘린더
13. `GET /api/us/ai-summary/<ticker>`: AI 생성 요약
14. `GET /api/us/technical-indicators/<ticker>`: 기술적 지표
15. `POST /api/us/update-data`: 데이터 업데이트 트리거

**내부 상태**:
- `SECTOR_MAP`: 티커 to 섹터 매핑 (하드코딩된 95개 티커)
- `_sector_cache`: 동적 섹터 캐시 (파일 기반)

**내부 함수**:
- `get_sector(ticker)`: 티커의 섹터 반환 (yfinance fallback)
- `_load_sector_cache()`: 섹터 캐시 로드
- `_save_sector_cache(cache)`: 섹터 캐시 저장

**의존성**:
- yfinance (실시간 가격 데이터)
- pandas (CSV 파일 로드)
- JSON 파일 (us_market/data/)

---

## app/routes/health.py

**목적**: 헬스 체크 엔드포인트

**책임**:
- 시스템 상태 확인
- 컴포넌트 상태 보고

**공개 인터페이스**:
- `GET /health`: 헬스 체크 응답

---

## app/services/market_data.py

**목적**: 시장 데이터 비즈니스 로직 및 캐싱

**책임**:
- yfinance API 호출 래핑
- 일괄(batch) 데이터 조회 최적화
- 캐싱 데코레이터 적용
- 섹터 정보 조회

**공개 인터페이스**:
- `MarketDataService`: 시장 데이터 서비스 클래스
  - `get_ticker_data(ticker, period)`: 단일 티커 데이터 조회
  - `get_ticker_data_batch(tickers, period)`: 일괄 티커 데이터 조회
  - `get_ticker_data_async(ticker, period)`: 비동기 단일 조회 (래퍼)
  - `get_multiple_tickers_async(tickers, period)`: 비동기 일괄 조회
  - `get_sector_info(ticker)`: 섹터 정보 조회
  - `get_index_data(indices)`: 지수 데이터 조회

**캐싱 전략**:
- `@cached(ttl=300, key_prefix='ticker_data')`: 티커 데이터 5분 캐시
- `@cached(ttl=300, key_prefix='sector_info')`: 섹터 정보 5분 캐시

**내부 최적화**:
- `yf.download()` 일괄 다운로드 활용
- 배치 처리로 API 호출 최소화

**의존성**:
- app.services.cache (캐싱 데코레이터)
- yfinance (시장 데이터 소스)

---

## app/services/cache.py

**목적**: 캐싱 서비스 및 데코레이터

**책임**:
- 인메모리 캐시 관리
- TTL 기반 캐시 만료
- 함수 결과 캐싱 데코레이터

**공개 인터페이스**:
- `get_cache()`: 캐시 인스턴스 반환 (싱글톤)
- `@cached(ttl, key_prefix)`: 캐싱 데코레이터
- `SimpleCache` 클래스: 기본 캐시 구현

---

## app/utils/decorators.py

**목적**: 요청 처리 데코레이터

**책임**:
- 재시도 로직
- 오류 처리
- 요청 로깅

---

## app/utils/errors.py

**목적**: 커스텀 에러 핸들러

**책임**:
- 예외 클래스 정의
- 에러 응답 포맷팅
- HTTP 예외 매핑

---

## app/utils/logging.py

**목적**: Structlog 설정

**책임**:
- JSON 포맷 로깅 구성
- 로그 레벨 설정
- 로그 포매터 설정

**공개 인터페이스**:
- `configure_logging(log_level)`: 로깅 시스템 초기화

---

## app/utils/validators.py

**목적**: 입력 데이터 검증

**책임**:
- 요청 매개변수 검증
- 티커 심볼 검증
- 날짜 범위 검증

---

## us_market/update_all.py

**목적**: 마스터 데이터 업데이트 스크립트

**책임**:
- 모든 데이터 수집 스크립트 순차적 실행
- 진행률 추적 및 로깅
- 에러 처리와 재시도

**실행 순서**:
1. 일일 가격 데이터 생성 (create_us_daily_prices.py)
2. 스마트 머니 스크리닝 (smart_money_screener_v2.py)
3. ETF 흐름 분석 (analyze_etf_flows.py)
4. 섹터 히트맵 생성 (sector_heatmap.py)
5. 매크로 분석 (macro_analyzer.py)
6. AI 요약 생성 (ai_summary_generator.py)
7. 경제 캘린더 (economic_calendar.py)
8. 옵션 플로우 (options_flow.py)

---

## us_market/smart_money_screener_v2.py

**목적**: 6-요인 스마트 머니 스크리닝

**책임**:
- 492개 미국 주식 분석
- 6개 요인 기반 점수 계산
- 상위 20개 픽 선정

**6-요인 스크리닝**:
1. **수급 분석 (25%)**: 거래량 누적 패턴
2. **기관 지지 (20%)**: 13F holdings 트래킹
3. **기술적 지표 (20%)**: RSI, MACD, 볼린저 밴드
4. **펀더멘털 (15%)**: P/E, PEG 비율
5. **애널리스트 평가 (10%)**: 월가 컨센서스
6. **상대 강도 (10%)**: S&P 500 대비 성과

**출력 파일**:
- `us_market/smart_money_current.json`: 현재 분석 결과
- `us_market/data/smart_money_picks_v2.csv`: CSV 백업

---

## us_market/macro_analyzer.py

**목적**: Gemini 기반 매크로 경제 분석

**책임**:
- 경제 지표 수집 (VIX, 금리, 달러, 원화)
- Gemini AI를 통한 경제 분석 생성
- 한국어/영어 지원

**출력 파일**:
- `us_market/macro_analysis.json`: 한국어 분석
- `us_market/macro_analysis_en.json`: 영어 분석

---

## us_market/macro_analyzer_gpt.py

**목적**: OpenAI GPT 기반 매크로 경제 분석

**책임**:
- 경제 지표 수집
- GPT 모델을 통한 경제 분석 생성
- 한국어/영어 지원

**출력 파일**:
- `us_market/macro_analysis_gpt.json`: GPT 분석 결과
- `us_market/macro_analysis_gpt_en.json`: 영어 GPT 분석

---

## us_market/ai_summary_generator.py

**목적**: AI 기반 개별 종목 요약 생성

**책임**:
- 주식 뉴스 수집
- AI 요약 생성 (Gemini/OpenAI)
- 감정 분석

**출력 파일**:
- `us_market/ai_summaries.json`: 모든 종목 요약

---

## us_market/analyze_etf_flows.py

**목적**: ETF 자금 흐름 분석

**책임**:
- 24개 ETF 수익률 계산
- 자금 흐름 점수 산출
- 시장 심리 평가

**출력 파일**:
- `us_market/data/us_etf_flows.csv`: ETF 흐름 데이터
- `us_market/etf_flow_analysis.json`: AI 분석

---

## us_market/sector_heatmap.py

**목적**: 섹터 히트맵 생성

**책임**:
- 11개 섹터 수익률 계산
- 히트맵 데이터 구조화

**출력 파일**:
- `us_market/sector_heatmap.json`: 섹터 히트맵 데이터

---

## us_market/economic_calendar.py

**목적**: 경제 캘린더 생성

**책임**:
- 주요 경제 이벤트 추출
- 날짜별 이벤트 정리

**출력 파일**:
- `us_market/weekly_calendar.json`: 주간 경제 캘린더

---

## us_market/options_flow.py

**목적**: 옵션 플로우 모니터링

**책임**:
- 옵션 거래 데이터 수집
- 풋/콜 비율 계산

**출력 파일**:
- `us_market/options_flow.json`: 옵션 플로우 데이터

---

## 모듈 경계

### 명확한 경계

1. **Flask 앱 (app/)**: API 서버로서 HTTP 요청/응답 처리
2. **데이터 수집 (us_market/)**: 독립 실행형 스크립트로 백그라운드 작업

### 계층 간 통신 규칙

- **Routes → Services**: 라우트는 서비스 계층만 호출
- **Services → Data Sources**: 서비스만 데이터 소스(yfinance, 파일)에 접근
- **Direct Data Access**: 라우트에서 직접 파일 I/O 금지 (일부 예외 존재)

### 모듈 간 의존성 방향

```
routes/market.py
    ↓
services/market_data.py
    ↓
yfinance API / CSV Files
```

---

## 공개 API와 내부 구현

### 공개 API (외부 호출 가능)

- Flask 엔드포인트 (app/routes/*.py)
- create_app() 팩토리 함수 (app/__init__.py)

### 내부 구현 (모듈 내부에서만 사용)

- 서비스 클래스 메서드 (app/services/*.py)
- 유틸리티 함수 (app/utils/*.py)
- 헬퍼 함수 (비공개 함수: _prefix)

### 데이터 모델

- Pydantic 모델 (app/models/schemas.py): 요청/응답 스키마
- 내부 딕셔너리: 모듈 간 데이터 전달
