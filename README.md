# LangGraph 기반 프로젝트 설계 프롬프트 생성기

**[English Version](./README.en.md)**

### Live Demo

[![Live Demo](https://img.shields.io/badge/demo-online-green.svg)](https://projectpromptgeneratorlanggraph-production.up.railway.app/) << 클릭

**LangGraph**와 **Upstage Solar Pro**를 활용하여 소프트웨어 프로젝트의 설계를 자동화하고 최적화된 프롬프트를 생성하는 플랫폼입니다. 사용자와의 구조화된 대화를 통해 UI/UX, 아키텍처, 데이터베이스 등 각 설계 영역을 세밀하게 분석하고, 즉시 구현 가능한 수준의 AI 프롬프트를 자동으로 도출합니다.

## 주요 특징

- **병렬 그래프 아키텍처**: **LangGraph**를 활용하여 UI/UX, 아키텍처, DB 등 6개 이상의 설계 영역을 동시에 독립적으로 관리합니다.
- **반복적 심화 대화**: 각 영역별로 최대 3라운드의 정교한 Q&A 세션을 진행하여 프로젝트 요구사항을 구체화합니다.
- **자동화된 프롬프트 엔지니어링**: 대화 이력을 바탕으로 각 영역별 전문가급 AI 프롬프트를 자동으로 생성합니다.
- **실시간 양방향 통신**: **FastAPI**와 **WebSocket**을 사용하여 각 영역의 진행 상태와 생성된 프롬프트를 실시간으로 확인할 수 있습니다.
- **유연한 확장성**: 보안, 배포 전략 등 프로젝트 특성에 따라 설계 영역(Dimension)을 자유롭게 추가하거나 수정할 수 있습니다.

## 기술 스택

- **AI 오케스트레이션**: LangGraph, LangChain
- **LLM**: Upstage Solar Pro
- **백엔드**: FastAPI, WebSocket
- **프론트엔드**: Vanilla JS, HTML5, CSS3
- **DevOps**: Docker

## 프로젝트 구조

```text
├── server/             # FastAPI 서버 및 WebSocket 핸들러
├── dimensions/         # 영역별 LLM 호출 및 비즈니스 로직
├── prompts/            # 시스템 프롬프트 및 라운드 설정
├── frontend/           # 3패널 구성의 대화형 웹 UI
└── state.py            # LangGraph 상태 정의 및 초기값
```

## 핵심 기술 구현 내용

### 1. 상태 머신 기반의 대화 제어
LangGraph의 상태 관리 기법을 사용하여 각 설계 영역이 독립적인 메시지 이력, 현재 라운드, 완료 상태를 추적하도록 설계했습니다. 이를 통해 여러 에이전트가 협업하는 것과 같은 효과를 효율적으로 구현했습니다.

### 2. WebSocket을 활용한 실시간 피드백
긴 대기 시간을 최소화하기 위해 모든 설계 영역을 병렬로 초기화하고 처리합니다. LLM이 질문을 생성하거나 최종 프롬프트를 도출하는 즉시 WebSocket을 통해 클라이언트에 푸시함으로써 끊김 없는 사용자 경험을 제공합니다.

## 빠른 시작

### 사전 요구사항
- Python 3.11 이상
- [Upstage API Key](https://console.upstage.ai/)

### 설치 및 실행
```bash
git clone <repository-url>
cd ProjectPromptGenerator_LangGraph
pip install -r requirements.txt
echo "UPSTAGE_API_KEY=your_key_here" > .env
uvicorn server.app:app --reload
```
`http://localhost:8000`에서 설계를 시작할 수 있습니다.

## 사용 방법
1. **아이디어 입력**: 만들고자 하는 프로젝트의 핵심 아이디어를 설명합니다.
2. **영역 선택**: 집중적으로 설계할 분야를 선택합니다.
3. **대화 진행**: 각 탭을 이동하며 AI의 질문에 답변하여 설계를 구체화합니다.
4. **결과 활용**: 생성된 최종 설계 문서를 복사하여 ChatGPT, Claude 등 선호하는 LLM에 입력하고 구현을 시작하세요.

>  **더 자세한 정보가 필요하신가요?**
> 상세한 LangGraph 상태 머신 설계, WebSocket 프로토콜 명세 등은 [상세 매뉴얼(DETAILS.md)](./DETAILS.md)에서 확인하실 수 있습니다.

---
LangGraph & Upstage Solar Pro로 구축한 프로젝트입니다.
