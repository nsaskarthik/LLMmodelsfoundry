from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel


class RouterDecision(BaseModel):
    mode: Literal["AGENT", "CHAT"]
    reason: str


router_prompt = ChatPromptTemplate.from_template(
    "You are a router. Decide the mode.\n"
    "Return exactly one token: AGENT or CHAT.\n\n"
    "Request: {user_input}\n"
    "Mode:"
)


def _keyword_route(user_input: str) -> str:
    triggers = ["run", "fetch", "execute", "scan", "list", "analyze", "tool", "call"]
    return "AGENT" if any(t in user_input.lower() for t in triggers) else "CHAT"


def route_message(llm=None, user_input: str = "", session_id=None) -> str:
    if not user_input.strip():
        return "CHAT"

    if llm is not None:
        try:
            chain = router_prompt | llm
            result = chain.invoke({"user_input": user_input})
            text = (result.content or "").strip().upper()

            if text.startswith("AGENT"):
                return "AGENT"
            if text.startswith("CHAT"):
                return "CHAT"
            return _keyword_route(user_input)

        except Exception as ex:
            print(f"Routing error: {ex}")
            return _keyword_route(user_input)

    return _keyword_route(user_input)
