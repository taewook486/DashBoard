# API 라우팅 수정 및 인코딩 문제 해결

**날짜**: 2026-02-14
**작업자**: MoAI
**상태**: 완료 ✅

---

## 문제 개요

미국 주식 시스템 대시보드에서 3개 API 엔드포인트가 오류를 반환하는 문제를 해결했습니다.

### 발생한 오류

| 엔드포인트 | HTTP 상태코드 | 원인 |
|-----------|--------------|------|
| `/api/us/smart-money` | 500 Internal Server Error | JSON 파일 인코딩 불일치 |
| `/api/us/sector-heatmap` | 404 Not Found | 라우팅 네이밍 불일치 |
| `/api/us/options-flow` | 404 Not Found | 라우팅 네이밍 불일치 |

---

## 상세 분석

### 1. `/api/us/smart-money` - 500 Internal Server Error

**증상**:
```
GET http://localhost:5001/api/us/smart-money 500 (INTERNAL SERVER ERROR)
```

**원인 분석**:
- `us_market/smart_money_current.json` 파일이 CP949 (EUC-KR) 인코딩으로 저장됨
- Python `json.load()` 함수가 UTF-8을 기대으로 작동하여 파일 읽기 실패
- 원인 데이터가 한국어 포함되어 있었음

**해결 방안**:
```python
# 인코딩 변환 스크립트
with open(src, 'r', encoding='cp949') as f:
    data = json.load(f)
with open(src, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

---

### 2. `/api/us/sector-heatmap` & `/api/us/options-flow` - 404 Not Found

**증상**:
```
GET http://localhost:5001/api/us/sector-heatmap 404 (NOT FOUND)
GET http://localhost:5001/api/us/options-flow 404 (NOT FOUND)
```

**원인 분석**:
- 프론트엔드에서 하이픈(`-`)을 사용한 URL 호출: `sector-heatmap`, `options-flow`
- Flask 서버는 언더스코어(`_`)를 사용한 라우팅 등록: `sector_heatmap`, `options_flow`
- URL 네이밍 규칙 불일치로 라우팅 매칭 실패

**해결 방안**:
1. Flask 서버 라우팅을 하이픈 → 언더스코어로 통일
2. 프론트엔드 API 호출 경로를 언더스코어로 변경

---

## 수정 파일 목록

### 1. `flask_app.py`

**변경 내용**:
- L713: `@app.route("/api/us/sector_heatmap")` (하이픈 → 언더스코어)
- L729: `@app.route("/api/us/options_flow")` (하이픈 → 언더스코어)

### 2. `templates/index.html`

**변경 내용**:
- `sector_heatmap` API 호출 경로 수정
- `options_flow` API 호출 경로 수정

### 3. `us_market/smart_money_current.json`

**변경 내용**:
- CP949 → UTF-8 인코딩 변환
- 백업 파일 생성: `smart_money_current.json.backup`

---

## 검증 결과

### 브라우저 콘솔 확인

| 엔드포인트 | 이전 상태 | 현재 상태 |
|-----------|----------|----------|
| `/api/us/smart-money` | 500 Error | ✅ 200 OK |
| `/api/us/sector-heatmap` | 404 Error | ✅ 200 OK |
| `/api/us/options-flow` | 404 Error | ✅ 200 OK |

### 서버 로그

```
127.0.0.1 - - [14/Feb/2026 12:34:56] "GET /api/us/smart-money HTTP/1.1" 200 -
127.0.0.1 - - [14/Feb/2026 12:34:57] "GET /api/us/sector_heatmap HTTP/1.1" 200 -
127.0.0.1 - - [14/Feb/2026 12:34:58] "GET /api/us/options_flow HTTP/1.1" 200 -
```

---

## 배포 정보

### 서버 재시작

```bash
# Windows 환경
Ctrl+C
python flask_app.py

# 또는 작업 관리자에서 프로세스 종료 후 재시작
```

### 프로세스 확인

```bash
# 실행 중인 Python 프로세스 확인
tasklist | findstr python

# 필요시 강제 종료
taskkill /PID <프로세스ID> /F
```

---

## 교� 사항

1. **URL 네이밍 규칙**: 하이픈과 언더스코어를 혼용하지 말고 통일된 규칙 사용
2. **인코딩 선언**: UTF-8을 표준으로 사용, 한국어 포함 파일은 명시적으로 인코딩 지정
3. **API 문서화**: 프론트엔드-백엔드 API 경로를 문서화하고 일관성 유지

---

## Git 커밋

```bash
commit daee382
Author: MoAI <email@mo.ai.kr>
Date:   Fri Feb 14 12:35:00 2026 +0900

    fix: API 라우팅 일관성 수정 및 인코딩 문제 해결

    - flask_app.py: sector-heatmap, options-flow 라우팅을 언더스코어로 변경
    - templates/index.html: 프론트엔드 API 호출 경로를 언더스코어로 변경
    - us_market/smart_money_current.json: CP949 → UTF-8 인코딩 변환
```

---

## 첨크리스트

- [x] API 라우팅 일관성 확인
- [x] 인코딩 문제 해결
- [x] 프론트엔드 API 호출 경로 수정
- [x] 서버 재시작 후 동작 확인
- [x] Git 커밋 완료
- [x] 작업 문서화 완료

---

**문서 버전**: 1.0.0
**최종 수정일**: 2026-02-14
**승인자**: MoAI
