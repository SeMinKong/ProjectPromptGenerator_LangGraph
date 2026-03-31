from langgraph.graph import StateGraph, END

from state import PromptState
from nodes import (
    analyze_input,
    write_draft,
    evaluate,
    agent_feedback,
    give_output,
)


def quality_check(state: PromptState) -> str:
    """Route after evaluate: needs improvement → agent_feedback, good → give_output."""
    draft = state.get("current_draft", "")
    if "<!-- eval:needs_improvement -->" in draft:
        return "agent_feedback"
    return "give_output"


def build_graph() -> StateGraph:
    builder = StateGraph(PromptState)

    # Register nodes
    builder.add_node("analyze_input", analyze_input)
    builder.add_node("write_draft", write_draft)
    builder.add_node("evaluate", evaluate)
    builder.add_node("agent_feedback", agent_feedback)
    builder.add_node("give_output", give_output)

    # Entry point
    builder.set_entry_point("analyze_input")

    # analyze_input → write_draft directly (agent handles missing info autonomously)
    builder.add_edge("analyze_input", "write_draft")

    # write_draft → evaluate
    builder.add_edge("write_draft", "evaluate")

    # Conditional routing after evaluate
    builder.add_conditional_edges(
        "evaluate",
        quality_check,
        {
            "agent_feedback": "agent_feedback",
            "give_output": "give_output",
        },
    )

    # agent_feedback → write_draft (revision loop)
    builder.add_edge("agent_feedback", "write_draft")

    # give_output → END
    builder.add_edge("give_output", END)

    return builder.compile()


app = build_graph()
