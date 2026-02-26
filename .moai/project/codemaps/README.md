# DashBoard 아키텍처 문서

## 개요

이 디렉토리에는 DashBoard 프로젝트의 포괄적인 아키텍처 문서가 포함되어 있습니다. 각 문서는 프로젝트의 특정 측면을 상세히 설명합니다.

## 문서 목록

### 1. [overview.md](./overview.md)
- 아키텍처 패턴 (Blueprint, Application Factory)
- 기술 스택 (Flask, Pydantic, yfinance, AI/ML)
- 모듈 조직화 (app/, us_market/)
- 핵심 설계 결정 및 이유
- 데이터 아키텍처
- 보안 아키텍처
- 확장성 고려사항

### 2. [modules.md](./modules.md)
- 각 모듈의 목적과 책임
- 공개 인터페이스와 내부 구현
- 모듈 경계와 통신 규칙
- Flask 앱 모듈 상세 (app/*)
- 데이터 수집 스크립트 상세 (us_market/*)

### 3. [dependencies.md](./dependencies.md)
- 내부 모듈 의존성 그래프
- 외부 의존성 (Flask, Pydantic, yfinance, AI/ML)
- 의존성 트리 구조
- 의존성 관리 전략
- 순환 의존성 감지 및 방지

### 4. [entry-points.md](./entry-points.md)
- Application Factory 패턴
- Flask 라우트 (17개 엔드포인트)
- 헬스 체크 엔드포인트
- 데이터 수집 스크립트 진입점
- CLI 실행 패턴

### 5. [data-flow.md](./data-flow.md)
- 요청 처리 흐름 (Mermaid 시퀀스 다이어그램)
- 주요 데이터 경로 (지수, 스마트 머니, ETF, 기술적 지표)
- 캐시 사용 패턴
- 외부 API 호출 패턴 (yfinance, Gemini, OpenAI)
- 데이터 수집 파이프라인
- 에러 처리 및 폴백
- 성능 최적화 전략

## 주요 다이어그램

### 아키텍처 계층도
```
Presentation Layer (Flask Routes)
    ↓
Business Logic Layer (Services)
    ↓
Data Access Layer (yfinance, Files)
    ↓
External APIs (Yahoo, Gemini, OpenAI)
```

### 요청 처리 시퀀스
```
Client → Flask → CORS → Rate Limiter → Blueprint
→ Service → Cache → yfinance → Response
```

### 의존성 그래프
```
app/__init__.py → app/config.py
              → app/routes/market.py → app/services/market_data.py
                                        → app/services/cache.py
```

## 기술 스택 요약

| 카테고리 | 기술 |
|----------|------|
| 웹 프레임워크 | Flask 3.0+ |
| 데이터 검증 | Pydantic 2.0+ |
| 데이터 처리 | pandas, numpy |
| 시장 데이터 | yfinance 0.2.28+ |
| AI/ML | Google Gemini, OpenAI |
| 로깅 | Structlog 24.0+ |
| 테스트 | pytest 8.0+ |
| 배포 | Docker, Gunicorn |

## 프로젝트 구조

```
DashBoard/
├── app/                          # Flask 애플리케이션
│   ├── __init__.py               # Application Factory
│   ├── config.py                 # Pydantic Settings
│   ├── models/schemas.py         # Pydantic 모델
│   ├── routes/                   # Flask Blueprints
│   │   ├── health.py             # 헬스 체크
│   │   └── market.py             # 시장 데이터 (17개 경로)
│   ├── services/                 # 비즈니스 로직
│   │   ├── cache.py              # 캐싱 서비스
│   │   └── market_data.py        # 시장 데이터 서비스
│   └── utils/                    # 유틸리티
│       ├── decorators.py         # 데코레이터
│       ├── errors.py             # 에러 처리
│       ├── logging.py            # 로깅
│       └── validators.py         # 검증
│
├── us_market/                    # 데이터 수집 스크립트
│   ├── update_all.py             # 마스터 업데이트
│   ├── create_us_daily_prices.py # 가격 데이터
│   ├── smart_money_screener_v2.py # 6-요인 스크리닝
│   ├── analyze_etf_flows.py      # ETF 흐름
│   ├── sector_heatmap.py         # 섹터 히트맵
│   ├── macro_analyzer.py         # Gemini 매크로
│   ├── macro_analyzer_gpt.py     # OpenAI 매크로
│   └── data/                     # CSV/JSON 데이터
│
├── tests/                        # 테스트 스위트 (111개)
├── templates/                    # 프론트엔드 템플릿
├── static/                       # 정적 파일
└── .moai/project/codemaps/       # 이 문서들
```

## 핵심 설계 원칙

1. **Blueprint 패턴**: 모듈형 라우팅
2. **Pydantic Settings**: 타입 안전한 설정 관리
3. **서비스 계층 분리**: 비즈니스 로직과 라우팅 분리
4. **캐싱 전략**: TTL 기반 성능 최적화
5. **구조화된 로깅**: JSON 포맷 로그
6. **데이터 수집 분리**: 독립적인 백그라운드 작업

## 데이터 통계

- **492개 미국 주식** 분석
- **746,233개** 가격 기록
- **11개 주요 지수** 추적
- **11개 섹터** 히트맵
- **24개 ETF** 자금 흐름
- **6개 요인** 스마트 머니 스크리닝

## API 엔드포인트

### 시장 데이터
- `GET /api/us/indices` - 주요 지수
- `GET /api/us/smart-money` - 스마트 머니 픽
- `GET /api/us/etf-flows` - ETF 흐름
- `GET /api/us/sector-heatmap` - 섹터 히트맵
- `GET /api/us/options-flow` - 옵션 플로우
- `GET /api/us/calendar` - 경제 캘린더

### 주식 분석
- `GET /api/us/stock-chart/<ticker>` - 차트 데이터
- `GET /api/us/technical-indicators/<ticker>` - 기술적 지표
- `GET /api/us/ai-summary/<ticker>` - AI 요약

### 매크로
- `GET /api/us/macro-analysis` - 매크로 경제 분석

### 데이터 관리
- `POST /api/us/update-data` - 데이터 업데이트 트리거
- `GET /health` - 헬스 체크

## 문서 사용법

### 새로운 팀원 온보딩
1. [overview.md](./overview.md)로 시작하여 전체 아키텍처 이해
2. [modules.md](./modules.md)로 모듈별 상세 기능 학습
3. [entry-points.md](./entry-points.md)로 API 엔드포인트 확인

### 기능 추가 개발
1. [dependencies.md](./dependencies.md)로 의존성 영향 확인
2. [modules.md](./modules.md)로 관련 모듈 식별
3. [data-flow.md](./data-flow.md)로 데이터 흐름 이해

### 버그 수정
1. [data-flow.md](./data-flow.md)로 에러 발생 지점 추적
2. [modules.md](./modules.md)로 관련 모듈 책임 확인
3. [entry-points.md](./entry-points.md)로 엔드포인트 동작 확인

### 성능 최적화
1. [data-flow.md](./data-flow.md)의 성능 최적화 전략 참고
2. [dependencies.md](./dependencies.md)로 의존성 최적화 기회 확인

## @SPEC:IMPROVE-001

이 문서는 @SPEC:IMPROVE-001 (모듈형 아키텍처 리팩토링)의 결과물입니다.

### 달성 목표
- ✅ Application Factory 패턴 구현
- ✅ Blueprint 기반 라우팅 분리
- ✅ Pydantic Settings 도입
- ✅ 서비스 계층 분리
- ✅ 구조화된 로깅 시스템
- ✅ 67% 테스트 커버리지 (111개 테스트)
- ✅ Docker 및 CI/CD 파이프라인

## 유지보수

이 문서들은 코드베이스와 동기화되어야 합니다. 주요 변경 사항이 있을 때마다 관련 문서를 업데이트하세요.

**문서 업데이트 체크리스트**:
- [ ] 새로운 엔드포인트 추가 → `entry-points.md` 업데이트
- [ ] 모듈 구조 변경 → `modules.md` 및 `dependencies.md` 업데이트
- [ ] 새로운 의존성 추가 → `dependencies.md` 업데이트
- [ ] 데이터 흐름 변경 → `data-flow.md` 업데이트
- [ ] 주요 설계 변경 → `overview.md` 업데이트

## 연락처

문서에 대한 질문이나 개선 제안은 프로젝트 저장소의 Issue를 통해 제출해 주세요.

---

**생성 날짜**: 2026-02-27
**버전**: 1.0.0
**작성자**: MoAI Documentation Agent
**프로젝트**: DashBoard - Smart Money Market Analysis System
