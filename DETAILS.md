# LangGraph 기반 프로젝트 설계 생성기 기술 상세

## 1. LangGraph 상태 구조 (`ProjectState`)
모든 노드는 아래의 `TypedDict` 상태를 공유하고 업데이트합니다.
```python
ProjectState = {
    "project_description": str,     # 프로젝트 설명
    "api_key": str,                 # API 키
    "dimensions": {                 # 6개 이상의 설계 영역 상태 (병렬 처리)
        "ux_design": {
            "id": str,
            "name": str,
            "messages": list,           # 각 영역별 독립된 대화 이력
            "status": "pending|in_progress|completed",
            "round": int,               # 현재 진행 라운드 (최대 3)
            "generated_prompt": str,    # 최종 생성된 프롬프트
        },
        # ... 추가 영역들
    },
    "final_output": str,            # 병합된 최종 마크다운 문서
}
```

## 2. 라운드별 대화 처리 로직 (`dimensions/runner.py`)
- **Round 1 (초기 질문)**: `시스템 프롬프트 + 프로젝트 설명` → LLM → 첫 질문 생성
- **Round 2 (심화 질문)**: `시스템 프롬프트 + 대화 이력 + 사용자 답변` → LLM → 구체적인 추가 질문
- **Round 3 (최종 도출)**: `전체 이력 + 프롬프트 추출 지시` → LLM → `[GENERATE_PROMPT]` 태그가 포함된 최종 프롬프트 도출

## 3. WebSocket 프로토콜 명세 (`server/ws_handler.py`)
| 방향 | 타입 | 필드 | 설명 |
|------|------|------|------|
| **C→S** | `project_init` | `content`, `dimensions` | 선택한 영역들로 프로젝트 초기화 |
| **C→S** | `dimension_message` | `dimension_id`, `content` | 특정 영역의 AI 질문에 답변 전송 |
| **C→S** | `add_dimension` | `config` | 커스텀 설계 영역 런타임 추가 |
| **S→C** | `dimension_question` | `dimension_id`, `content`, `round`| AI가 생성한 질문 수신 |
| **S→C** | `dimension_complete` | `dimension_id`, `prompt` | 특정 영역 설계 완료 및 프롬프트 수신 |
| **S→C** | `final_document` | `content` | 모든 영역 완료 후 통합 문서 수신 |

## 4. 커스텀 설계 영역 추가 방법 (`state.py` & `prompts/dimension_prompts.py`)
기본 6개 영역 외에 '보안', '다국어' 등의 커스텀 영역을 추가하려면 서버 상태 초기화 배열에 새 ID를 등록하고, 해당 ID와 매칭되는 시스템 프롬프트를 추가하면 프론트엔드에서 자동으로 로드되어 병렬 파이프라인에 편입됩니다.
