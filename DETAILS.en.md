# Project Design Prompt Generator Technical Details

## 1. LangGraph State Structure (`ProjectState`)
The core `TypedDict` that orchestrates the parallel graph execution:
```python
ProjectState = {
    "project_description": str,
    "api_key": str,
    "dimensions": {
        "ux_design": {
            "id": str,
            "name": str,
            "messages": list,       # Independent message history
            "status": "pending|in_progress|completed",
            "round": int,           # Current Q&A iteration
            "generated_prompt": str,
        }
    },
    "final_output": str,
}
```

## 2. Iterative Round Logic (`dimensions/runner.py`)
- **Round 1**: Uses the system prompt and user description to formulate initial exploratory questions.
- **Round 2**: Analyzes the user's responses alongside history to ask deeper, clarifying questions.
- **Round 3**: Compiles the full context and commands the LLM to output the final prompt wrapped in a `[GENERATE_PROMPT]` tag.

## 3. WebSocket Protocol (`server/ws_handler.py`)
- **Client to Server**:
  - `project_init`: Initializes the parallel LangGraph branches.
  - `dimension_message`: Submits a user reply to a specific dimension.
  - `add_dimension`: Adds custom domains dynamically.
- **Server to Client**:
  - `dimension_question`: Broadcasts the LLM's next question.
  - `dimension_complete`: Broadcasts the final extracted prompt for a tab.
  - `final_document`: Merges all dimensions into a final markdown file.
