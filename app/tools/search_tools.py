from pathlib import Path

from app.tools.file_tools import IGNORED_DIRS, SENSITIVE_NAMES


SEARCHABLE_EXTENSIONS = {
    ".py",
    ".dart",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".kt",
    ".go",
    ".rs",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
    ".txt",
}

MAX_RESULTS = 30
MAX_FILE_SIZE = 100_000


def search_code(project_root: str, query: str) -> dict:
    root = Path(project_root).resolve()

    if not root.is_dir():
        raise NotADirectoryError("Invalid project directory.")

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    results = []

    for file in root.rglob("*"):

        if not file.is_file():
            
            continue

        relative = file.relative_to(root)

        if any(part in IGNORED_DIRS for part in relative.parts):
            continue

        if (
            file.name.lower() in SENSITIVE_NAMES
            or file.name.lower().startswith(".env")
            or file.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}
        ):
            continue

        if file.suffix.lower() not in SEARCHABLE_EXTENSIONS:
            continue

        try:
            if file.stat().st_size > MAX_FILE_SIZE:
                continue

            content = file.read_text(
                encoding="utf-8",
                errors="replace"
            )

            for line_number, line in enumerate(
                content.splitlines(), start=1
            ):
                if query.casefold() in line.casefold():
                    results.append({
                        "file": relative.as_posix(),
                        "line": line_number,
                        "content": line.strip()[:300],
                    })

                    if len(results) >= MAX_RESULTS:
                        return {
                            "query": query,
                            "results": results,
                            "truncated": True,
                        }

        except (OSError, PermissionError):
            continue

    return {
        "query": query,
        "results": results,
        "truncated": False,
    }