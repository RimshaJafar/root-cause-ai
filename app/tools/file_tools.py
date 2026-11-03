from pathlib import Path


IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
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
            raise ValueError("Access outside project is not allowed.")

        if any(part in IGNORED_DIRS for part in resolved.relative_to(
            self.project_root
        ).parts):
            raise PermissionError("Access to this directory is denied.")

        if (
            resolved.name.lower() in SENSITIVE_NAMES
            or resolved.suffix.lower() in SENSITIVE_SUFFIXES
            or resolved.name.lower().startswith(".env")
        ):
            raise PermissionError("Access to sensitive files is denied.")

        if not resolved.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        return resolved

    def read_file(self, file_path: str) -> dict:
        path = self._resolve_path(file_path)

        if path.stat().st_size > MAX_FILE_SIZE:
            raise ValueError("File is too large to read.")

        content = path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        return {
            "file": file_path,
            "content": content,
            "success": True,
        }


    def list_files(self, directory: str = ".") -> dict:
        if directory == ".":
            target = self.project_root
        else:
            requested = Path(directory)

            if requested.is_absolute():
                raise ValueError("Absolute paths are not allowed.")

            target = (
                self.project_root / requested
            ).resolve()

        if not target.is_relative_to(self.project_root):
            raise ValueError("Access outside project is not allowed.")

        if not target.is_dir():
            raise NotADirectoryError(
                f"Directory not found: {directory}"
            )

        files = []

        for path in target.rglob("*"):

            relative = path.relative_to(self.project_root)

            if any(part in IGNORED_DIRS for part in relative.parts):
                continue

            if (
                path.name.lower().startswith(".env")
                or path.name.lower() in SENSITIVE_NAMES
                or path.suffix.lower() in SENSITIVE_SUFFIXES
            ):
                continue

            if path.is_file():
                files.append(relative.as_posix())

            if len(files) >= 200:
                break

        return {
            "directory": directory,
            "files": files,
            "truncated": len(files) >= 200,
        }    