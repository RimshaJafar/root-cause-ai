
import pytest
from langgraph.types import Command

import app.agent.workflow as workflow_module


# --------------------------------------------------
# Routing unit tests
# --------------------------------------------------

def test_route_to_finalizer_when_evidence_is_sufficient():

    state = {
        "is_sufficient": True,
        "attempt_count": 1,
        "max_attempts": 3,
    }

    assert (
        workflow_module.route_after_evaluation(state)
        == "finalize"
    )


def test_route_to_investigator_when_evidence_is_insufficient():

    state = {
        "is_sufficient": False,
        "attempt_count": 1,
        "max_attempts": 3,
    }

    assert (
        workflow_module.route_after_evaluation(state)
        == "investigate"
    )


def test_route_to_finalizer_when_max_attempts_are_reached():

    state = {
        "is_sufficient": False,
        "attempt_count": 3,
        "max_attempts": 3,
    }

    assert (
        workflow_module.route_after_evaluation(state)
        == "finalize"
    )


def test_route_to_finalizer_when_attempts_exceed_limit():

    state = {
        "is_sufficient": False,
        "attempt_count": 4,
        "max_attempts": 3,
    }

    assert (
        workflow_module.route_after_evaluation(state)
        == "finalize"
    )


# --------------------------------------------------
# Mock workflow nodes
# --------------------------------------------------

def setup_mock_nodes(monkeypatch, evaluator):

    def fake_planner(state):
        return {
            "investigation_plan": [
                "Inspect relevant source code.",
                "Analyze traceback.",
                "Identify root cause.",
            ],
            "attempt_count": 0,
            "investigation_history": [],
        }

    def fake_investigator(state):

        attempt = state.get("attempt_count", 0) + 1

        history = list(
            state.get("investigation_history", [])
        )

        history.append(
            f"Mock investigation attempt {attempt}"
        )

        return {
            "attempt_count": attempt,
            "investigation_history": history,
            "current_findings": (
                f"Findings from attempt {attempt}"
            ),
        }

    def fake_finalizer(state):
        return {
            "final_report": "Mock final investigation report."
        }

    monkeypatch.setattr(
        workflow_module,
        "plan_investigation",
        fake_planner,
    )

    monkeypatch.setattr(
        workflow_module,
        "investigate",
        fake_investigator,
    )

    monkeypatch.setattr(
        workflow_module,
        "evaluate_evidence",
        evaluator,
    )

    monkeypatch.setattr(
        workflow_module,
        "generate_final_report",
        fake_finalizer,
    )


def create_initial_state(max_attempts=3):

    return {
        "project_root": "sample-project",
        "bug_report": "Sample bug",
        "traceback_text": "Sample traceback",
        "investigation_plan": [],
        "investigation_history": [],
        "attempt_count": 0,
        "max_attempts": max_attempts,
        "is_sufficient": False,
        "approved": False,
    }


def create_config():

    import uuid

    return {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
        },
        "recursion_limit": 30,
    }


# --------------------------------------------------
# Full workflow tests
# --------------------------------------------------

def test_workflow_retries_until_evidence_is_sufficient(
    monkeypatch,
):

    def fake_evaluator(state):

        sufficient = state["attempt_count"] >= 2

        return {
            "is_sufficient": sufficient,
            "evaluation_notes": (
                "Evidence sufficient."
                if sufficient
                else "More investigation required."
            ),
        }

    setup_mock_nodes(
        monkeypatch,
        fake_evaluator,
    )

    workflow = workflow_module.build_workflow()

    config = create_config()

    result = workflow.invoke(
        create_initial_state(),
        config=config,
    )

    # The workflow should perform two attempts.
    assert result["attempt_count"] == 2

    # It should generate a final report.
    assert (
        result["final_report"]
        == "Mock final investigation report."
    )

    # It should pause for human approval.
    assert result.get("__interrupt__")

    # Resume with approval.
    result = workflow.invoke(
        Command(resume=True),
        config=config,
    )

    assert result["approved"] is True


def test_workflow_stops_at_maximum_attempts(
    monkeypatch,
):

    def fake_evaluator(state):
        return {
            "is_sufficient": False,
            "evaluation_notes": "Evidence is insufficient.",
        }

    setup_mock_nodes(
        monkeypatch,
        fake_evaluator,
    )

    workflow = workflow_module.build_workflow()

    config = create_config()

    result = workflow.invoke(
        create_initial_state(max_attempts=3),
        config=config,
    )

    # It must not exceed three attempts.
    assert result["attempt_count"] == 3

    # It should still generate a report.
    assert result["final_report"]

    assert result.get("__interrupt__")


def test_workflow_handles_human_rejection(
    monkeypatch,
):

    def fake_evaluator(state):
        return {
            "is_sufficient": True,
            "evaluation_notes": "Evidence is sufficient.",
        }

    setup_mock_nodes(
        monkeypatch,
        fake_evaluator,
    )

    workflow = workflow_module.build_workflow()

    config = create_config()

    result = workflow.invoke(
        create_initial_state(),
        config=config,
    )

    assert result.get("__interrupt__")

    # Resume with rejection.
    result = workflow.invoke(
        Command(resume=False),
        config=config,
    )

    assert result["approved"] is False
    assert result["attempt_count"] == 1
