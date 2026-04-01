# 프로젝트 설계 프롬프트 생성기 / Project Design Prompt Generator

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange)
![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-blueviolet)

**🤖 LangGraph 기반 AI 프롬프트 생성 플랫폼 / LangGraph-powered AI Prompt Generator**

> 이 프로젝트는 [SeMinKong/PromptGenerator_LangGraph](https://github.com/SeMinKong/PromptGenerator_LangGraph)의 이전 버전을 기반으로 고도화되었습니다.

AI와 대화하며 소프트웨어 프로젝트의 설계를 체계적으로 진행하고, 각 설계 영역별 **고도화된 AI 프롬프트를 자동 생성**하는 웹 애플리케이션입니다.

**Powered by [LangGraph](https://github.com/langchain-ai/langgraph) + [Upstage Solar Pro](https://console.upstage.ai)**

---

<details open>
<summary><h2>📌 한국어 문서 / Korean Documentation</h2></summary>

## 프로젝트 개요

**프로젝트 설계 프롬프트 생성기**는 LangGraph 기반의 AI 대화형 시스템으로, 소프트웨어 프로젝트의 설계 단계를 구조화된 대화를 통해 자동으로 진행합니다.

사용자가 프로젝트 설명을 입력하면, 시스템은 **6가지 설계 영역**(UI/UX, 아키텍처, 데이터베이스, API, 배포, 테스트)에서 Upstage Solar LLM을 활용해 각 영역별 맞춤형 질문을 던집니다. 사용자 답변을 수집한 후 최종적으로 **구현 가능한 설계 프롬프트**를 생성합니다.

**핵심 특징:**
- **병렬 처리**: 6개 영역을 동시에 진행 (모든 영역이 독립적으로 작동)
- **대화형 설계**: 각 영역마다 최대 3라운드의 질문-답변 사이클
- **최종 문서 생성**: 모든 영역 완료 후 통합 마크다운 설계 문서 생성
- **실시간 피드백**: WebSocket 기반 실시간 상태 업데이트
- **커스텀 영역 추가**: 기본 6개 영역 외에 사용자 정의 영역 추가 가능

---

### 기술 스택

| 계층 | 기술 | 용도 |
|------|------|------|
| **LLM** | Upstage Solar Pro | 대화형 설계 질문 생성 및 프롬프트 생성 |
| **아키텍처** | LangGraph | 상태 머신 기반 대화 흐름 제어 |
| **웹 프레임워크** | FastAPI | 비동기 HTTP/WebSocket 서버 |
| **실시간 통신** | WebSocket | 클라이언트-서버 양방향 통신 |
| **LLM 통합** | LangChain | Upstage API 통합 레이어 |
| **프론트엔드** | Vanilla JS/HTML/CSS | 대화형 UI (3패널 레이아웃) |
| **컨테이너** | Docker | 배포 환경 표준화 |
| **서버** | Uvicorn | ASGI 서버 |
| **언어** | Python 3.11+ | 백엔드 런타임 |

---

### 주요 기능

1. **프로젝트 초기화**: 프로젝트 설명과 진행할 설계 영역 선택
2. **영역별 병렬 진행**: 6개 영역이 독립적으로 3라운드 대화
3. **적응형 질문**: LLM이 사용자 답변을 분석해 다음 질문 자동 생성
4. **프롬프트 추출**: 각 영역에서 최종 설계 프롬프트 자동 생성
5. **통합 문서 생성**: 모든 영역의 프롬프트를 하나의 마크다운 문서로 통합
6. **영역 커스터마이징**: 기본 6개 외에 사용자가 정의한 설계 영역 추가 가능
7. **실시간 진행 현황**: WebSocket으로 각 영역의 진행 상태 실시간 표시
8. **프롬프트 미리보기**: 우측 패널에서 생성된 프롬프트 실시간 확인 및 복사

---

### 사용자 가이드

#### 1단계: API 키 입력

앱을 시작하면 **API 키 입력 모달**이 표시됩니다.

- **입력 필드**: `up_xxxxxxxxxxxx` 형식의 Upstage API 키
- **소스**: 환경변수 `UPSTAGE_API_KEY` 또는 모달에서 직접 입력
- **처리**: 키를 제출하면 백엔드가 세션을 생성하고 WebSocket 연결 수립

```
┌─────────────────────────────────┐
│    🔑 API 키 입력               │
│                                 │
│  [up_xxxxxxxxxxxxx]             │
│                                 │
│         [ 시작하기 ]             │
└─────────────────────────────────┘
```

#### 2단계: 프로젝트 설명 및 영역 선택

왼쪽 패널에 다음을 입력합니다:

- **프로젝트 설명**: 만들고자 하는 프로젝트를 자유롭게 설명
  > 예: "음식 배달 앱을 만들고 싶어. 맛집 검색, 주문, 배달 추적 기능이 필요해"

- **설계 영역 선택**: 체크박스로 진행할 영역 선택 (기본: 6개 모두 선택)
  - 🎨 UI/UX 디자인
  - 🏗️ 시스템 아키텍처
  - 🗄️ 데이터베이스 설계
  - 🔌 API 설계
  - 🚀 배포 전략
  - ✅ 테스트 전략

```
┌─── 왼쪽 패널 ───────────────────┐
│ 프로젝트 설명                   │
│ [여러 줄 텍스트 입력]            │
│                                 │
│ 설계 영역 선택      [모두 선택]   │
│ ☑ 🎨 UI/UX 디자인             │
│ ☑ 🏗️ 시스템 아키텍처           │
│ ☑ 🗄️ 데이터베이스 설계         │
│ ☑ 🔌 API 설계                  │
│ ☑ 🚀 배포 전략                │
│ ☑ ✅ 테스트 전략               │
│                                 │
│     [ 설계 시작 → ]              │
└─────────────────────────────────┘
```

#### 3단계: 영역별 대화 진행

**설계 시작** 버튼을 클릭하면:

1. **프로젝트 준비** - 서버가 선택된 영역들을 초기화
2. **병렬 진행** - 모든 영역이 동시에 첫 번째 라운드 질문 시작
3. **탭 전환** - 중앙 패널의 탭을 클릭해 각 영역의 대화 확인
4. **답변 입력** - 각 영역별로 LLM의 질문에 답변 입력
5. **라운드 진행** - 최대 3라운드까지 자동 진행

**예시 대화 흐름:**

```
[ 탭 1: 🎨 UI/UX 디자인 ] [ 탭 2: 🏗️ 아키텍처 ] [ 탭 3: ... ]

┌─── 중앙 패널 (대화 영역) ──────────┐
│                                    │
│ AI: 안녕하세요! UI/UX 설계 전문가  │
│     입니다. 몇 가지 질문을 하겠습니다:
│     1. 타겟 사용자는 누구인가요?   │
│     2. 모바일 우선인가요?          │
│     3. 색상 스타일 선호도는?      │
│                                    │
│                                    │
│ 사용자: 20~40대 직장인 대상        │
│        모바일 우선                 │
│        간결하고 모던한 스타일      │
│                                    │
│ AI: 감사합니다! 다음 질문:        │
│     ...                            │
│                                    │
│  [                    ] [ 전송 ]   │
│  (사용자 입력 필드)                 │
└─────────────────────────────────────┘
```

#### 4단계: 프롬프트 미리보기

오른쪽 패널 **📋 프롬프트 미리보기**:

- 각 영역의 진행 상황에 따라 실시간으로 생성된 프롬프트 표시
- 완료된 영역의 프롬프트를 선택하면 미리보기 갱신
- **복사 버튼** - 프롬프트를 클립보드에 복사 가능

```
┌──── 오른쪽 패널 ─────────────┐
│ 📋 프롬프트 미리보기          │
│                              │
│ [생성된 프롬프트 텍스트]       │
│ 당신은 UI/UX 디자인 전문가...  │
│ ...                           │
│                              │
│     [ 복사 ]                  │
└──────────────────────────────┘
```

#### 5단계: 진행 현황 모니터링

왼쪽 패널 **설계 진행 현황**:

- 각 영역의 상태를 실시간으로 표시
- **대기** (⚪) - 아직 시작하지 않음
- **진행 중** (🟡) - 현재 질문-답변 진행 중
- **완료** (🟢) - 최종 프롬프트 생성 완료

```
설계 진행 현황
┌──────────────────────────┐
│ 🎨 UI/UX 디자인      [완료] │
│ 🏗️ 시스템 아키텍처   [진행중] │
│ 🗄️ 데이터베이스 설계 [완료] │
│ 🔌 API 설계          [완료] │
│ 🚀 배포 전략         [대기] │
│ ✅ 테스트 전략       [대기] │
└──────────────────────────┘
```

#### 6단계: 최종 문서 생성

모든 영역이 완료되면 **📄 최종 문서 생성** 버튼이 활성화됩니다:

- 클릭하면 서버가 모든 영역의 프롬프트를 수집
- LLM이 통합 마크다운 설계 문서 생성
- 완성된 문서가 우측 패널에 표시
- **복사**해서 AI 모델에 입력하여 구현 시작

```
생성된 최종 문서:

# 프로젝트 설계 문서: 음식 배달 앱

## 프로젝트 개요
사용자 중심의 음식 배달 플랫폼으로...

## 각 영역별 설계 프롬프트

### UI/UX 디자인
당신은 UI/UX 디자인 전문가입니다.
타겟 사용자는 20~40대 직장인...

### 시스템 아키텍처
당신은 소프트웨어 아키텍처 전문가입니다.
마이크로서비스 아키텍처 기반으로...

### ... (각 영역별 프롬프트)

## 통합 고려사항
각 영역 간의 연계점을 고려할 때...
```

---

### "설계 영역(Dimension)"이란?

**설계 영역**은 소프트웨어 프로젝트를 성공적으로 구현하기 위해 고려해야 할 **서로 다른 관점**입니다.

#### 기본 6개 영역

| 영역 | 아이콘 | 설명 |
|------|--------|-----|
| **UI/UX 디자인** | 🎨 | 사용자가 상호작용하는 인터페이스 설계<br>페르소나, 사용자 여정, 화면 구성, 디자인 시스템 |
| **시스템 아키텍처** | 🏗️ | 전체 기술 구조와 시스템 조직<br>아키텍처 패턴, 기술 스택, 컴포넌트 설계 |
| **데이터베이스 설계** | 🗄️ | 데이터를 저장하고 관리하는 방식<br>데이터 모델, 스키마, 성능, 백업 전략 |
| **API 설계** | 🔌 | 서로 다른 시스템 간 통신 인터페이스<br>REST/GraphQL 선택, 엔드포인트, 인증 방식 |
| **배포 전략** | 🚀 | 애플리케이션을 프로덕션에 올리는 방식<br>호스팅, CI/CD, 컨테이너화, 모니터링 |
| **테스트 전략** | ✅ | 품질 보증 계획<br>테스트 유형, 커버리지, 자동화, QA 프로세스 |

#### 커스텀 영역 추가

기본 영역 외에 프로젝트 특성에 맞는 새로운 영역을 추가할 수 있습니다.

**예:**
- 🔒 보안 설계 (사이버보안, 인증, 데이터 암호화 등)
- 📊 분석 및 대시보드 설계
- 🌐 다국어/국제화 (i18n)
- 👥 사용자 관리 및 권한 설계

중앙 패널의 **＋ 버튼**으로 언제든지 새 영역을 추가할 수 있습니다.

---

### 생성된 프롬프트 활용 방법

최종 문서로 생성된 프롬프트는 **AI 모델(ChatGPT, Claude, Gemini 등)에 입력**하여 구현을 시작합니다.

#### 예시 사용 흐름

```
1️⃣ 이 도구로 설계 프롬프트 생성
   ↓
2️⃣ 최종 문서 복사
   ↓
3️⃣ ChatGPT/Claude에 입력
   "다음 설계를 바탕으로 코드를 구현해줄래?"
   ↓
4️⃣ AI가 프로젝트 구조 및 구현 코드 생성
   ↓
5️⃣ 생성된 코드를 개발 환경에서 수정/보완
```

---

## 🔧 개발자 가이드

### 사전 요구사항

- **Python 3.11 이상**
- **pip** (Python 패키지 관리자)
- **Upstage API 키** (https://console.upstage.ai 에서 발급)
- **Docker** (선택사항, 컨테이너 배포용)

### 설치 방법

#### 1. 저장소 클론
```bash
git clone <repository-url>
cd ProjectPromptGenerator_LangGraph
```

#### 2. Python 가상 환경 생성 및 활성화
```bash
# 가상 환경 생성
python3 -m venv venv

# 활성화 (Linux/macOS)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate
```

#### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

#### 4. 환경 변수 설정
`.env` 파일을 생성하거나 환경변수로 설정합니다:

```bash
# .env 파일 생성
echo "UPSTAGE_API_KEY=up_xxxxxxxxxxxx" > .env

# 또는 환경변수로 직접 설정 (Linux/macOS)
export UPSTAGE_API_KEY="up_xxxxxxxxxxxx"

# 또는 Windows
set UPSTAGE_API_KEY=up_xxxxxxxxxxxx
```

### 환경 변수

| 변수명 | 필수 | 기본값 | 설명 |
|--------|------|--------|------|
| `UPSTAGE_API_KEY` | ✅ | - | Upstage API 키 (https://console.upstage.ai) |
| `PORT` | ❌ | 8000 | 서버 포트 |
| `LOG_LEVEL` | ❌ | INFO | 로깅 레벨 (DEBUG, INFO, WARNING, ERROR) |
| `HOST` | ❌ | 127.0.0.1 | 바인드 호스트 (0.0.0.0 권장) |

---

### 실행 명령어

#### 로컬 개발 (uvicorn 직접 실행)

```bash
# 기본 실행 (포트 8000)
uvicorn server.app:app --reload

# 특정 포트 지정
uvicorn server.app:app --reload --port 8080

# 모든 인터페이스에서 수신 (원격 접속 허용)
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
```

**`--reload` 플래그:**
- 코드 변경 시 자동 재시작
- 개발 환경에서만 사용
- 프로덕션에서는 제거

#### 프로덕션 실행

```bash
# 워커 4개로 실행 (프로덕션)
uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 4

# Gunicorn + uvicorn 조합 (권장)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server.app:app
```

---

### Docker 실행

#### Docker로 빌드 및 실행

```bash
# 이미지 빌드
docker build -t prompt-generator .

# 컨테이너 실행 (환경변수 전달)
docker run -p 8000:8000 \
  -e UPSTAGE_API_KEY="up_xxxxxxxxxxxx" \
  prompt-generator
```

#### Docker Compose 사용 (선택사항)

`docker-compose.yml` 파일 생성:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      UPSTAGE_API_KEY: ${UPSTAGE_API_KEY}
      PORT: 8000
    restart: unless-stopped
```

실행:

```bash
# .env 파일 생성 후
docker-compose up

# 백그라운드 실행
docker-compose up -d
```

---

### 프로젝트 구조

```
ProjectPromptGenerator_LangGraph/
├── server/
│   ├── app.py                 # FastAPI 메인 애플리케이션
│   ├── graph_runner.py        # 영역별 대화 처리
│   ├── session.py             # 세션 상태 관리
│   └── ws_handler.py          # WebSocket 메시지 형식
├── dimensions/
│   ├── __init__.py
│   └── runner.py              # 개별 영역 LLM 호출
├── prompts/
│   ├── __init__.py
│   └── dimension_prompts.py   # 각 영역별 시스템 프롬프트
├── frontend/
│   ├── index.html             # HTML 레이아웃
│   ├── app.js                 # 프론트엔드 로직
│   └── style.css              # 스타일
├── state.py                   # 상태 정의 (TypedDict)
├── llm.py                     # LLM 초기화
├── requirements.txt           # Python 의존성
├── Dockerfile                 # Docker 빌드 설정
└── README.md                  # 이 파일
```

#### 파일 설명

| 파일 | 역할 |
|------|------|
| **server/app.py** | FastAPI 애플리케이션 진입점<br>HTTP 엔드포인트(/api/session, /ws) 정의 |
| **server/graph_runner.py** | 대화 흐름 처리<br>각 영역의 turn 처리, 완료 판단, 최종 문서 생성 |
| **server/session.py** | In-memory 세션 저장소<br>각 사용자 세션의 상태 관리 |
| **server/ws_handler.py** | WebSocket 메시지 생성/파싱<br>클라이언트와의 통신 프로토콜 |
| **dimensions/runner.py** | LLM 호출 로직<br>각 영역의 질문 생성 및 완료 판단 |
| **prompts/dimension_prompts.py** | 각 영역별 시스템 프롬프트 정의<br>MAX_ROUNDS 상수 포함 |
| **state.py** | 프로젝트/영역 상태 정의 (TypedDict)<br>기본 영역 리스트 포함 |
| **llm.py** | Upstage Solar LLM 초기화 |
| **frontend/index.html** | 3패널 레이아웃 HTML |
| **frontend/app.js** | 상태 관리, 이벤트 처리, WebSocket 통신 |

---

### LangGraph 흐름 설명

이 프로젝트는 **함수 기반 상태 관리**로 각 영역별 대화를 제어합니다.

#### 상태 흐름 다이어그램

```
┌──────────────────────┐
│   클라이언트 (브라우저) │
│ 프로젝트 설명 입력    │
└──────────┬───────────┘
           │
           ▼ project_init 메시지
┌────────────────────────────────────┐
│  server/app.py - WebSocket Handler │
│  • store.init_project()             │
│  • handle_dimension_turn() × N      │
│    (병렬 실행)                      │
└────────────────────────────────────┘
           │
   ┌───────┼───────┐
   ▼       ▼       ▼
┌────┐ ┌────┐ ┌────┐
│Dim1│ │Dim2│ │Dim3│  (6개 영역 병렬)
│R1  │ │R1  │ │R1  │
└──┬─┘ └──┬─┘ └──┬─┘
   │      │      │
   ▼      ▼      ▼
┌────────────────────────────────────┐
│  dimensions/runner.py              │
│  • 시스템 프롬프트 로드             │
│  • 대화 이력 복원                  │
│  • LLM.invoke() → 응답 생성        │
│  • [GENERATE_PROMPT] 태그 확인     │
│    ├─ Round < MAX_ROUNDS → 질문    │
│    └─ Round >= MAX_ROUNDS → 프롬프트│
└────────────────────────────────────┘
   │      │      │
   └───────┼───────┘
           ▼
┌────────────────────────────────────┐
│  server/ws_handler.py              │
│  WebSocket 메시지 생성             │
│  • dimension_question              │
│  • dimension_complete              │
└────────────────────────────────────┘
           │
           ▼
    클라이언트: 답변 입력
    (반복: Round 2, 3)
           │
           ▼
    모든 라운드 완료
           │
           ▼
┌────────────────────────────────────┐
│  handle_finalize()                 │
│  • 모든 영역 프롬프트 수집         │
│  • LLM 호출 → 통합 문서 생성      │
│  • final_document 메시지 반환      │
└────────────────────────────────────┘
           │
           ▼
    클라이언트: 최종 설계 문서 표시
```

#### 핵심 상태 구조

```python
ProjectState = {
    "project_description": str,     # 프로젝트 설명
    "api_key": str,                 # API 키
    "dimensions": {                 # 영역별 상태
        "ux_design": {
            "id": str,
            "name": str,
            "messages": list,           # 대화 이력
            "status": "pending|in_progress|completed",
            "round": int,               # 현재 라운드
            "generated_prompt": str,    # 최종 프롬프트
        },
        ...
    },
    "final_output": str,            # 최종 문서
}
```

#### 라운드별 처리 로직

```python
# Round 1: 초기 질문
시스템 프롬프트 + 프로젝트 설명 → LLM → 질문 생성

# Round 2: 심화 질문
시스템 프롬프트 + 프로젝트 설명 + 대화 이력 + 사용자 답변 → LLM → 추가 질문

# Round 3: 최종 프롬프트
시스템 프롬프트 + 전체 대화 이력 + 최종 지시
→ LLM → [GENERATE_PROMPT] 태그 포함 설계 프롬프트 생성
```

---

### 세션 관리

#### 세션 저장소 (server/session.py)

```python
class SessionStore:
    def __init__(self):
        self._sessions: dict[str, ProjectState] = {}
        self._lock = asyncio.Lock()    # 동시성 안전
    
    # 세션 생성/조회/업데이트/삭제
    async def create_session(self, api_key: str) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = make_project_state(api_key)
        return session_id
```

**특징:**
- **In-memory 저장** - 빠른 접근
- **asyncio.Lock** - 동시 요청 안전성
- **UUID 기반 세션 ID** - 안전한 식별

#### 주의사항

- **메모리 누수**: 프로덕션에서는 세션 타임아웃 구현 필요
- **분산 시스템**: 여러 서버 운영 시 Redis/DB 기반 스토어로 변경 필요

---

### WebSocket 메시지 프로토콜

#### 클라이언트 → 서버 메시지

| 타입 | 필드 | 설명 |
|------|------|------|
| `project_init` | `content`, `dimensions` | 프로젝트 시작 |
| `dimension_message` | `dimension_id`, `content` | 답변 전송 |
| `add_dimension` | `config` | 영역 추가 |
| `remove_dimension` | `dimension_id` | 영역 삭제 |
| `start_dimension` | `dimension_id` | 영역 시작 |
| `finalize` | (없음) | 최종 문서 생성 |

#### 서버 → 클라이언트 메시지

| 타입 | 필드 | 설명 |
|------|------|------|
| `project_ready` | `dimensions`, `project_description` | 프로젝트 준비 완료 |
| `dimension_question` | `dimension_id`, `content`, `round` | 질문 수신 |
| `dimension_status` | `dimension_id`, `status` | 상태 변경 |
| `dimension_complete` | `dimension_id`, `prompt` | 영역 완료 |
| `all_complete` | (없음) | 모든 영역 완료 |
| `final_document` | `content` | 최종 문서 생성 |
| `error` | `message` | 오류 발생 |

---

### 새로운 설계 영역 추가 방법

#### 1단계: 영역 설정 추가 (state.py)

```python
DEFAULT_DIMENSIONS = [
    # ... 기존 6개 ...
    {"id": "security", "name": "보안 설계", "icon": "🔒"},
]
```

#### 2단계: 시스템 프롬프트 추가 (prompts/dimension_prompts.py)

```python
DIMENSION_PROMPTS = {
    # ... 기존 6개 ...
    "security": """
당신은 보안 전문가입니다. 프로젝트의 보안 설계를 담당합니다.

집중 영역:
- 인증/인가 전략
- 데이터 암호화
- 접근 제어
- 보안 감사

{base_instructions}
""".strip(),
}
```

#### 3단계: 프론트엔드 자동 로드

/api/dimensions/defaults 엔드포인트에서 자동으로 로드됩니다.

---

### Docker 사용법

#### 이미지 빌드 및 실행

```bash
# 빌드
docker build -t prompt-generator .

# 실행
docker run -p 8000:8000 \
  -e UPSTAGE_API_KEY="up_xxxxxxxxxxxx" \
  prompt-generator

# 백그라운드 실행
docker run -d \
  -p 8000:8000 \
  -e UPSTAGE_API_KEY="up_xxxxxxxxxxxx" \
  --name prompt-gen \
  prompt-generator
```

---

</details>

---

<details>
<summary><h2>📌 English Documentation</h2></summary>

## Project Overview

**Project Design Prompt Generator** is a LangGraph-based AI conversational system that automates the design phase of software projects through structured dialogue.

When users input a project description, the system uses Upstage Solar LLM to ask tailored questions across **6 design dimensions** (UI/UX, Architecture, Database, API, Deployment, Testing). After collecting user responses, it generates an **implementable design prompt**.

**Key Features:**
- **Parallel Processing**: All 6 dimensions work simultaneously (independent workflows)
- **Conversational Design**: Up to 3 Q&A rounds per dimension
- **Final Document Generation**: Integrated markdown design document after all dimensions complete
- **Real-time Feedback**: WebSocket-based live status updates
- **Custom Dimensions**: Add user-defined dimensions beyond the default 6

---

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **LLM** | Upstage Solar Pro | Conversational design questions & prompt generation |
| **Architecture** | LangGraph | State machine-based conversation flow control |
| **Web Framework** | FastAPI | Async HTTP/WebSocket server |
| **Real-time Communication** | WebSocket | Bidirectional client-server communication |
| **LLM Integration** | LangChain | Upstage API integration layer |
| **Frontend** | Vanilla JS/HTML/CSS | Interactive 3-panel UI |
| **Container** | Docker | Deployment standardization |
| **Server** | Uvicorn | ASGI server |
| **Language** | Python 3.11+ | Backend runtime |

---

### Key Features

1. **Project Initialization**: Input project description and select design dimensions
2. **Parallel Dimension Progress**: 6 dimensions progress independently through 3 Q&A rounds
3. **Adaptive Questions**: LLM analyzes user responses and generates next questions automatically
4. **Prompt Extraction**: Each dimension generates its final design prompt
5. **Integrated Document Generation**: Combines all dimension prompts into one markdown document
6. **Dimension Customization**: Add user-defined design dimensions beyond the default 6
7. **Real-time Status Updates**: WebSocket provides live progress tracking per dimension
8. **Prompt Preview**: Right panel shows generated prompts in real-time with copy functionality

---

### User Guide

#### Step 1: API Key Input

Upon app start, an **API Key Input Modal** appears.

- **Input Field**: Upstage API key in format `up_xxxxxxxxxxxx`
- **Source**: Environment variable `UPSTAGE_API_KEY` or direct input
- **Processing**: After submitting, backend creates session and establishes WebSocket connection

#### Step 2: Project Description & Dimension Selection

Input in left panel:

- **Project Description**: Describe your project freely
  > Example: "I want to build a food delivery app with restaurant search, ordering, and delivery tracking"

- **Design Dimensions**: Select dimensions via checkboxes (default: all 6)
  - 🎨 UI/UX Design
  - 🏗️ System Architecture
  - 🗄️ Database Design
  - 🔌 API Design
  - 🚀 Deployment Strategy
  - ✅ Testing Strategy

#### Step 3: Dimension-specific Conversation

Clicking **Start Design** button initiates:

1. **Project Preparation** - Server initializes selected dimensions
2. **Parallel Progress** - All dimensions simultaneously start first-round questions
3. **Tab Switching** - Click tabs in center panel to view each dimension's conversation
4. **Answer Input** - Respond to LLM questions for each dimension
5. **Round Progression** - Automatically advances through max 3 rounds

#### Step 4: Prompt Preview

**📋 Prompt Preview** in right panel:

- Shows real-time generated prompts as dimensions progress
- Updates when switching between completed dimensions
- **Copy Button** - Copy prompt to clipboard

#### Step 5: Progress Monitoring

**Design Progress** in left panel:

- Real-time status display for each dimension
- **Pending** (⚪) - Not yet started
- **In Progress** (🟡) - Q&A currently happening
- **Completed** (🟢) - Final prompt generated

#### Step 6: Final Document Generation

When all dimensions complete, **📄 Generate Final Document** button activates:

- Server collects prompts from all dimensions
- LLM generates integrated markdown design document
- Document displays in right panel
- **Copy** and use in your AI model to start implementation

---

### What are "Design Dimensions"?

**Design Dimensions** are **different perspectives** needed for successful software project implementation.

#### Default 6 Dimensions

| Dimension | Icon | Description |
|-----------|------|-------------|
| **UI/UX Design** | 🎨 | User-facing interface design<br>Personas, user journeys, screen layouts, design systems |
| **System Architecture** | 🏗️ | Overall technical structure and organization<br>Architecture patterns, tech stack, component design |
| **Database Design** | 🗄️ | Data storage and management approach<br>Data models, schemas, performance, backup strategy |
| **API Design** | 🔌 | Communication interface between systems<br>REST/GraphQL choice, endpoints, authentication |
| **Deployment Strategy** | 🚀 | How to push application to production<br>Hosting, CI/CD, containerization, monitoring |
| **Testing Strategy** | ✅ | Quality assurance planning<br>Test types, coverage, automation, QA processes |

#### Custom Dimensions

Add project-specific dimensions beyond the default 6:

**Examples:**
- 🔒 Security Design
- 📊 Analytics & Dashboard Design
- 🌐 Internationalization (i18n)
- 👥 User Management & Authorization

Use the **＋ button** in center panel to add custom dimensions anytime.

---

### Using Generated Prompts

The final document is designed to be **input into AI models** (ChatGPT, Claude, Gemini, etc.) to start implementation.

---

## 🔧 Developer Guide

### Prerequisites

- **Python 3.11 or higher**
- **pip** (Python package manager)
- **Upstage API key** (get from https://console.upstage.ai)
- **Docker** (optional, for container deployment)

### Installation

#### 1. Clone Repository
```bash
git clone <repository-url>
cd ProjectPromptGenerator_LangGraph
```

#### 2. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate          # Windows
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Set Environment Variables
```bash
export UPSTAGE_API_KEY="up_xxxxxxxxxxxx"
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `UPSTAGE_API_KEY` | ✅ | - | Upstage API key |
| `PORT` | ❌ | 8000 | Server port |
| `LOG_LEVEL` | ❌ | INFO | Logging level |
| `HOST` | ❌ | 127.0.0.1 | Bind host |

---

### Running the Application

#### Local Development
```bash
uvicorn server.app:app --reload
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
```

#### Production
```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 4
```

---

### Docker

#### Build and Run
```bash
docker build -t prompt-generator .
docker run -p 8000:8000 \
  -e UPSTAGE_API_KEY="up_xxxxxxxxxxxx" \
  prompt-generator
```

#### Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      UPSTAGE_API_KEY: ${UPSTAGE_API_KEY}
    restart: unless-stopped
```

---

### Project Structure

```
ProjectPromptGenerator_LangGraph/
├── server/
│   ├── app.py                 # FastAPI application
│   ├── graph_runner.py        # Conversation handling
│   ├── session.py             # Session management
│   └── ws_handler.py          # WebSocket protocol
├── dimensions/
│   └── runner.py              # LLM calls per dimension
├── prompts/
│   └── dimension_prompts.py   # System prompts
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── state.py                   # State definitions
├── llm.py                     # LLM initialization
├── requirements.txt
├── Dockerfile
└── README.md
```

---

### LangGraph Flow

The project uses **function-based state management** to control per-dimension conversations.

#### State Flow

```
Client Input
    ↓
project_init message
    ↓
Server: initialize all dimensions
    ↓
Parallel: Each dimension runs through 3 rounds
    - Round 1: Initial questions
    - Round 2: Follow-up questions
    - Round 3: Final prompt generation
    ↓
All complete: generate final integrated document
    ↓
Client: display and copy final document
```

#### Core State Structure

```python
{
    "project_description": str,
    "api_key": str,
    "dimensions": {
        "dimension_id": {
            "id": str,
            "name": str,
            "messages": list,
            "status": "pending|in_progress|completed",
            "round": int,
            "generated_prompt": str,
        },
        ...
    },
    "final_output": str,
}
```

---

### WebSocket Protocol

#### Client → Server

| Type | Fields | Description |
|------|--------|-------------|
| `project_init` | `content`, `dimensions` | Start project |
| `dimension_message` | `dimension_id`, `content` | Send answer |
| `add_dimension` | `config` | Add dimension |
| `remove_dimension` | `dimension_id` | Remove dimension |
| `start_dimension` | `dimension_id` | Start dimension |
| `finalize` | (none) | Generate final document |

#### Server → Client

| Type | Fields | Description |
|------|--------|-------------|
| `project_ready` | `dimensions`, `project_description` | Project initialized |
| `dimension_question` | `dimension_id`, `content`, `round` | Question received |
| `dimension_status` | `dimension_id`, `status` | Status changed |
| `dimension_complete` | `dimension_id`, `prompt` | Dimension completed |
| `all_complete` | (none) | All dimensions done |
| `final_document` | `content` | Final document |
| `error` | `message` | Error occurred |

---

### Adding a New Dimension

#### Step 1: Add to state.py
```python
DEFAULT_DIMENSIONS = [
    # ...existing...
    {"id": "security", "name": "Security Design", "icon": "🔒"},
]
```

#### Step 2: Add to dimension_prompts.py
```python
DIMENSION_PROMPTS = {
    # ...existing...
    "security": """
You are a security expert...
{base_instructions}
""".strip(),
}
```

---

</details>

---

## 🔗 API Endpoints

```
GET  /                          # Serve index.html
GET  /health                    # Health check
POST /api/session               # Create session
GET  /api/dimensions/defaults   # Get default dimensions
GET  /ws/{session_id}           # WebSocket connection
```

---

## 📦 Dependencies

See `requirements.txt`:
- **FastAPI 0.110+** - Web framework
- **Uvicorn 0.29+** - ASGI server
- **WebSockets 12.0+** - WebSocket support
- **LangGraph 0.2+** - Graph execution framework
- **LangChain 0.2+** - LLM integration
- **langchain-upstage 0.1+** - Upstage integration
- **python-dotenv 1.0+** - Environment variables

---

## 🚀 Live Demo

[projectpromptgeneratorlanggraph-production.up.railway.app](https://projectpromptgeneratorlanggraph-production.up.railway.app)

---

## 📝 Notes

- **Session Storage**: In-memory (development only; use Redis/DB for production)
- **API Key Security**: Never hardcode API keys; use environment variables
- **CORS**: Frontend served from same origin; CORS not needed
- **WebSocket**: Uses ws:// (HTTP) or wss:// (HTTPS) based on page protocol

---

## 🤝 Contributing

Contributions welcome! Please submit issues and pull requests.

---

## 📄 License

(Add your license information here)

---

**Last Updated**: April 2025 | **Version**: 1.0.0
