# 📊 FinAssistant AI - 시계열 데이터 기반 맞춤형 AI 비서

> **"내 주가 데이터를 이해하고, 근거 있는 분석을 제공하는 나만의 금융 AI 어시스턴트"**  
> 본 프로젝트는 삼성전자(005930.KS)의 1년 시계열 종가 데이터를 수집·분석하여 Firebase Firestore에 저장하고, 실시간 데이터 통계 요약을 **Google Gemini AI**의 시스템 프롬프트에 동적으로 주입(Context Injection)하여 지능적인 맞춤형 상담을 제공하는 풀스택 웹 애플리케이션입니다.

---

## 📑 목차
1. [서비스 소개 (해결하고자 하는 문제)](#1-서비스-소개-해결하고자-하는-문제)
2. [핵심 기능 및 결과물](#2-핵심-기능-및-결과물)
3. [기술 스택](#3-기술-스택)
4. [아키텍처 및 설계 원리](#4-아키텍처-및-설계-원리)
5. [API 엔드포인트 명세](#5-api-엔드포인트-명세)
6. [로컬 실행 가이드](#6-로컬-실행-가이드)
7. [환경 변수 설정 (.env)](#7-환경-변수-설정-env)
8. [배포 안내 (Render & Vercel)](#8-배포-안내-render--vercel)
9. [제출용 스크린샷 가이드](#9-제출용-스크린샷-가이드)

---

## 1. 🌟 서비스 소개 (해결하고자 하는 문제)

일반적인 범용 ChatGPT나 Gemini는 사용자의 최신 데이터나 특정 시점의 종가 정보를 알지 못합니다. "최근 주가 최고가가 얼마였지?" 또는 "이번 달 주가 트렌드가 어때?"라고 물어보면 일반론적이거나 과거 학습 데이터에 의존한 답변만 돌아옵니다.

**FinAssistant AI**는 다음과 같은 방식으로 이 문제를 완벽히 해결합니다:
1. **시계열 데이터 실시간 집계**: 수집된 주가 데이터를 분석하여 기간, 총 레코드 수, 통계 지표(평균/최고/최저), 최근 추세(변동률)를 자동 산출합니다.
2. **컨텍스트 주입 (Context Injection)**: 산출된 요약 통계를 Gemini 모델의 `system_instruction`에 동적으로 삽입하여, AI가 실제 수치를 근거로 한 팩트 기반의 정확한 맞춤형 답변을 제공합니다.
3. **직관적인 데이터 제어 (CRUD)**: 웹 화면에서 시계열 주가 데이터를 직접 등록, 수정, 삭제할 수 있으며, 데이터 변경 즉시 AI의 분석 컨텍스트에 실시간 반영됩니다.
4. **대화 이력 영구 보존**: 상담 세션을 Firestore에 자동 저장하고, 필요 시 언제든 이전 상담 내역을 다시 불러와 대화를 이어갈 수 있습니다.
5. **보너스 과제 달성 (다크 모드)**: 장시간 데이터 분석 시 눈의 피로를 덜어주는 감각적인 다크/라이트 테마 전환 기능을 탑재했습니다.

---

## 2. 🎯 핵심 기능 및 결과물

| 기능 | 입력 및 요청 | 출력 및 화면 동작 |
| :--- | :--- | :--- |
| **1. 데이터 기반 AI 채팅** | 사용자의 자연어 질문 | Firestore 데이터 요약(통계/추세)이 주입된 Gemini의 맞춤형 답변 + 실시간 로딩 인디케이터 |
| **2. 데이터 관리 (CRUD)** | `(date, value, memo)` 데이터 추가 / 수정 / 삭제 | 실시간 테이블 목록 갱신, 상단 통계 대시보드 자동 재계산, 수정 모달 인터랙션 |
| **3. 대화 기록 관리** | 대화 자동/수동 저장, 목록 조회, 특정 대화 클릭 | 이전 상담 이력 목록 표시, 선택한 세션의 전체 메시지 말풍선 복원 및 삭제 |
| **4. 보너스 과제: 다크 모드** | 헤더 우측 테마 토글 버튼 클릭 (🌙 / ☀️) | CSS Custom Properties 기반 실시간 테마 전환 및 `localStorage` 영구 유지 |
| **5. 배포 및 문서화** | Render(백엔드), Vercel(프론트엔드) 접속 | Swagger UI(`/docs`) 제공, CORS 및 환경 변수 분리 운영 |

---

## 3. 🛠️ 기술 스택 (Tech Stack)

```
[ Frontend: Vanilla HTML/CSS/JS ]  <--- REST API (Fetch) --->  [ Backend: FastAPI (Python 3.14) ]
                                                                      │
                                                ┌─────────────────────┴─────────────────────┐
                                                ▼                                           ▼
                                   [ Firebase Firestore (NoSQL) ]              [ Google Gemini API (LLM) ]
                                   - data (시계열 종가 데이터)                    - gemini-3.5-flash
                                   - conversations (대화 세션)                  - System Context Injection
```

- **Backend**: Python 3.14+, FastAPI, Uvicorn, Pydantic v2
- **Frontend**: Vanilla HTML5, CSS3 (Modern Flex/Grid, CSS Variables), JavaScript (ES6+ Fetch API) - *프레임워크 미사용*
- **Database**: Google Cloud Firebase Firestore (`data`, `conversations` 컬렉션)
- **AI / LLM**: Google GenAI SDK (`google-genai`), `gemini-3.5-flash` 모델
- **Data Collection**: `yfinance`, `pandas` (삼성전자 245거래일 종가 수집)
- **Deployment**: Render (백엔드 Web Service), Vercel (프론트엔드 정적 호스팅)

---

## 4. 🧠 아키텍처 및 설계 원리

### 1) 시계열 데이터 요약 및 컨텍스트 주입 (Context Injection)
AI 비서가 정확한 통계를 말할 수 있도록 사용자의 질문이 들어올 때마다 다음 파이프라인이 실행됩니다:
1. `compute_summary()`가 Firestore의 전체 데이터를 조회하여 기본 통계 산출:
   - **기간**: 시작 거래일 ~ 종료 거래일 (`2025-10-30 ~ 2026-10-30`)
   - **총 레코드 수**: 245개
   - **핵심 지표**: 평균가, 최고가, 최저가, 총합
   - **최근 트렌드**: 최근 30거래일 변동률 기반 추세 분석 (상승/하락/보합)
2. 아래 형식으로 Gemini의 `system_instruction`에 주입:
   ```text
   당신은 사용자의 금융/주식 데이터를 깊이 있게 분석하고 친절히 설명하는 전문 AI 데이터 비서입니다.

   [사용자 데이터 요약]
   - 데이터 기간: {period}
   - 총 레코드: {count}개
   - 주요 지표: 합계: {total}, 평균: {average}, 최고가: {max}, 최저가: {min}
   - 최근 트렌드: {trend}

   위 데이터를 기반으로 사용자의 질문에 전문적이고 친절한 맞춤형 답변을 한국어로 제공하세요.
   ```
3. Gemini는 주입된 요약 지표를 바탕으로 오차 없는 구체적 수치로 답변을 반환합니다.

### 2) FastAPI 계층화 아키텍처 (Layered Architecture)
유지보수성과 가독성을 위해 역할을 엄격히 분리했습니다:
- **`routers/`**: HTTP 요청 처리, 파라미터 매핑, 상태 코드 반환 (`data_router`, `chat_router`, `conversation_router`)
- **`services/`**: 순수 비즈니스 로직 및 외부 연동 (`data_service`: 시계열 통계 계산, `chat_service`: Gemini API 호출 및 프롬프트 주입)
- **`schemas.py`**: Pydantic 스키마를 통한 입력값 검증(Validation) 및 응답 직렬화(Serialization)
- **`firebase_db.py`**: Firestore 데이터베이스 CRUD 연산 캡슐화 (키 미등록 시 로컬 메모리 폴백 지원)

### 3) Firestore NoSQL 데이터 모델링
- **`data` 컬렉션**:
  - `date` (string, `YYYY-MM-DD`): 거래일
  - `value` (number): 수정 종가 (소수점 2자리)
  - `memo` (string): 데이터 메모 (예: "삼성전자 종가")
- **`conversations` 컬렉션**:
  - `title` (string): 대화 제목 (사용자 첫 질문 요약)
  - `created_at` (string, ISO 8601): 생성 일시
  - `messages` (array of objects): `[{"role": "user"|"assistant", "content": "..."}]`

---

## 5. 📡 API 엔드포인트 명세

### 1) 시계열 데이터 API (`/api/data`)
| 메서드 | 엔드포인트 | 설명 |
| :---: | :--- | :--- |
| **GET** | `/api/data/summary` | 데이터 요약 정보(기간, 개수, 평균/최고/최저, 트렌드) 조회 |
| **GET** | `/api/data` | 저장된 모든 주가 데이터 목록 조회 (날짜 오름차순) |
| **POST** | `/api/data` | 새 데이터 추가 `{"date": "YYYY-MM-DD", "value": 75000.0, "memo": "..."}` |
| **PUT** | `/api/data/{id}` | 특정 ID의 데이터 수정 |
| **DELETE** | `/api/data/{id}` | 특정 ID의 데이터 삭제 |

### 2) AI 대화 API (`/api/chat`)
| 메서드 | 엔드포인트 | 설명 |
| :---: | :--- | :--- |
| **POST** | `/api/chat` | 데이터 요약 주입 기반 Gemini AI 질의응답 및 대화 자동 저장 |

### 3) 대화 기록 API (`/api/conversations`)
| 메서드 | 엔드포인트 | 설명 |
| :---: | :--- | :--- |
| **GET** | `/api/conversations` | 저장된 대화 목록 조회 (최신순) |
| **GET** | `/api/conversations/{id}` | 특정 대화의 전체 메시지(messages) 불러오기 |
| **POST** | `/api/conversations` | 대화 세션 저장 |
| **DELETE** | `/api/conversations/{id}` | 대화 세션 삭제 |

### 4) 시스템 헬스체크 (`/api/health`)
- 서버 상태, Firestore 연결 여부, Gemini API 설정 여부 반환

---

## 6. 💻 로컬 실행 가이드

### 1) 패키지 설치
```bash
pip install -r requirements.txt
```

### 2) 환경 변수 파일(`.env`) 설정
프로젝트 루트 경로에 `.env` 파일을 생성하고 아래 내용을 입력합니다:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash
FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json
ALLOWED_ORIGINS=*
PORT=8000
```
*(Firebase 서비스 계정 키 파일 `serviceAccountKey.json`을 프로젝트 루트에 위치시킵니다.)*

### 3) 시계열 데이터 수집 및 Firestore 적재 (최초 1회)
```bash
# 1. 삼성전자 최근 1년 주가 데이터 수집 (data_samsung.json 생성)
python collect_stock.py

# 2. Firestore에 245개 종가 데이터 일괄 적재 (Batch Seeding)
python seed_data.py
```

### 4) 로컬 웹 서버 실행
```bash
python -m uvicorn main:app --reload
```
*(또는 `python main.py`)*

- 브라우저 접속: **[http://localhost:8000](http://localhost:8000)**
- API 문서 (Swagger UI): **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 7. 🔑 환경 변수 목록 (.env)

| 변수명 | 필수 여부 | 설명 | 예시 |
| :--- | :---: | :--- | :--- |
| `GEMINI_API_KEY` | **필수** | Google AI Studio에서 발급받은 Gemini API 키 | `AIzaSy...` |
| `GEMINI_MODEL` | 선택 | 사용할 Gemini 모델명 (기본: `gemini-3.5-flash`) | `gemini-3.5-flash` |
| `FIREBASE_CREDENTIALS_PATH` | 선택 | 로컬 서비스 계정 JSON 키 경로 | `serviceAccountKey.json` |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | 선택 (배포용) | Render 등 클라우드 배포 시 JSON 키 내용 전체 문자열 | `{"type": "service_account", ...}` |
| `ALLOWED_ORIGINS` | 선택 | CORS 허용 도메인 목록 (쉼표 구분 또는 `*`) | `https://your-app.vercel.app` |
| `PORT` | 선택 | 서버 바인딩 포트 (기본값: `8000`) | `8000` |

---

## 8. 🚀 배포 안내 (Render & Vercel)

### 1) 백엔드 배포 (Render Web Service)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `GEMINI_API_KEY`: Google AI Studio 키
  - `FIREBASE_SERVICE_ACCOUNT_JSON`: `serviceAccountKey.json` 내용 전체를 한 줄 텍스트로 등록
  - `ALLOWED_ORIGINS`: Vercel 프론트엔드 도메인 주소 등록
- **배포 확인**: `https://your-backend.onrender.com/docs`에서 Swagger UI 정상 호출 확인

> ⚠️ **Render 무료 티어 슬립 모드(Cold Start) 대응**:  
> Render 무료 티어는 약 15분간 요청이 없으면 서버가 대기 상태(Sleep)로 전환됩니다. 첫 접속 시 30초~1분 정도의 응답 지연이 발생할 수 있으니 화면 로딩 스피너를 보며 잠시 대기해 주시기 바랍니다.

### 2) 프론트엔드 배포 (Vercel)
- GitHub 저장소를 Vercel에 연결하고 Root Directory를 `frontend`로 지정하거나 정적 배포를 진행합니다.
- `frontend/app.js` 상단의 `API_BASE_URL`이 배포된 백엔드 Render URL(`https://your-backend.onrender.com`)을 가리키도록 설정합니다.

### 3) 배포 URL
- **프론트엔드 서비스 URL**: `https://your-app.vercel.app` *(배포 후 업데이트)*
- **백엔드 API URL**: `https://your-backend.onrender.com` *(배포 후 업데이트)*
- **Swagger UI (API 문서)**: `https://your-backend.onrender.com/docs`

---

## 9. 📸 제출용 스크린샷 가이드

과제 제출 시 아래 3가지 화면을 캡처하여 첨부합니다:

1. **데이터 요약이 보이는 채팅 화면**:  
   상단의 4개 요약 카드(기간, 개수, 평균 종가, 트렌드)가 노출된 상태에서, AI에게 주가 관련 질문을 입력하고 요약 수치가 반영된 맞춤형 답변을 받은 화면.
2. **데이터 관리 (CRUD) 화면**:  
   우측 패널의 데이터 테이블 목록과 함께 새 데이터를 추가하거나, 기존 데이터를 수정/삭제하는 모달이나 동작이 확인되는 화면.
3. **대화 기록 화면 (불러오기 동작)**:  
   상단 '이전 대화' 드롭다운에서 과거 상담 세션을 선택하여 이전 메시지 내역이 채팅창에 그대로 복원된 화면.
