
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import InvestigationState
from app.agent.nodes import (
    plan_investigation,
    investigate,
    evaluate_evidence,
    generate_final_report,
)
from app.agent.approval import human_approval


def route_after_evaluation(
    state: InvestigationState,
) -> str:

    if state.get("is_sufficient", False):
        return "finalize"

    if (
        state.get("attempt_count", 0)
        >= state.get("max_attempts", 3)
    ):
        return "finalize"

    return "investigate"


def build_workflow():

    workflow = StateGraph(InvestigationState)

    # Register nodes
    workflow.add_node(
        "planner",
        plan_investigation,
    )

    workflow.add_node(
        "investigator",
        investigate,
    )

    workflow.add_node(
        "evaluator",
        evaluate_evidence,
    )

    workflow.add_node(
        "finalizer",
        generate_final_report,
    )

    workflow.add_node(
        "human_approval",
        human_approval,
    )

    # Connect workflow
    workflow.add_edge(
        START,
        "planner",
    )

    workflow.add_edge(
        "planner",
        "investigator",
    )

    workflow.add_edge(
        "investigator",
        "evaluator",
    )

    # Conditional routing
    workflow.add_conditional_edges(
        "evaluator",
        route_after_evaluation,
        {
            "investigate": "investigator",
            "finalize": "finalizer",
        },
    )

    workflow.add_edge(
        "finalizer",
        "human_approval",
    )

    workflow.add_edge(
        "human_approval",
        END,
    )

    # Checkpointer is required for interrupt/resume.
    memory = MemorySaver()

    return workflow.compile(
        checkpointer=memory,
    )
