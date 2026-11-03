
import re


FRAME_PATTERN = re.compile(
    r'^\s*File "(.+)", line (\d+), in (.+)$'
)

EXCEPTION_PATTERN = re.compile(
    r'^([A-Za-z_][\w.]*(?:Error|Exception|Interrupt|Exit|Warning))'
    r':\s*(.*)$'
)


def analyze_traceback(traceback_text: str) -> dict:
    """Extract factual information from a Python traceback."""

    if not traceback_text.strip():
        raise ValueError("Traceback cannot be empty.")

    frames = []

    for line in traceback_text.splitlines():
        match = FRAME_PATTERN.match(line)

        if match:
            file_path, line_number, function = match.groups()

            frames.append({
                "file": file_path,
                "line": int(line_number),
                "function": function,
            })

    exception_type = None
    message = None

    for line in reversed(traceback_text.splitlines()):
        match = EXCEPTION_PATTERN.match(line.strip())

        if match:
            exception_type, message = match.groups()
            break

    return {
        "exception_type": exception_type,
        "message": message,
        "frames": frames,
        "last_frame": frames[-1] if frames else None,
        "has_exception": exception_type is not None,
    }
