# services/tool_executor.py
import json
import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tools from Foundry's JSON responses."""

    @staticmethod
    def extract_json_tool_call(response_text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON tool call from Foundry response."""
        try:
            # Try markdown code block
            json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Try direct JSON
            return json.loads(response_text)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON: {e}")
            return None

    @staticmethod
    def execute(tool_call: Dict[str, Any]) -> str:
        """Execute a single tool call with detailed error handling."""
        tool_name = tool_call.get("name")
        arguments = tool_call.get("arguments", {})

        logger.info(f"[EXECUTE] Tool: {tool_name}, Args: {arguments}")

        try:
            # Validate tool call structure
            if not tool_name:
                return "❌ Error: Tool name missing from call"

            if not isinstance(arguments, dict):
                return f"❌ Error: Tool arguments must be a dict, got {type(arguments).__name__}"

            # Import tool
            try:
                from tools import get_tool

                tool = get_tool(tool_name)
            except ImportError as e:
                return f"❌ Error: Cannot import tools module: {str(e)}"

            # Check tool exists
            if not tool:
                available = _get_available_tools()
                return f"❌ Tool '{tool_name}' not found.\nAvailable tools: {', '.join(available)}"

            # Execute tool
            try:
                result = tool.invoke(arguments)
                logger.info(f"[SUCCESS] {tool_name} completed")
                return str(result)

            except TypeError as e:
                # Wrong arguments
                return f"❌ Tool '{tool_name}' error:\nWrong arguments: {str(e)}\nExpected: {tool.args}"

            except ValueError as e:
                # Invalid argument values
                return f"❌ Tool '{tool_name}' error:\nInvalid values: {str(e)}"

            except FileNotFoundError as e:
                return f"❌ File not found: {str(e)}"

            except Exception as e:
                return f"❌ Tool '{tool_name}' failed:\n{str(e)}"

        except Exception as e:
            logger.error(f"Critical error in execute: {e}")
            return f"❌ Critical error: {str(e)}"


def _get_available_tools():
    """Get list of available tool names."""
    try:
        from tools import list_available_tools

        tools = list_available_tools()
        return [t.get("name", "unknown") for t in tools]
    except:
        return ["generate_code", "analyze_code", "save_memory"]
