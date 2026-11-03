import tempfile

from pathlib import Path

import pytest

from app.tools.file_tools import ProjectFileTools
from app.tools.search_tools import search_code


@pytest.fixture
def project():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)

        (root / "app").mkdir()

        (root / "app" / "auth.py").write_text(
            "def login_user():\n"
            "    return None\n",
            encoding="utf-8",
        )

        (root / "README.md").write_text(
            "RootCause AI test project",
            encoding="utf-8",
        )

        yield root


def test_read_file(project):
    tools = ProjectFileTools(str(project))

    result = tools.read_file("app/auth.py")

    assert result["success"] is True
    assert "login_user" in result["content"]


def test_reject_outside_path(project):
    tools = ProjectFileTools(str(project))

    with pytest.raises(ValueError):
        tools.read_file("../../secret.txt")


def test_reject_sensitive_file(project):
    (project / ".env").write_text(
        "SECRET=value",
        encoding="utf-8",
    )

    tools = ProjectFileTools(str(project))

    with pytest.raises(PermissionError):
        tools.read_file(".env")


def test_list_files(project):
    tools = ProjectFileTools(str(project))

    result = tools.list_files()

    assert "app/auth.py" in result["files"]
    assert "README.md" in result["files"]


def test_search_code(project):
    result = search_code(str(project), "login_user")

    assert len(result["results"]) == 1
    assert result["results"][0]["file"] == "app/auth.py"