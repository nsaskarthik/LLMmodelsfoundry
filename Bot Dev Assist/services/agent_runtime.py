"""Agent runtime execution."""

from __future__ import annotations

import uuid
from typing import Any, Optional

from config import settings
from config.logging_config import setup_logging, with_context
from services.core.guardrails import check_input, strip_control_tokens
from services.core.router import route_message


class AgentRuntime:
    """Main entry point for chat/agent execution."""

    def __init__(
        self,
        user: str = "Guest",
        agent: Any = None,
        llm: Any = None,
        session_id: Optional[str] = None,
    ):
        base_logger = setup_logging(settings.app)
        self.user = user
        self.session_id = session_id or str(uuid.uuid4())
        self.logger = with_context(
            base_logger,
            component="AgentRuntime",
            user=self.user,
            session_id=self.session_id,
        )

        # agent: create_agent(...) return (compiled agent runtime)
        # llm: ChatOpenAI instance (chat-only mode)
        self.agent = agent
        self.llm = llm

        # Some LangChain components accept a second "config" arg; keep thread_id for traceability.
        self.config = {"configurable": {"thread_id": self.session_id}}

    def run(self, user_input: str) -> str:
        allowed, message = check_input(user_input)
        if not allowed:
            return f"Request rejected: {message}"

        try:
            mode = route_message(
                llm=self.llm, user_input=user_input, session_id=self.session_id
            )
            self.logger.info("Routing decision", extra={"mode": mode})

            if mode == "AGENT":
                return self._run_agent(user_input)
            return self._run_llm_only(user_input)

        except Exception as e:
            self.logger.error("Runtime error", extra={"error": str(e)})
            return f"I encountered an error: {str(e)}"

    def _run_agent(self, user_input: str) -> str:
        """
        Run agent with tools.

        Official LangChain usage:
        agent.invoke({"messages": [{"role": "user", "content": "..."}]})
        The agent runtime executes tools internally and returns updated state.
        """
        if self.agent is None:
            return "Agent is not initialized. Check modal_loader.get_agent()."

        try:
            # Pass messages in state, as documented.
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                self.config,
            )

            # result is an updated state dict; docs show messages being present in state.
            messages = result.get("messages") if isinstance(result, dict) else None
            if not messages:
                return "Agent returned no messages."

            last_msg = messages[-1]
            content = getattr(last_msg, "content", None)
            if content is None:
                content = str(last_msg)

            return strip_control_tokens(content)

        except Exception as e:
            self.logger.error("Agent execution failed", extra={"error": str(e)})
            return f"Agent execution failed: {str(e)}"

    def _run_llm_only(self, user_input: str) -> str:
        """Run chat-only path (no tools)."""
        if self.llm is None:
            return "LLM is not initialized. Check modal_loader.get_llm()."

        try:
            result = self.llm.invoke(user_input)
            content = getattr(result, "content", None)
            if content is None:
                content = str(result)
            return strip_control_tokens(content)

        except Exception as e:
            self.logger.error("LLM execution failed", extra={"error": str(e)})
            return f"LLM execution failed: {str(e)}"
