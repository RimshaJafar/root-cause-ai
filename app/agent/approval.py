
from langgraph.types import interrupt

from app.agent.state import InvestigationState


def human_approval(
    state: InvestigationState,
) -> dict:

    decision = interrupt(
        {
            "message": "Review the investigation report.",
            "report": state.get("final_report", ""),
            "question": "Do you approve this report?",
        }
    )

    return {
        "approved": bool(decision),
    }
