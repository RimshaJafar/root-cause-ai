
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.agent.nodes import evaluate_evidence
from app.tools.file_tools import ProjectFileTools
from app.tools.search_tools import search_code


# --------------------------------------------------
# Evaluator tests
# --------------------------------------------------

class FakeModel:

    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    def invoke(self, prompt):
        if self.error:
            raise self.error

        return SimpleNamespace(content=self.response)


def evaluator_state():
    return {
        "bug_report": "Application crashes when creating an order.",
        "traceback_text": "TypeError: unsupported operand types",
        "investigation_plan": ["Inspect order calculation."],
        "investigation_history": [
            "Inspected app/orders.py.",
            "Found a float being added to a string.",
        ],
    }


def test_evaluator_accepts_sufficient_decision(monkeypatch):
    fake_model = FakeModel(
        "DECISION: SUFFICIENT\nREASON: Source code confirms the cause."
    )

    monkeypatch.setattr(
        "app.agent.nodes.get_model",
        lambda: fake_model,
    )

    result = evaluate_evidence(evaluator_state())

    assert result["is_sufficient"] is True
    assert "SUFFICIENT" in result["evaluation_notes"]


def test_evaluator_rejects_insufficient_decision(monkeypatch):
    fake_model = FakeModel(
        "DECISION: INSUFFICIENT\nREASON: More evidence is needed."
    )

    monkeypatch.setattr(
        "app.agent.nodes.get_model",
        lambda: fake_model,
    )

    result = evaluate_evidence(evaluator_state())

    assert result["is_sufficient"] is False


def test_evaluator_rejects_invalid_decision(monkeypatch):
    fake_model = FakeModel(
        "The investigation looks complete."
    )

    monkeypatch.setattr(
        "app.agent.nodes.get_model",
        lambda: fake_model,
    )

    result = evaluate_evidence(evaluator_state())

    assert result["is_sufficient"] is False
    assert "invalid decision format" in result["evaluation_notes"]


def test_evaluator_handles_api_failure(monkeypatch):
    fake_model = FakeModel(
        error=RuntimeError("API unavailable")
    )

    monkeypatch.setattr(
        "app.agent.nodes.get_model",
        lambda: fake_model,
    )

    result = evaluate_evidence(evaluator_state())

    assert result["is_sufficient"] is False
    assert "evaluation failed" in result["evaluation_notes"]


# --------------------------------------------------
# Project file security tests
# --------------------------------------------------

def test_read_file_rejects_path_traversal(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    outside_file = tmp_path / "outside.txt"
    outside_file.write_text("private data", encoding="utf-8")

    tools = ProjectFileTools(str(project))

    with pytest.raises(ValueError):
        tools.read_file("../outside.txt")


def test_read_file_rejects_sensitive_files(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    secret_file = project / ".env"
    secret_file.write_text(
        "API_KEY=secret",
        encoding="utf-8",
    )

    tools = ProjectFileTools(str(project))

    with pytest.raises(PermissionError):
        tools.read_file(".env")


def test_list_files_excludes_sensitive_files(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    (project / "main.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )

    (project / ".env").write_text(
        "API_KEY=secret",
        encoding="utf-8",
    )

    (project / "credentials.json").write_text(
        "{}",
        encoding="utf-8",
    )

    tools = ProjectFileTools(str(project))
    result = tools.list_files()

    assert "main.py" in result["files"]
    assert ".env" not in result["files"]
    assert "credentials.json" not in result["files"]


def test_search_code_excludes_sensitive_files(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    (project / "main.py").write_text(
        "API_KEY = 'example'",
        encoding="utf-8",
    )

    (project / ".env").write_text(
        "API_KEY = 'secret'",
        encoding="utf-8",
    )

    result = search_code(str(project), "API_KEY")

    assert len(result["results"]) == 1
    assert result["results"][0]["file"] == "main.py"


def test_read_file_rejects_symlink_outside_project(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    outside_file = tmp_path / "outside.txt"
    outside_file.write_text(
        "private data",
        encoding="utf-8",
    )

    link = project / "external.txt"

    try:
        link.symlink_to(outside_file)
    except (OSError, NotImplementedError):
        pytest.skip("Symbolic links are unavailable on this system.")

    tools = ProjectFileTools(str(project))

    with pytest.raises(ValueError):
        tools.read_file("external.txt")


def test_list_files_skips_symbolic_links(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    outside_file = tmp_path / "outside.txt"
    outside_file.write_text(
        "private data",
        encoding="utf-8",
    )

    link = project / "external.txt"

    try:
        link.symlink_to(outside_file)
    except (OSError, NotImplementedError):
        pytest.skip("Symbolic links are unavailable on this system.")

    tools = ProjectFileTools(str(project))
    result = tools.list_files()

    assert "external.txt" not in result["files"]


def test_search_code_skips_symbolic_links(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    outside_file = tmp_path / "outside.py"
    outside_file.write_text(
        "SPECIAL_EXTERNAL_VALUE = 123",
        encoding="utf-8",
    )

    link = project / "external.py"

    try:
        link.symlink_to(outside_file)
    except (OSError, NotImplementedError):
        pytest.skip("Symbolic links are unavailable on this system.")

    result = search_code(
        str(project),
        "SPECIAL_EXTERNAL_VALUE",
    )

    assert result["results"] == []
