# DashBoard 기술 스택 (Technology Stack)

**개발 프레임워크 및 도구 모음**

---

## 백엔드 기술 (Backend Technologies)

### 핵심 프레임워크

**Flask 3.0+**
- 경량 REST API 프레임워크
- Application Factory Pattern
- Blueprint 기반 모듈형 아키텍처
- 확장 가능한 미들웨어 시스템

### 데이터 검증 및 설정

**Pydantic 2.0+**
- 타입 기반 데이터 검증
- Pydantic Settings: 환경변수 관리
- 자동 JSON 직렬화/역직렬화
- OpenAPI 스키마 생성

**python-dotenv 1.0+**
- .env 파일 기반 설정 관리
- 환경별 설정 분리
- 비밀 정보 보호

### 데이터 처리

**pandas 2.0+**
- 시계열 데이터 처리
- CSV 파일 입출력
- 데이터 필터링 및 변환
- DataFrame 기반 분석

**numpy 1.24+**
- 수치 연산
- 배열 데이터 처리
- 기술적 지표 계산

**yfinance 0.2.28+**
- Yahoo Finance API 데이터 수집
- 실시간 주식 가격 조회
- 과거 시세 데이터 다운로드
- 재무 정보 추출

### 로깅

**structlog 24.0+**
- 구조화된 JSON 로깅
- 로그 레벨별 필터링
- 컨텍스트 기반 로깅
- production 친화적 로그 포맷

### 웹 확장

**Flask-CORS 4.0+**
- Cross-Origin Resource Sharing
- 출처 기반 접근 제어
- 프리플라이트 요청 처리

**Flask-Limiter 3.5.0+**
- Rate Limiting
- IP 기반 요청 제한
- 메모리/Redis 스토리지 지원

### AI/ML 통합

**google-generativeai 0.3.0+**
- Google Gemini 3.0 API
- 매크로 경제 분석
- 멀티모달 지원

**openai 1.0.0+**
- OpenAI GPT-5.2 API
- 종목별 인사이트 생성
- 텍스트 요약 및 분석

---

## 프론트엔드 기술 (Frontend Technologies)

### 스타일링

**Tailwind CSS**
- Utility-first CSS 프레임워크
- 반응형 디자인
- 다크 모드 지원
- 커스텀 테마

### 데이터 시각화

**Lightweight Charts**
- 고성능 캔들스틱 차트
- 실시간 데이터 업데이트
- 기술적 지표 오버레이
- 인터랙티브 줌/팬

**Chart.js**
- 다양한 차트 타입
- 라인/바/파이 차트
- 애니메이션 지원
- 반응형 크기 조정

**ApexCharts**
- 히트맵 시각화
- 트리맵 차트
- 고급 인터랙션
- 커스텀 툴팁

### DOM 조작

**jQuery**
- DOM 조작 및 이벤트 처리
- AJAX 요청
- 플러그인 생태계

---

## 보안 및 성능 (Security & Performance)

### 보안

**CORS (Cross-Origin Resource Sharing)**
- 허용된 출처만 접근
- 프리플라이트 요청 검증
- 자격 증명 포함 지원

**Rate Limiting**
- IP 기반 요청 제한
- 기본: 100 requests/minute
- 메모리 기반 스토리지

**Input Validation**
- Pydantic 스키마 검증
- 티커 심볼 검증
- 날짜 범위 검증
- SQL Injection 방지

### 성능

**Gunicorn 21.0.0+**
- Production WSGI 서버
- Multi-worker 처리
- 비동기 worker 지원

**Caching**
- TTL 기반 캐싱
- 메모리 캐시
- 선택적 Redis 지원

---

## 테스트 도구 (Testing Tools)

### 테스트 프레임워크

**pytest 8.0.0+**
- Python 테스트 프레임워크
- Fixture 기반 테스트 설정
- Parametrized 테스트
- Plugin 생태계

**pytest-cov 4.0.0+**
- 코드 커버리지 리포트
- HTML 커버리지 보고서
- 분기 커버리지 측정

**pytest-mock 3.12.0+**
- Mock 객체 생성
- 외부 서비스 모킹
- Patch 기능

### 테스트 커버리지

- **총 테스트**: 316개 (315 passed, 1 skipped)
- **커버리지**: 87% (목표 85% 초과 달성 ✅)
- **테스트 유형**:
  - Unit Tests (단위 테스트)
  - Integration Tests (통합 테스트)
  - Characterization Tests (특성화 테스트)
  - Coverage Tests (커버리지 전용 테스트)

---

## 코드 품질 (Code Quality)

### 린팅 및 포맷팅

**Ruff**
- Python 린터 및 포맷터
- 빠른 린팅 속도
- Flake8, Black 기능 통합
- Configuration: `pyproject.toml`

### 타입 검사

**mypy**
- 정적 타입 검사
- 타입 힌트 검증
- 옵셔널 타입 지원

---

## 배포 및 DevOps (Deployment & DevOps)

### 컨테이너화

**Docker**
- Multi-stage Dockerfile
- Python 3.11-slim 베이스
- Gunicorn 런타임
- 최소 이미지 크기 최적화

**docker-compose**
- 서비스 오케스트레이션
- 볼륨 마운트
- 환경변수 관리
- 네트워크 구성

### CI/CD

**GitHub Actions**
- 자동화 파이프라인
- Lint, Format, Type Check
- Test 실행 및 커버리지
- Security Scan

### 클라우드 호스팅

**Render**
- PaaS 플랫폼
- 자동 배포
- 환경변수 관리

**Vercel**
- 프론트엔드 호스팅
- CDN 배포
- 자동 SSL

---

## 데이터 시각화 라이브러리 (Data Visualization)

### Python 라이브러리

**seaborn 0.12.0+**
- 통계적 데이터 시각화
- 히트맵 생성
- 색상 팔레트

**matplotlib 3.7.0+**
- 기본 차트 라이브러리
- 데이터 플로팅
- 이미지 저장

---

## 의존성 관리 (Dependency Management)

### 패키지 관리

**pip**
- Python 패키지 매니저
- requirements.txt 기반 설치
- 가상 환경 지원

**가상 환경**
- venv
- 가상 환경 격리
- 프로젝트별 의존성

---

## 개발 도구 (Development Tools)

### 버전 관리

**Git**
- 분산 버전 관리
- GitHub 연동
- Conventional Commits

### 프로젝트 설정

**pyproject.toml**
- 프로젝트 메타데이터
- Ruff 설정
- Mypy 설정
- Pytest 설정

---

## 시스템 요구사항 (System Requirements)

### Python 버전
- **최소**: Python 3.11
- **권장**: Python 3.11 또는 3.12

### 데이터베이스
- CSV 파일 기반 데이터 스토리지
- 선택적 Redis 캐시

### API 키
- Google Gemini API Key (선택)
- OpenAI API Key (선택)
- FRED API Key (선택)

---

## 환경 변수 (Environment Variables)

```env
# Flask 설정
FLASK_ENV=development
LOG_LEVEL=INFO
PORT=5001

# API 키
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
FRED_API_KEY=your_fred_api_key

# 데이터 설정
DATA_DIR=./us_market/data

# 보안 설정
CORS_ENABLED=True
RATE_LIMIT_ENABLED=True
RATE_LIMIT_DEFAULT=100 per minute
```

---

## 성능 최적화 (Performance Optimization)

### 캐싱 전략
- TTL 기반 캐싅 (기본 5분)
- 메모리 캐시 또는 Redis
- 선택적 캐시 무효화

### Rate Limiting
- IP 기반 요청 제한
- 과부하 방지
- 공정한 자원 분배

### 비동기 처리
- 비동기 작업 큐 (계획 중)
- 백그라운드 데이터 업데이트
- 장기 실행 작업 분리

---

## 보안 고려사항 (Security Considerations)

### 보안 헤더
- CORS 정책
- Content Security Policy (계획 중)
- HTTPS 강제 (Production)

### 비밀 정보 관리
- 환경변수 기반 설정
- .env 파일 Git 제외
- API 키 암호화

### 입력 검증
- Pydantic 스키마 검증
- 티커 심볼 검증
- SQL Injection 방지
- XSS 방지

---

## 모니터링 (Monitoring)

### Health Check
- `/health` 엔드포인트
- 컴포넌트 상태 확인
- API 연결 상태

### 로깅
- Structlog JSON 로그
- 로그 레벨별 필터링
- 에러 트래킹

---

**@SPEC:TECH-001** - 기술 스택 문서
**@SPEC:IMPROVE-001** - 커버리지 향상 완료 (87% 달성)
**최종 업데이트**: 2026-02-27
