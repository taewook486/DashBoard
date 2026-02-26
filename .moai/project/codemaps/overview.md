# DashBoard 아키텍처 개요

## 아키텍처 패턴

DashBoard는 **Flask Blueprint 패턴**을 기반으로 한 모듈형 웹 애플리케이션 아키텍처를 따릅니다.

### 핵심 패턴: Application Factory + Blueprint

**Application Factory 패턴**
- `create_app()` 함수가 Flask 애플리케이션 인스턴스를 생성
- 설정 로딩, 확장 초기화, Blueprint 등록을 단일 진입점에서 관리
- 테스트와 다양한 환경(development, production, testing) 지원

**Blueprint 패턴**
- 기능별로 Blueprint 분리 (market_bp, health_bp)
- 라우트, 서비스, 유틸리티가 명확하게 분리된 계층 구조
- 모듈 확장과 유지보수가 용이한 구조

### 계층형 아키텍처 (Layered Architecture)

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│    (Flask Routes / Blueprints)          │
├─────────────────────────────────────────┤
│         Business Logic Layer            │
│       (Services / Cache)                │
├─────────────────────────────────────────┤
│         Data Access Layer               │
│    (yfinance / pandas / File I/O)       │
├─────────────────────────────────────────┤
│         External APIs Layer             │
│  (Google Gemini / OpenAI / yfinance)    │
└─────────────────────────────────────────┘
```

## 기술 스택

### 백엔드 프레임워크
- **Flask 3.0+**: 가볍고 유연한 REST API 프레임워크
- **Pydantic 2.0+:** 데이터 검증과 설정 관리 (Pydantic Settings)
- **Structlog**: 구조화된 JSON 로깅

### 데이터 처리
- **pandas**: 데이터프레임 연산과 CSV 처리
- **numpy**: 수치 계산
- **yfinance**: 야후 파이낸스 API를 통한 시장 데이터 수집
- **TA-Lib (선택)**: 기술적 지표 계산 (RSI, MACD, 볼린저 밴드)

### AI/ML 통합
- **Google Generative AI**: Gemini API를 통한 매크로 경제 분석
- **OpenAI**: GPT 모델을 통한 시장 인사이트 생성

### 보안 및 성능
- **Flask-CORS**: 크로스 오리진 리소스 공유
- **Flask-Limiter**: 속도 제한 (Rate Limiting)
- **캐싱 서비스**: TTL 기반 인메모리 캐시 (300초 기본)

### 데이터 수집 (us_market/)
- **독립 실행형 Python 스크립트**: 일일 시장 데이터 업데이트
- **Smart Money Screener**: 6개 요인 기반 주식 스크리닝
- **ETF Flow Analyzer**: 자금 흐름 분석
- **Macro Analyzer**: AI 기반 경제 분석

### 테스트 및 배포
- **pytest**: 111개 테스트 케이스, 67% 커버리지
- **Docker**: 멀티스테이지 Dockerfile
- **GitHub Actions**: CI/CD 파이프라인
- **Gunicorn**: 프로덕션 WSGI 서버

## 모듈 조직화

### app/ 디렉토리 구조

```
app/
├── __init__.py           # Application Factory (create_app)
├── config.py             # Pydantic Settings 설정 관리
├── models/
│   └── schemas.py        # Pydantic 데이터 모델
├── routes/
│   ├── health.py         # 헬스 체크 엔드포인트
│   └── market.py         # 시장 데이터 엔드포인트 (17개 경로)
├── services/
│   ├── cache.py          # 캐싱 서비스 (TTL, 데코레이터)
│   └── market_data.py    # 시장 데이터 비즈니스 로직
└── utils/
    ├── decorators.py     # 요청 데코레이터
    ├── errors.py         # 커스텀 에러 핸들러
    ├── logging.py        # Structlog 설정
    └── validators.py     # 입력 검증
```

### us_market/ 디렉토리 구조

데이터 수집 스크립트는 Flask 앱과 독립적으로 실행됩니다:

```
us_market/
├── update_all.py              # 마스터 업데이트 스크립트
├── create_us_daily_prices.py  # 일일 가격 데이터 수집
├── smart_money_screener_v2.py # 6-요인 스마트 머니 스크리닝
├── analyze_etf_flows.py       # ETF 자금 흐름 분석
├── sector_heatmap.py          # 섹터 히트맵 생성
├── macro_analyzer.py          # Gemini 기반 매크로 분석
├── macro_analyzer_gpt.py      # OpenAI 기반 매크로 분석
├── ai_summary_generator.py    # AI 주식 요약 생성
├── economic_calendar.py       # 경제 캘린더 생성
├── options_flow.py            # 옵션 플로우 모니터링
├── analyze_13f.py             # 13F holdings 분석
└── data/                      # CSV 데이터 저장소
```

## 핵심 설계 결정

### 1. Blueprint 패턴 채택

**이유**: 모듈성과 확장성

- 각 기능 영역을 독립적인 Blueprint로 분리
- 라우트가 명확하게 구성되고 유지보수가 용이
- @SPEC:IMPROVE-001 요구사항에 따른 리팩토링 결과

### 2. Pydantic Settings 활용

**이유**: 타입 안전성과 환경 변수 관리

- 환경 변수를 통한 설정 관리 (.env 파일)
- 타입 검증과 변환 자동화
- 불변(immutable) 설정 객체로 보안 강화

### 3. 서비스 계층 분리

**이유**: 비즈니스 로직과 라우팅 로직 분리

- `services/market_data.py`: 시장 데이터 조회 및 캐싱 로직
- `routes/market.py`: HTTP 요청/응답 처리만 담당
- 테스트 용이성 향상과 코드 재사용성 증대

### 4. 캐싱 전략

**이유**: 성능 최적화와 외부 API 부하 감소

- TTL 기반 인메모리 캐시 (기본 300초)
- `@cached` 데코레이터로 선언적 캐싱
- yfinance API 호출 최소화

### 5. 구조화된 로깅

**이유**: 디버깅과 모니터링 향상

- Structlog로 JSON 형식 로그
- 로그 레벨별 환경 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 요청 추적과 오류 진단 용이

### 6. 데이터 수집 스크립트 분리

**이유**: 장기 실행 작업과 API 서버 분리

- Flask 앱과 독립적인 데이터 수집 파이프라인
- GitHub Actions를 통한 자동화된 일일 업데이트
- 병렬 처리 가능한 독립 스크립트

## 데이터 아키텍처

### 데이터 소스

1. **실시간 데이터**: yfinance API를 통한 라이브 가격 조회
2. **일일 스냅샷**: us_market/data/ 디렉토리의 CSV 파일들
3. **AI 분석 결과**: JSON 파일로 저장된 캐시된 분석

### 데이터 흐름

```
외부 API (yfinance, Gemini, OpenAI)
    ↓
데이터 수집 스크립트 (us_market/*.py)
    ↓
CSV/JSON 파일 저장 (us_market/data/)
    ↓
Flask API (app/routes/market.py)
    ↓
프론트엔드 (templates/index.html + static/js/app.js)
```

### 캐싱 계층

1. **애플리케이션 캐시**: Python 인메모리 (services/cache.py)
2. **파일 기반 캐시**: sector_cache.json
3. **AI 분석 캐시**: macro_analysis_*.json, ai_summaries.json

## 보안 아키텍처

### 보안 계층

1. **입력 검증**: Pydantic 모델로 요청 데이터 검증
2. **속도 제한**: Flask-Limiter로 DDoS 방지
3. **CORS 정책**: 환경 변수 기반 오리진 허용
4. **설정 관리**: Pydantic Settings로 보안 설정 강화 (불변 객체)
5. **API 키 관리**: 환경 변수로 외부 API 키 보호

## 확장성 고려사항

### 현재 확장 지점

1. **새로운 Blueprint 추가**: `app/routes/`에 새로운 Blueprint 생성
2. **서비스 계층 확장**: `app/services/`에 새로운 서비스 추가
3. **데이터 수집 스크립트**: `us_market/`에 새로운 분석 스크립트 추가
4. **API 엔드포인트**: Blueprint에 새로운 경로 등록

### 미래 확장 가능성

- **데이터베이스 통합**: CSV 파일을 PostgreSQL/MySQL로 대체
- **비동기 처리**: async/await를 통한 동시성 개선
- **메시지 큐**: Celery를 통한 백그라운드 작업 처리
- **마이크로서비스**: 각 Blueprint를 독립 서비스로 분리

## @SPEC:IMPROVE-001 달성 사항

모듈형 아키텍처 리팩토링 (@SPEC:IMPROVE-001)을 통해 다음을 달성했습니다:

- Application Factory 패턴 구현
- Blueprint 기반 라우팅 분리
- Pydantic Settings 도입
- 서비스 계층 분리
- 구조화된 로깅 시스템
- 67% 테스트 커버리지 달성 (111개 테스트)
- Docker 및 CI/CD 파이프라인 구축
