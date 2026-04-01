import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from server.session import store
from server.graph_runner import handle_dimension_turn, handle_finalize
from server.ws_handler import (
    parse_client_message,
    make_error,
    make_project_ready,
    make_dimension_question,
    make_dimension_status,
)
from state import DEFAULT_DIMENSIONS

logger = logging.getLogger(__name__)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

app = FastAPI(title="Project Design Prompt Generator")
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.api_route("/", methods=["GET", "HEAD"])
async def index() -> FileResponse:
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.api_route("/health", methods=["GET", "HEAD"])
async def health() -> dict:
    return {"status": "ok"}


class SessionRequest(BaseModel):
    api_key: str = ""


def _check_api_key(api_key: str) -> bool:
    """Return True if api_key is non-empty.

    A non-empty key is accepted optimistically; the first real LLM call will
    fail with an authentication error if the key is invalid, which is surfaced
    to the client through the normal error path.  Creating a throwaway LLM
    instance and calling .invoke() just to validate the key is expensive and
    unnecessary.
    """
    return bool(api_key.strip())


@app.post("/api/session")
async def create_session(body: SessionRequest = SessionRequest()) -> JSONResponse:
    key_to_use = body.api_key or os.getenv("UPSTAGE_API_KEY", "")
    if not key_to_use:
        return JSONResponse(status_code=400, content={"error": "API 키가 필요합니다."})
    if not _check_api_key(key_to_use):
        return JSONResponse(status_code=401, content={"error": "유효하지 않은 API 키입니다."})
    session_id = await store.create_session(api_key=body.api_key)
    return JSONResponse(content={"session_id": session_id})


@app.get("/api/dimensions/defaults")
async def get_default_dimensions() -> dict:
    return {"dimensions": DEFAULT_DIMENSIONS}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()

    state = await store.get_session(session_id)
    if state is None:
        await websocket.send_text(make_error("세션을 찾을 수 없습니다."))
        await websocket.close()
        return

    async def send(message: str) -> None:
        await websocket.send_text(message)

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                msg = parse_client_message(raw)
            except ValueError as e:
                await send(make_error(str(e)))
                continue

            msg_type = msg.get("type")
            state = await store.get_session(session_id)

            # ── project_init ──────────────────────────────────────
            if msg_type == "project_init":
                project_desc = msg.get("content", "").strip()
                if not project_desc:
                    await send(make_error("프로젝트 설명을 입력해주세요."))
                    continue

                dims = msg.get("dimensions", DEFAULT_DIMENSIONS)
                state = await store.init_project(session_id, project_desc, dims)

                dim_list = [
                    {
                        "id": d["id"],
                        "name": d["name"],
                        "icon": d["icon"],
                        "status": d["status"],
                        "generated_prompt": d.get("generated_prompt", "")
                    }
                    for d in state["dimensions"].values()
                ]
                await send(make_project_ready(dim_list, project_desc))

                # Auto-start ALL dimensions in parallel
                tasks = [
                    handle_dimension_turn(session_id, did, None, state, send, store)
                    for did in state["dimensions"].keys()
                ]
                await asyncio.gather(*tasks)

            # ── dimension_message ─────────────────────────────────
            elif msg_type == "dimension_message":
                dimension_id = msg.get("dimension_id", "")
                content = msg.get("content", "").strip()
                if not dimension_id:
                    await send(make_error("dimension_id가 필요합니다."))
                    continue
                if not content:
                    await send(make_error("메시지 내용이 필요합니다."))
                    continue

                dim = state["dimensions"].get(dimension_id)
                if dim is None:
                    await send(make_error(f"존재하지 않는 영역: {dimension_id}"))
                    continue
                # Removed 'completed' check to allow revisions

                await handle_dimension_turn(session_id, dimension_id, content, state, send, store)

            # ── add_dimension ─────────────────────────────────────
            elif msg_type == "add_dimension":
                config = msg.get("config", {})
                if not config.get("id") or not config.get("name"):
                    await send(make_error("영역 id와 name이 필요합니다."))
                    continue
                await store.add_dimension(session_id, config)
                state = await store.get_session(session_id)
                dim = state["dimensions"][config["id"]]
                await send(make_dimension_status(config["id"], dim["status"]))

            # ── remove_dimension ──────────────────────────────────
            elif msg_type == "remove_dimension":
                dimension_id = msg.get("dimension_id", "")
                await store.remove_dimension(session_id, dimension_id)

            # ── start_dimension ───────────────────────────────────
            elif msg_type == "start_dimension":
                dimension_id = msg.get("dimension_id", "")
                if not dimension_id:
                    await send(make_error("dimension_id가 필요합니다."))
                    continue
                dim = state["dimensions"].get(dimension_id)
                if dim is None:
                    await send(make_error(f"존재하지 않는 영역: {dimension_id}"))
                    continue

                # If already started or completed, just ignore instead of sending error
                if dim["status"] != "pending":
                    continue

                await handle_dimension_turn(session_id, dimension_id, None, state, send, store)

            # ── finalize ──────────────────────────────────────────
            elif msg_type == "finalize":
                await handle_finalize(state, send, state["api_key"])

            else:
                await send(make_error(f"알 수 없는 메시지 유형: {msg_type}"))

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for session %s", session_id)
        await store.delete_session(session_id)
