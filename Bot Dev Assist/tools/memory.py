"""save_memory tool - Store data persistently across conversations."""

import json
import logging

from langchain.tools import ToolRuntime, tool

logger = logging.getLogger(__name__)


@tool
def save_memory(
    key: str, value: str, category: str = "general", runtime: ToolRuntime = None
) -> str:
    """Save information to persistent memory.

    This tool:
    - Saves data across conversations
    - Organizes by category (user_info, preferences, history, etc)
    - Persists in long-term store
    - Can be retrieved later

    Args:
        key: Memory key (e.g., "user_name", "project_path")
        value: Value to save (string)
        category: Category (user_info, preferences, history, context)
        runtime: Tool runtime for accessing store

    Returns:
        Confirmation message
    """
    try:
        if not runtime:
            return "❌ Error: Runtime context not available"

        logger.info(f"Saving to memory - {category}/{key}: {value[:50]}")

        # Get store from runtime
        store = runtime.store

        # Create namespace (category, key)
        namespace = (category,)

        # Save to store
        store.put(
            namespace,
            key,
            {"value": value, "timestamp": _get_timestamp(), "category": category},
        )

        logger.info(f"✅ Saved {category}/{key}")
        return f"✅ Saved to memory: {category}/{key}\nValue: {value[:100]}"

    except Exception as e:
        logger.error(f"Failed to save memory: {e}")
        return f"❌ Failed to save: {str(e)}"


@tool
def recall_memory(
    key: str, category: str = "general", runtime: ToolRuntime = None
) -> str:
    """Retrieve saved information from memory.

    Args:
        key: Memory key to retrieve
        category: Category to search
        runtime: Tool runtime for accessing store

    Returns:
        Saved value or "not found" message
    """
    try:
        if not runtime:
            return "❌ Error: Runtime context not available"

        store = runtime.store
        namespace = (category,)

        # Get from store
        result = store.get(namespace, key)

        if result and result.value:
            data = result.value
            logger.info(f"Retrieved: {category}/{key}")
            return f"📝 Retrieved from memory:\n{data['value']}"

        return f"⚠️ Not found in memory: {category}/{key}"

    except Exception as e:
        logger.error(f"Failed to recall: {e}")
        return f"❌ Failed to retrieve: {str(e)}"


@tool
def list_memories(category: str = "general", runtime: ToolRuntime = None) -> str:
    """List all saved items in a category.

    Args:
        category: Category to list
        runtime: Tool runtime

    Returns:
        List of saved items
    """
    try:
        if not runtime:
            return "❌ Error: Runtime context not available"

        store = runtime.store
        namespace = (category,)

        # Get all items in namespace
        items = store.get_all(namespace)

        if not items:
            return f"📭 No memories in category: {category}"

        result = f"📚 Memories in '{category}':\n"
        for key, data in items.items():
            result += f"  • {key}: {data.value if isinstance(data, dict) else data}\n"

        return result

    except Exception as e:
        logger.error(f"Failed to list: {e}")
        return f"❌ Failed to list: {str(e)}"


def _get_timestamp():
    """Get current timestamp."""
    from datetime import datetime

    return datetime.now().isoformat()
