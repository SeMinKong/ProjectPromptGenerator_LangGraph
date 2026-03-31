import json
import os
from dotenv import load_dotenv
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from state import PromptState

# 환경 변수 로드 (fallback only)
load_dotenv()
_FALLBACK_API_KEY = os.getenv("UPSTAGE_API_KEY", "")


def _get_llm(api_key: str) -> ChatUpstage:
    return ChatUpstage(
        api_key=api_key or _FALLBACK_API_KEY,
        model="solar-pro",
        reasoning_effort="high",
    )


def _parse_json_response(content: str) -> dict:
    """Strip optional markdown fences and parse JSON from an LLM response."""
    content = content.strip()
    if content.startswith("```"):
        content = "\n".join(
            line for line in content.split("\n")
            if not line.startswith("```")
        ).strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}


def _clean_str(s: str) -> str:
    """Ensure the string can be encoded to UTF-8 without surrogate errors."""
    return s.encode('utf-8', 'ignore').decode('utf-8')


def analyze_input(state: PromptState) -> PromptState:
    """Analyze the latest user message and update missing_info."""
    conversation = state.get("messages", [])
    if not conversation:
        return state

    system_prompt = SystemMessage(content=(
        "You are an expert prompt engineer. Your job is to analyze the user's request "
        "and identify what information is still missing to write a high-quality, "
        "structured prompt.\n\n"
        "The 6 required sections are:\n"
        "1. 역할 (Role)\n"
        "2. 배경 정보 (Background Information)\n"
        "3. 수행 과제 (Task to Perform)\n"
        "4. 제약 사항 (Constraints)\n"
        "5. 세부 지시 (Detailed Instructions)\n"
        "6. 출력 형식 (Output Format)\n\n"
        "Respond ONLY with a valid JSON object in this exact format:\n"
        '{"missing": ["item1", "item2", ...]}\n'
        "If nothing is missing, respond with: {\"missing\": []}"
    ))

    messages_to_send = [system_prompt] + list(conversation)
    response = _get_llm(state.get("api_key", "")).invoke(messages_to_send)

    content = _clean_str(response.content)
    missing = _parse_json_response(content).get("missing", [])
    return {**state, "missing_info": missing}


def ask_user(state: PromptState) -> PromptState:
    """Generate a question asking the user for missing information."""
    missing = state.get("missing_info", [])

    if not missing:
        question = "추가로 제공해 주실 정보가 있으신가요?"
    else:
        items = "\n".join(f"- {item}" for item in missing)
        question = (
            f"좋은 프롬프트를 작성하기 위해 다음 정보가 더 필요합니다:\n\n"
            f"{items}\n\n"
            "위 항목들에 대해 알려주세요."
        )

    ai_message = AIMessage(content=_clean_str(question))
    return {
        **state,
        "messages": [ai_message],
    }


def write_draft(state: PromptState) -> PromptState:
    """Generate a structured 6-section prompt draft from collected information."""
    conversation = state.get("messages", [])

    system_prompt = SystemMessage(content=(
        "You are an expert prompt engineer. Based on the conversation so far, "
        "write a complete, high-quality prompt using EXACTLY the following 6-section template.\n\n"
        "IMPORTANT: If any information is missing or unclear, make reasonable and sensible assumptions "
        "based on context — do NOT ask the user for more information. Fill in every section fully.\n\n"
        "## 역할 (Role)\n"
        "[Describe the role the AI should take]\n\n"
        "## 배경 정보 (Background Information)\n"
        "[Provide relevant context and background]\n\n"
        "## 수행 과제 (Task to Perform)\n"
        "[Clearly state what the AI needs to do]\n\n"
        "## 제약 사항 (Constraints)\n"
        "[List limitations, rules, and restrictions]\n\n"
        "## 세부 지시 (Detailed Instructions)\n"
        "[Step-by-step instructions or additional guidance]\n\n"
        "## 출력 형식 (Output Format)\n"
        "[Specify the expected format of the output]\n\n"
        "Fill in each section thoroughly. Use Korean headings as shown above."
    ))

    messages_to_send = [system_prompt] + list(conversation)
    response = _get_llm(state.get("api_key", "")).invoke(messages_to_send)
    draft = _clean_str(response.content.strip())

    return {
        **state,
        "current_draft": draft,
    }


def evaluate(state: PromptState) -> PromptState:
    """Evaluate the quality of the current draft and determine if it needs revision."""
    draft = state.get("current_draft", "")

    system_prompt = SystemMessage(content=(
        "You are a strict prompt quality evaluator. Review the following prompt draft "
        "and assess whether it fully meets all 6 required sections:\n"
        "역할, 배경 정보, 수행 과제, 제약 사항, 세부 지시, 출력 형식\n\n"
        "Respond ONLY with a valid JSON object in this format:\n"
        '{"quality": "good" or "needs_improvement", "reason": "brief explanation"}\n\n'
        "Use \"good\" only if ALL sections are present, detailed, and coherent.\n"
        "Use \"needs_improvement\" if any section is missing, too vague, or incomplete."
    ))

    draft_message = HumanMessage(content=f"Draft to evaluate:\n\n{draft}")
    response = _get_llm(state.get("api_key", "")).invoke([system_prompt, draft_message])

    content = _clean_str(response.content)
    try:
        parsed = _parse_json_response(content)
        quality = parsed.get("quality", "needs_improvement")
        reason = parsed.get("reason", "")
    except Exception:
        quality = "good"
        reason = "Evaluation parsing failed, accepting draft."

    eval_message = AIMessage(content=f"[평가] 품질: {quality} — {reason}")
    return {
        **state,
        "messages": [eval_message],
        "current_draft": state.get("current_draft", "") + f"\n\n",
    }


def agent_feedback(state: PromptState) -> PromptState:
    """Generate specific feedback to improve the current draft."""
    draft = state.get("current_draft", "")

    system_prompt = SystemMessage(content=(
        "You are an expert prompt engineer providing revision feedback. "
        "The draft below needs improvement. Give specific, actionable feedback "
        "on exactly what to fix in each section. Be concise and direct.\n"
        "Focus on: missing content, vague instructions, and structural issues."
    ))

    draft_message = HumanMessage(content=f"Draft to improve:\n\n{draft}")
    response = _get_llm(state.get("api_key", "")).invoke([system_prompt, draft_message])
    feedback = _clean_str(response.content.strip())

    feedback_message = AIMessage(content=f"[피드백]\n{feedback}")
    return {
        **state,
        "messages": [feedback_message],
    }


def give_output(state: PromptState) -> PromptState:
    """Return the final polished prompt to the user."""
    draft = state.get("current_draft", "")
    # Strip internal evaluation markers
    final = draft.replace("", "").replace("", "").strip()

    separator = "=" * 60
    final_output = (
        f"\n{separator}\n"
        f"✅ 최종 프롬프트가 완성되었습니다!\n"
        f"{separator}\n\n"
        f"{final}\n\n"
        f"{separator}\n"
    )

    output_message = AIMessage(content=final_output)
    return {
        **state,
        "messages": [output_message],
        "current_draft": final,
    }