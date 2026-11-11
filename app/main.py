
from pathlib import Path
from uuid import uuid4

from langgraph.types import Command

from app.agent.workflow import build_workflow


def main():

    print("\n========== ROOTCAUSE AI ==========\n")

    project_root = input(
        "Enter the project directory to investigate: "
    ).strip().strip('"')

    project_path = Path(
        project_root
    ).expanduser().resolve()

    if not project_path.is_dir():
        print(
            "\nError: The selected project directory does not exist."
        )
        return

    bug_report = input(
        "\nDescribe the bug: "
    ).strip()

    if not bug_report:
        print("\nError: Bug description cannot be empty.")
        return

    print(
        "\nPaste the traceback. "
        "Type END on a new line when finished."
    )

    traceback_lines = []

    while True:
        line = input()

        if line.strip() == "END":
            break

        traceback_lines.append(line)

    traceback_text = "\n".join(traceback_lines)

    initial_state = {
        "project_root": str(project_path),
        "bug_report": bug_report,
        "traceback_text": traceback_text,
        "attempt_count": 0,
        "max_attempts": 3,
        "investigation_history": [],
        "investigation_plan": [],
        "is_sufficient": False,
        "approved": False,
    }

    config = {
        "configurable": {
            "thread_id": str(uuid4()),
        },
        "recursion_limit": 30,
    }

    try:

        workflow = build_workflow()

        print("\nStarting RootCause AI workflow...\n")

        result = workflow.invoke(
            initial_state,
            config=config,
        )

        # Check whether the workflow paused for approval.
        interruptions = result.get("__interrupt__", [])

        if interruptions:

            print(
                "\n========== REPORT READY FOR REVIEW ==========\n"
            )

            print(result.get("final_report", ""))

            approval = input(
                "\nDo you approve this report? (yes/no): "
            ).strip().lower()

            approved = approval in {
                "yes",
                "y",
            }

            # Resume the paused workflow.
            result = workflow.invoke(
                Command(resume=approved),
                config=config,
            )

        if result.get("approved", False):
            print("\nReport approved.")
        else:
            print("\nReport was not approved.")

        print(
            "\nInvestigation attempts:",
            result.get("attempt_count", 0),
        )

    except KeyboardInterrupt:
        print("\nInvestigation cancelled by user.")

    except Exception as error:
        print(
            f"\nInvestigation failed: {error}"
        )


if __name__ == "__main__":
    main()
