
from pathlib import Path

from app.tools.file_tools import (
    IGNORED_DIRS,
    MAX_FILE_SIZE,
    is_sensitive_path,
)


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


def search_code(project_root: str, query: str) -> dict:
    root = Path(project_root).resolve()

    if not root.is_dir():
        raise NotADirectoryError(
            "Invalid project directory."
        )

    if not query.strip():
        raise ValueError(
            "Search query cannot be empty."
        )

    results = []

    for file in root.rglob("*"):
        # Skip symbolic links to prevent external access.
        if file.is_symlink():
            continue

        try:
            relative = file.relative_to(root)

            if is_sensitive_path(relative):
                continue

            if not file.is_file():
                continue

            resolved = file.resolve()

            if not resolved.is_relative_to(root):
                continue

            if file.suffix.lower() not in SEARCHABLE_EXTENSIONS:
                continue

            if file.stat().st_size > MAX_FILE_SIZE:
                continue

            content = file.read_text(
                encoding="utf-8",
                errors="replace",
            )

            for line_number, line in enumerate(
                content.splitlines(),
                start=1,
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

        except (OSError, PermissionError, ValueError):
            continue

    return {
        "query": query,
        "results": results,
        "truncated": False,
    }
