# RootCause AI 

**An AI-powered debugging investigation agent that analyzes Python tracebacks, explores project source code, and identifies likely root causes using evidence.**

## Overview

RootCause AI helps developers investigate software bugs by combining an LLM with Python-based investigation tools.

Instead of relying only on a bug description, the agent can inspect a selected project, analyze Python tracebacks, search source code, and read relevant files before generating a debugging report.

## Key Features

- **Traceback Analysis:** Extracts exception types, messages, stack frames, file paths, and line numbers.
- **Project Exploration:** Lists and reads files within a selected project.
- **Code Search:** Searches source files for functions, variables, and relevant text.
- **AI Investigation:** Uses an LLM-powered agent to investigate bugs with available tools.
- **Evidence-Based Reports:** Separates likely root causes from supporting evidence and limitations.
- **Read-Only Investigation:** Does not modify project files or execute shell commands.

## Architecture

```text
             Developer
                 |
                 v
             main.py
                 |
                 v
           Agent (LangChain)
                 |
                 v
          LangGraph Runtime
                 |
                 v
           LLM (Groq)
                 |
           Tool Calling
                 |
        +--------+---------+
        |        |         |
        v        v         v
    File Tools  Search   Traceback
                Tools     Analysis
        |        |         |
        +--------+---------+
                 |
                 v
         Investigation Report
```

## Technology Stack

- Python
- LangChain
- LangGraph
- Groq API
- Pydantic
- python-dotenv
- Pytest

## Project Structure

```text
root-cause-ai/
├── app/
│   ├── agent/
│   ├── llm/
│   ├── tools/
│   ├── analyzer.py
│   └── main.py
├── tests/
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd root-cause-ai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Never commit your actual API key.

### 5. Run the application

```bash
python -m app.main
```

Enter the path of the project you want to investigate, describe the bug, and paste the traceback. Type `END` on a separate line to finish entering the traceback.

### 6. Run tests

```bash
python -m pytest -q
```

## Current Development Status

**Milestone 2 — Core agent implementation completed.**

- Investigation tools implemented.
- LLM integration configured.
- LangChain agent created.
- LangGraph runtime integrated.
- Initial automated tests passing.

Further development will focus on advanced agent workflows, reliability, security, verification, and production readiness.

## Future Improvements

- Advanced investigation planning and orchestration.
- Improved evidence tracking.
- Conditional agent workflows.
- Isolated test execution for proposed fixes.
- Git diff and project-context analysis.
- Investigation history and API interface.

---

*Built as a practical project to explore professional agentic AI engineering and intelligent software debugging.*