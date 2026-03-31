from typing import TypedDict

DEFAULT_DIMENSIONS = [
    {"id": "ux_design", "name": "UI/UX 디자인", "icon": "🎨"},
    {"id": "architecture", "name": "시스템 아키텍처", "icon": "🏗️"},
    {"id": "database", "name": "데이터베이스 설계", "icon": "🗄️"},
    {"id": "api", "name": "API 설계", "icon": "🔌"},
    {"id": "deployment", "name": "배포 전략", "icon": "🚀"},
    {"id": "testing", "name": "테스트 전략", "icon": "✅"},
]


class PromptState(TypedDict):
    messages: list
    missing_info: list
    current_draft: str
    api_key: str


class DimensionState(TypedDict):
    id: str
    name: str
    icon: str
    messages: list  # [{"role": "assistant"|"user", "content": str}]
    status: str     # "pending" | "in_progress" | "completed"
    decisions: list
    generated_prompt: str
    round: int


class ProjectState(TypedDict):
    project_description: str
    api_key: str
    dimensions: dict   # id -> DimensionState
    final_output: str


def make_dimension_state(dim_config: dict) -> DimensionState:
    return DimensionState(
        id=dim_config["id"],
        name=dim_config["name"],
        icon=dim_config.get("icon", "📋"),
        messages=[],
        status="pending",
        decisions=[],
        generated_prompt="",
        round=0,
    )


def make_project_state(api_key: str, dimension_configs: list | None = None) -> ProjectState:
    configs = dimension_configs if dimension_configs is not None else DEFAULT_DIMENSIONS
    dimensions = {c["id"]: make_dimension_state(c) for c in configs}
    return ProjectState(
        project_description="",
        api_key=api_key,
        dimensions=dimensions,
        final_output="",
    )
