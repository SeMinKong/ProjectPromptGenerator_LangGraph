import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _msg(**kwargs: Any) -> str:
    return json.dumps({k: v for k, v in kwargs.items() if v is not None})


def make_project_ready(dimensions: list, project_description: str) -> str:
    return _msg(type="project_ready", dimensions=dimensions, project_description=project_description)


def make_dimension_question(dimension_id: str, content: str, round_num: int) -> str:
    return _msg(type="dimension_question", dimension_id=dimension_id, content=content, round=round_num)


def make_dimension_status(dimension_id: str, status: str) -> str:
    return _msg(type="dimension_status", dimension_id=dimension_id, status=status)


def make_dimension_complete(dimension_id: str, prompt: str) -> str:
    return _msg(type="dimension_complete", dimension_id=dimension_id, prompt=prompt)


def make_all_complete() -> str:
    return _msg(type="all_complete")


def make_final_document(content: str) -> str:
    return _msg(type="final_document", content=content)


def make_error(message: str) -> str:
    return _msg(type="error", message=message)


def parse_client_message(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e
    if "type" not in data:
        raise ValueError("Missing 'type' field")
    return data
