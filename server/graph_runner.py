"""Dimension turn runner for WebSocket handler."""
import asyncio
from typing import Callable, Awaitable

from dimensions.runner import run_dimension_turn, extract_prompt
from prompts.dimension_prompts import MAX_ROUNDS
from server.ws_handler import (
    make_dimension_question,
    make_dimension_status,
    make_dimension_complete,
    make_all_complete,
    make_final_document,
    make_error,
)

SendFn = Callable[[str], Awaitable[None]]


async def handle_dimension_turn(
    session_id: str,
    dimension_id: str,
    user_input: str | None,
    state: dict,
    send: SendFn,
    store,
) -> None:
    """Process one turn for a dimension and send appropriate WS messages."""
    dims = state.get("dimensions", {})
    if dimension_id not in dims:
        await send(make_error(f"알 수 없는 영역: {dimension_id}"))
        return

    dim = dict(dims[dimension_id])
    project_desc = state.get("project_description", "")
    api_key = state.get("api_key", "")

    # Advance round
    new_round = dim["round"] + 1
    dim["round"] = new_round
    dim["status"] = "in_progress"

    await store.update_dimension(session_id, dimension_id, {"round": new_round, "status": "in_progress"})
    await send(make_dimension_status(dimension_id, "in_progress"))

    try:
        response, is_completed = await run_dimension_turn(
            dimension_id=dimension_id,
            dimension_name=dim["name"],
            project_description=project_desc,
            conversation_history=dim["messages"],
            user_input=user_input,
            current_round=new_round,
            api_key=api_key,
        )
    except Exception as e:
        await send(make_error(f"LLM 오류 ({dim['name']}): {e}"))
        await store.update_dimension(session_id, dimension_id, {"status": "pending", "round": new_round - 1})
        return

    # Append to conversation history
    new_messages = list(dim["messages"])
    if user_input:
        new_messages.append({"role": "user", "content": user_input})
    new_messages.append({"role": "assistant", "content": response})

    if is_completed:
        final_prompt = extract_prompt(response)
        await store.update_dimension(session_id, dimension_id, {
            "messages": new_messages,
            "status": "completed",
            "generated_prompt": final_prompt,
        })
        await send(make_dimension_complete(dimension_id, final_prompt))
        await send(make_dimension_status(dimension_id, "completed"))

        # Check if all dimensions are completed
        updated_state = await store.get_session(session_id)
        all_done = all(
            d["status"] == "completed"
            for d in updated_state["dimensions"].values()
        )
        if all_done:
            await send(make_all_complete())
    else:
        await store.update_dimension(session_id, dimension_id, {"messages": new_messages})
        await send(make_dimension_question(dimension_id, response, new_round))


async def handle_finalize(state: dict, send: SendFn, api_key: str) -> None:
    """Generate the final integrated document from all completed dimensions."""
    from langchain_core.messages import HumanMessage, SystemMessage
    from llm import get_llm
    from prompts.dimension_prompts import FINAL_DOCUMENT_PROMPT

    dims = state.get("dimensions", {})
    project_desc = state.get("project_description", "프로젝트")

    completed = {did: d for did, d in dims.items() if d.get("generated_prompt")}
    if not completed:
        await send(make_error("완료된 영역이 없습니다. 최소 하나의 영역을 완료해주세요."))
        return

    # Build prompt sections
    sections = "\n\n".join(
        f"## {d['name']}\n{d['generated_prompt']}"
        for d in completed.values()
    )

    system = FINAL_DOCUMENT_PROMPT.format(project_name=project_desc[:60])
    user_content = f"프로젝트: {project_desc}\n\n{sections}"

    try:
        llm = get_llm(api_key)
        response = await asyncio.to_thread(
            llm.invoke,
            [SystemMessage(content=system), HumanMessage(content=user_content)]
        )
        await send(make_final_document(response.content))
    except Exception as e:
        await send(make_error(f"최종 문서 생성 오류: {e}"))
