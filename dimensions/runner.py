"""Per-dimension conversation runner."""
import asyncio
import logging
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from llm import get_llm
from prompts.dimension_prompts import get_system_prompt, MAX_ROUNDS

logger = logging.getLogger(__name__)

GENERATE_TAG = "[GENERATE_PROMPT]"


async def run_dimension_turn(
    dimension_id: str,
    dimension_name: str,
    project_description: str,
    conversation_history: list,
    user_input: str | None,
    current_round: int,
    api_key: str,
) -> tuple[str, bool]:
    """
    Run one turn for a dimension.

    Returns (response_content, is_completed).
    is_completed=True means the dimension has generated its final prompt.
    """
    system_prompt = get_system_prompt(dimension_id, dimension_name, current_round)

    messages = [SystemMessage(content=system_prompt)]

    # Inject project description as context
    messages.append(HumanMessage(content=f"프로젝트 설명: {project_description}"))

    # Replay conversation history
    for msg in conversation_history:
        if msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
        else:
            messages.append(HumanMessage(content=msg["content"]))

    # Add the new user input (skip on first turn)
    if user_input:
        messages.append(HumanMessage(content=user_input))

    # If this is the final round, explicitly ask for the prompt
    is_final_round = current_round >= MAX_ROUNDS
    if is_final_round and user_input:
        messages.append(HumanMessage(content=(
            "이제 지금까지 수집한 정보를 바탕으로 최종 설계 프롬프트를 생성해주세요. "
            f"반드시 {GENERATE_TAG} 태그를 첫 줄에 포함해야 합니다."
        )))

    llm = get_llm(api_key)
    logger.debug("Running dimension turn: id=%s round=%d", dimension_id, current_round)
    response = await asyncio.to_thread(llm.invoke, messages)
    content: str = response.content

    # Strict completion condition: Only complete if tag is present AND it's the final round
    is_completed = (GENERATE_TAG in content) and is_final_round
    return content, is_completed


def extract_prompt(response_content: str) -> str:
    """Extract the generated prompt from a response containing GENERATE_TAG."""
    if GENERATE_TAG in response_content:
        parts = response_content.split(GENERATE_TAG, 1)
        return parts[1].strip()
    return response_content.strip()
