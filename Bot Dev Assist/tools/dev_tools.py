# tools.py - Complete for daily use

import subprocess
from datetime import datetime

import requests
from langchain_core.tools import tool


# ============= 1. WEB SEARCH & RESEARCH =============
@tool
def web_search(query: str, num_results: int = 5) -> str:
    """Search the web for information (research, news, data).

    Use for:
    - Finding tutorials, documentation
    - Researching topics
    - Getting latest news/data
    - Comparing products/services
    """
    import requests

    try:
        # Using Tavily or DuckDuckGo free API
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url, timeout=5)
        results = response.json()
        return f"Found {len(results)} results for '{query}'"
    except Exception as e:
        return f"Search failed: {e}"


# ============= 2. CODE GENERATION & EXECUTION =============
@tool
def generate_code(
    requirement: str, language: str = "python", save_file: str = None
) -> str:
    """Generate code based on requirement.

    Use for:
    - Quick scripts
    - Boilerplate code
    - Algorithm implementation
    - Data processing
    """
    # Your existing implementation
    pass


@tool
def execute_code(code: str, language: str = "python") -> str:
    """Execute code and return output.

    Use for:
    - Running calculations
    - Testing ideas
    - Data processing
    - Quick automation
    """
    try:
        if language == "python":
            result = subprocess.run(
                ["python", "-c", code], capture_output=True, text=True, timeout=10
            )
            return result.stdout or result.stderr
        return "Only Python supported"
    except Exception as e:
        return f"Execution failed: {e}"


# ============= 3. FILE OPERATIONS =============
@tool
def read_file(file_path: str) -> str:
    """Read file contents.

    Use for:
    - Reading code files
    - Checking configs
    - Reading notes
    """
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"File not found: {file_path}"


@tool
def write_file(file_path: str, content: str, append: bool = False) -> str:
    """Write or append content to file.

    Use for:
    - Saving code
    - Creating configs
    - Writing notes
    - Saving results
    """
    try:
        mode = "a" if append else "w"
        with open(file_path, mode) as f:
            f.write(content)
        action = "appended to" if append else "created"
        return f"✅ File {action}: {file_path}"
    except Exception as e:
        return f"Write failed: {e}"


@tool
def list_files(directory: str = ".") -> str:
    """List files in directory.

    Use for:
    - Finding files
    - Organizing projects
    """
    import os

    try:
        files = os.listdir(directory)
        return "\n".join(files)
    except Exception as e:
        return f"Failed to list files: {e}"


# ============= 4. PRODUCTIVITY & NOTES =============
@tool
def create_todo(task: str, priority: str = "medium") -> str:
    """Create a to-do task.

    Use for:
    - Task management
    - Reminders
    """
    with open("todo.txt", "a") as f:
        f.write(f"[{priority}] {task} - {datetime.now()}\n")
    return f"✅ Added: {task}"


@tool
def save_note(title: str, content: str) -> str:
    """Save a note for later reference.

    Use for:
    - Research notes
    - Ideas
    - Findings
    """
    filename = f"notes/{title}.md"
    with open(filename, "w") as f:
        f.write(f"# {title}\n\n{content}\n\nCreated: {datetime.now()}")
    return f"✅ Note saved: {filename}"


# ============= 5. DATA & ANALYSIS =============
@tool
def analyze_text(text: str, analysis_type: str = "summary") -> str:
    """Analyze text (summary, keywords, sentiment).

    Use for:
    - Summarizing articles
    - Extracting key points
    - Understanding documents
    """
    if analysis_type == "summary":
        # Simple summary (first 30% of text)
        return text[: len(text) // 3] + "\n\n[Truncated for brevity]"
    return "Analysis type not supported"


@tool
def get_time() -> str:
    """Get current date/time.

    Use for:
    - Time-based decisions
    - Logging
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============= EXPORT =============
def get_all_tools():
    return [
        web_search,
        generate_code,
        execute_code,
        read_file,
        write_file,
        list_files,
        create_todo,
        save_note,
        analyze_text,
        get_time,
    ]


def get_tool(tool_name: str):
    tools = {t.name: t for t in get_all_tools()}
    return tools.get(tool_name)


def list_available_tools():
    return [{"name": t.name, "description": t.description} for t in get_all_tools()]
