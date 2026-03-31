import asyncio
import uuid
from typing import Optional

from state import ProjectState, make_project_state, make_dimension_state


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, ProjectState] = {}
        self._lock = asyncio.Lock()

    async def create_session(self, api_key: str = "") -> str:
        session_id = str(uuid.uuid4())
        async with self._lock:
            self._sessions[session_id] = make_project_state(api_key)
        return session_id

    async def get_session(self, session_id: str) -> Optional[ProjectState]:
        async with self._lock:
            return self._sessions.get(session_id)

    async def update_session(self, session_id: str, state: ProjectState) -> None:
        async with self._lock:
            self._sessions[session_id] = state

    async def init_project(self, session_id: str, project_description: str, dimension_configs: list) -> Optional[ProjectState]:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            dimensions = {c["id"]: make_dimension_state(c) for c in dimension_configs}
            session["project_description"] = project_description
            session["dimensions"] = dimensions
            session["final_output"] = ""
            return session

    async def add_dimension(self, session_id: str, dim_config: dict) -> bool:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False
            dim_id = dim_config["id"]
            if dim_id not in session["dimensions"]:
                session["dimensions"][dim_id] = make_dimension_state(dim_config)
            return True

    async def remove_dimension(self, session_id: str, dimension_id: str) -> bool:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False
            session["dimensions"].pop(dimension_id, None)
            return True

    async def update_dimension(self, session_id: str, dimension_id: str, dim_state: dict) -> None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session and dimension_id in session["dimensions"]:
                session["dimensions"][dimension_id].update(dim_state)

    async def delete_session(self, session_id: str) -> None:
        async with self._lock:
            self._sessions.pop(session_id, None)


store = SessionStore()
