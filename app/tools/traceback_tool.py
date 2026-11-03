from langchain_core.tools import tool

from app.analyzer import analyze_traceback


@tool
def analyze_traceback_tool(traceback_text: str) -> dict:
    """Analyze a Python traceback and extract exception details,
    stack frames, file paths, line numbers, and the last frame.
    """
    return analyze_traceback(traceback_text)