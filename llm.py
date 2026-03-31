from langchain_upstage import ChatUpstage


def get_llm(api_key: str) -> ChatUpstage:
    return ChatUpstage(api_key=api_key, model="solar-pro")
