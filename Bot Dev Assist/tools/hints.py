# services/agent_runtime.py with full type hints
from typing import Any, Dict, List, Optional

from langchain.messages import BaseMessage, HumanMessage
from services.modal_loader import modal_loader
from services.tool_executor import ToolExecutor


class AgentRuntime:
    """Main entry point for agent execution with Foundry JSON tool calls."""

    def __init__(
        self,
        user: str = "Guest",
        agent: Optional[Any] = None,
        llm: Optional[Any] = None,
    ) -> None:
        """Initialize the agent runtime.

        Args:
            user: User identifier
            agent: Pre-initialized agent
            llm: Pre-initialized LLM
        """
        self.user: str = user
        self.agent: Any = agent or modal_loader.get_agent()
        self.llm: Any = llm or modal_loader.get_llm()
        self.executor: ToolExecutor = ToolExecutor()

    def run(self, user_input: str) -> str:
        """Execute agent or LLM.

        Args:
            user_input: User message

        Returns:
            Agent response string
        """
        # Validation
        if not isinstance(user_input, str):
            return "❌ Input must be string"

        if not user_input.strip():
            return "❌ Input cannot be empty"

        try:
            result: str = self._run_agent(user_input)
            return result
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _run_agent(self, user_input: str) -> str:
        """Run agent with tools."""
        result: Dict[str, Any] = self.agent.invoke(
            {"messages": [HumanMessage(content=user_input)]}
        )

        output: str = self._extract_output(result)
        tool_call: Optional[Dict[str, Any]] = self.executor.extract_json_tool_call(
            output
        )

        if tool_call:
            return self.executor.execute(tool_call)

        return output

    def _extract_output(self, result: Any) -> str:
        """Extract output from agent result."""
        if hasattr(result, "content"):
            return result.content

        if isinstance(result, dict) and "messages" in result:
            messages: List[Any] = result.get("messages", [])
            if messages:
                last_msg: Any = messages[-1]
                if hasattr(last_msg, "content"):
                    return last_msg.content

        return str(result)
