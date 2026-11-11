
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
}

SENSITIVE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "secrets.json",
}

SENSITIVE_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}

MAX_FILE_SIZE = 100_000
MAX_LIST_RESULTS = 200


def is_sensitive_path(path: Path) -> bool:
    """Check whether a path contains sensitive names or directories."""
    parts = [part.lower() for part in path.parts]

    if any(part in IGNORED_DIRS for part in parts):
        return True

    name = path.name.lower()

    return (
        name in SENSITIVE_NAMES
        or name.startswith(".env")
        or path.suffix.lower() in SENSITIVE_SUFFIXES
    )


class ProjectFileTools:

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()

        if not self.project_root.is_dir():
            raise NotADirectoryError(
                "Project root must be an existing directory."
            )

    def _resolve_path(self, file_path: str) -> Path:
        requested = Path(file_path)

        if requested.is_absolute():
            raise ValueError("Absolute paths are not allowed.")

        resolved = (self.project_root / requested).resolve()

        if not resolved.is_relative_to(self.project_root):
            raise ValueError(
                "Access outside project is not allowed."
            )

        relative = resolved.relative_to(self.project_root)

        if is_sensitive_path(relative):
            raise PermissionError(
                "Access to this path is denied."
            )

        if not resolved.is_file():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        return resolved

    def read_file(self, file_path: str) -> dict:
        path = self._resolve_path(file_path)

        if path.stat().st_size > MAX_FILE_SIZE:
            raise ValueError("File is too large to read.")

        content = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        return {
            "file": file_path,
            "content": content,
            "success": True,
        }

    def list_files(self, directory: str = ".") -> dict:
        requested = Path(directory)

        if requested.is_absolute():
            raise ValueError("Absolute paths are not allowed.")

        target = (self.project_root / requested).resolve()

        if not target.is_relative_to(self.project_root):
            raise ValueError(
                "Access outside project is not allowed."
            )

        relative_target = target.relative_to(self.project_root)

        if is_sensitive_path(relative_target):
            raise PermissionError(
                "Access to this directory is denied."
            )

        if not target.is_dir():
            raise NotADirectoryError(
                f"Directory not found: {directory}"
            )

        files = []

        for path in target.rglob("*"):
            # Do not follow or include symbolic links.
            if path.is_symlink():
                continue

            try:
                relative = path.relative_to(self.project_root)

                if is_sensitive_path(relative):
                    continue

                if not path.is_file():
                    continue

                resolved = path.resolve()

                if not resolved.is_relative_to(self.project_root):
                    continue

                files.append(relative.as_posix())

                if len(files) >= MAX_LIST_RESULTS:
                    break

            except (OSError, ValueError):
                continue

        return {
            "directory": directory,
            "files": files,
            "truncated": len(files) >= MAX_LIST_RESULTS,
        }
