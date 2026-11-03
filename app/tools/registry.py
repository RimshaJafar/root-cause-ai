from langchain_core.tools import tool

from app.tools.file_tools import ProjectFileTools
from app.tools.search_tools import search_code
from app.tools.traceback_tool import analyze_traceback_tool


def build_tools(project_root: str):

    project = ProjectFileTools(project_root)

    @tool
    def read_file(file_path: str) -> dict:
        """Read a source file inside the selected project."""

        return project.read_file(file_path)

    @tool
    def list_files(directory: str = ".") -> dict:
        """List files inside the selected project directory."""

        return project.list_files(directory)

    @tool
    def search_project_code(query: str) -> dict:
        """Search project source code for a function, variable, or text."""

        return search_code(project_root, query)

    return [
        read_file,
        list_files,
        search_project_code,
        analyze_traceback_tool,
    ]