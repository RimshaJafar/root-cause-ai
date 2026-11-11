
from typing import TypedDict


class InvestigationState(TypedDict, total=False):
    # User input
    project_root: str
    bug_report: str
    traceback_text: str

    # Planning
    investigation_plan: list[str]

    # Investigation
    investigation_history: list[str]
    current_findings: str

    # Evaluation and workflow control
    evaluation_notes: str
    attempt_count: int
    max_attempts: int
    is_sufficient: bool

    # Final report and approval
    final_report: str
    approved: bool
