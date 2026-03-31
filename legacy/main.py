from langchain_core.messages import HumanMessage

from graph import app
from state import PromptState


def run() -> None:
    """Interactive terminal loop for the prompt generator agent."""

    print("=" * 60)
    print("  범용 프롬프트 생성기 (Universal Prompt Generator)")
    print("  Powered by LangGraph + Upstage Solar")
    print("  종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("=" * 60)
    print()

    # Initial state
    state: PromptState = {
        "messages": [],
        "missing_info": [],
        "current_draft": "",
    }

    print("어떤 용도의 프롬프트를 만들어 드릴까요? 원하시는 내용을 입력해 주세요.")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n프로그램을 종료합니다. 감사합니다!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "종료"):
            print("프로그램을 종료합니다. 감사합니다!")
            break

        # Add user message to state
        state["messages"] = list(state.get("messages", [])) + [
            HumanMessage(content=user_input)
        ]

        # Run the graph
        try:
            result = app.invoke(state)
        except Exception as e:
            import traceback
            try:
                print(f"\n[오류] 처리 중 문제가 발생했습니다: {e}\n")
                traceback.print_exc()
            except UnicodeEncodeError:
                print(f"\n[오류] 처리 중 문제가 발생했습니다 (인코딩 우회): {repr(e)}\n")
                print("Traceback (encoded):")
                print(traceback.format_exc().encode('utf-8', 'replace').decode('utf-8'))
            continue

        # Update state with graph result
        state = result

        # Print the latest AI message
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, "content") and last_message.content:
                print(f"\nAgent: {last_message.content}\n")

        # If give_output was reached, prompt for a new request
        current_draft = state.get("current_draft", "")
        if current_draft and "<!-- eval:" not in current_draft:
            print("-" * 60)
            print("새로운 프롬프트를 만들려면 내용을 입력하세요.")
            print()
            # Reset state for next prompt generation session
            state = {
                "messages": [],
                "missing_info": [],
                "current_draft": "",
            }


if __name__ == "__main__":
    run()
