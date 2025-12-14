"""
Tools Module - All available tools for the agent
"""

import json
from typing import Any, Dict, List, Optional

from langchain_core.tools import BaseTool, StructuredTool

# Import your tools
from tools.analyze_code import analyze_code
from tools.memory import list_memories, recall_memory, save_memory
from tools.py_codeAnalyst import read_and_generate_code


def _as_tool(obj: Any) -> BaseTool:
    """
    Ensure every tool is a LangChain BaseTool with OpenAI-compatible schema.
    - If already BaseTool: keep it
    - If callable: wrap it as a StructuredTool
    """
    if isinstance(obj, BaseTool):
        return obj
    if callable(obj):
        return StructuredTool.from_function(obj)
    raise TypeError(f"Unsupported tool type: {type(obj)}")


# Tool registry (normalize everything to BaseTool)
_RAW_TOOL_REGISTRY: Dict[str, Any] = {
    "read_and_generate_code": read_and_generate_code,
    "analyze_code": analyze_code,
    "save_memory": save_memory,
    "recall_memory": recall_memory,
    "list_memories": list_memories,
}

TOOL_REGISTRY: Dict[str, BaseTool] = {
    k: _as_tool(v) for k, v in _RAW_TOOL_REGISTRY.items()
}


def get_all_tools() -> List[BaseTool]:
    """Get all available tools."""
    return list(TOOL_REGISTRY.values())


def get_tool(name: str) -> Optional[BaseTool]:
    """Get specific tool by name."""
    return TOOL_REGISTRY.get(name)


def list_available_tools() -> str:
    """Get tool descriptions."""
    tools_info = {}
    for name, tool_obj in TOOL_REGISTRY.items():
        tools_info[name] = {"name": tool_obj.name, "description": tool_obj.description}
    return json.dumps(tools_info, indent=2)


__all__ = ["get_all_tools", "get_tool", "list_available_tools", "TOOL_REGISTRY"]
