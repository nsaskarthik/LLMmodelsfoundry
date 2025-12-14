"""
LLM and Agent initialization (LangChain v1).

- LLM: ChatOpenAI configured for an OpenAI-compatible endpoint (e.g., Foundry Local).
- Agent: create_agent(...) is the standard LangChain v1 agent builder and runs a tool loop internally.
"""

from __future__ import annotations

import logging
from typing import Optional

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

import tools
from config import settings

logger = logging.getLogger(__name__)


class ModalLoader:
    """Singleton loader for LLM and Agent instances."""

    _llm_instance: Optional[ChatOpenAI] = None
    _agent_instance = None  # Compiled agent runtime returned by create_agent(...)

    SYSTEM_PROMPT = """You are Dev Assistant, a helpful expert (Python + SQL) developer assistant.

        PRIMARY ROLE:
        - Expert Programming Developer in Python
        - Help with development, debugging, testing, and code reviewing
        - Execute code analysis, generate reports, and fetch metrics
        - Maintain code quality and security standards

        AVAILABLE TOOLS:
        You have access to the following tools:
        - read_and_generate_code(requirement: str, output_file: str): Generate Python code based on requirement and save to file
        - analyze_code(file_path: str): Analyze code file and return insights
        - save_memory(key: str, content: str): Save information to memory
        - recall_memory(key: str): Retrieve saved memory
        - list_memories(): List all saved memories

        CRITICAL INSTRUCTIONS:
        1. ONLY use read_and_generate_code when user EXPLICITLY asks to:
        - "generate code and save to [file]"
        - "create a file with [code]"
        - "write [code] to [filename]"

        2. DO NOT use the tool for:
        - "show me code for..."
        - "how to..."
        - "example of..."
        - "write code for..." (without save to file)

        3. For questions without file saving, just answer directly in chat

        4. NEVER just describe what the tool does - if you use it, CALL it
        5. Extract the requirement and output file path clearly
        6. NEVER invent or hallucinate tool outputs

        OUTPUT REQUIREMENTS:
        1. Be concise - summarize results clearly
        2. Include relevant details
        3. For code examples, show complete working code
        4. Suggest next steps when applicable

        ERROR HANDLING:
        - If a tool fails, explain why
        - Ask for clarification if needed"""

    @classmethod
    def get_llm(cls) -> ChatOpenAI:
        """Get or initialize the LLM instance."""
        if cls._llm_instance is None:
            cls._llm_instance = cls._initialize_llm()
        return cls._llm_instance

    @classmethod
    def get_agent(cls):
        """
        Get or initialize the agent runtime.

        LangChain v1: create_agent(model, tools=..., system_prompt=...) is the standard approach.
        The returned object is invokable via agent.invoke({"messages": [...]})
        and it executes tool calls internally.
        """
        if cls._agent_instance is not None:
            return cls._agent_instance

        llm = cls.get_llm()
        tool_list = tools.get_all_tools()
        print([(type(t).__name__, t.name) for t in tool_list])

        cls._agent_instance = create_agent(
            model=llm,
            tools=tool_list,
            system_prompt=cls.SYSTEM_PROMPT,
        )
        return cls._agent_instance

    @classmethod
    def _initialize_llm(cls) -> ChatOpenAI:
        """Initialize ChatOpenAI for Foundry Local (OpenAI-compatible)."""
        model_cfg = settings.model

        # NOTE: You said you'll manage base_url. Keep it as-is in your environment/config.
        llm = ChatOpenAI(
            model=model_cfg.foundry_model,
            base_url="http://127.0.0.1:62670/v1",
            api_key="foundry-local",
            temperature=model_cfg.temperature,
            timeout=40,
            max_retries=1,
        )

        # Optional sanity check; remove if you don't want a startup call.
        try:
            llm.invoke("test")
        except Exception as e:
            logger.exception("LLM startup test failed.")
            raise

        return llm

    @classmethod
    def reset(cls) -> None:
        """Reset cached instances (useful for testing)."""
        cls._llm_instance = None
        cls._agent_instance = None


modal_loader = ModalLoader()
