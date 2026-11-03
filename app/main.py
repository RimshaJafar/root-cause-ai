from pathlib import Path

from app.agent.graph import build_agent


def main():

    print("\n========== ROOTCAUSE AI ==========\n")

    project_root = input(
        "Enter the project directory to investigate: "
    ).strip().strip('"')

    project_path = Path(project_root).expanduser().resolve()

    if not project_path.is_dir():
        print("Error: The selected project directory does not exist.")
        return

    bug_report = input(
        "\nDescribe the bug: "
    ).strip()

    if not bug_report:
        print("Error: Bug description cannot be empty.")
        return

    print(
        "\nPaste the traceback. Type END on a new line when finished."
    )

    traceback_lines = []

    while True:
        line = input()

        if line.strip() == "END":
            break

        traceback_lines.append(line)

    traceback_text = "\n".join(traceback_lines)

    user_message = f"""
BUG REPORT:
{bug_report}

TRACEBACK:
{traceback_text if traceback_text.strip() else "No traceback supplied."}

Investigate this bug using the available project tools.
Return an evidence-based debugging report.
"""

    print("\nStarting investigation...\n")

    try:
        agent = build_agent(str(project_path))

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ]
            },
            config={
                "recursion_limit": 15
            },
        )

        final_message = result["messages"][-1]

        print("\n========== INVESTIGATION REPORT ==========\n")
        print(final_message.content)

    except Exception as error:
        print(f"\nInvestigation failed: {error}")


if __name__ == "__main__":
    main()