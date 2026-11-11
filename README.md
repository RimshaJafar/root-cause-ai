# RootCause AI

**An AI-powered agentic debugging investigator built with Python, LangChain, and LangGraph.**

RootCause AI investigates software bugs by analyzing error tracebacks, exploring project source code, collecting evidence, evaluating findings, and generating structured debugging reports.

Unlike a simple chatbot, RootCause AI uses a multi-step agentic workflow with planning, investigation, evidence evaluation, conditional retries, and human approval.

## Features

- **Automated Investigation Planning:** Creates a structured plan based on the reported bug and traceback.
- **Traceback Analysis:** Extracts exception types, error messages, and relevant stack frames.
- **Project Exploration:** Lists project files and searches source code for relevant functions, variables, and errors.
- **AI-Powered Investigation:** Uses an LLM-powered agent with tools to inspect project files and collect evidence.
- **Evidence Evaluation:** Evaluates whether collected findings adequately support a likely root cause.
- **Conditional Investigation:** Repeats investigation when evidence is insufficient, within a configurable attempt limit.
- **Structured Debugging Reports:** Generates reports containing the bug summary, traceback analysis, investigation, likely root cause, supporting evidence, suggested fix, confidence, and limitations.
- **Human Approval:** Pauses for human review before completing the workflow.
- **Read-Only Investigation:** Inspects project files without modifying them or executing shell commands.
- **Security Protections:** Includes path traversal checks, sensitive-file filtering, symbolic-link restrictions, and file-size limits.

## Architecture

RootCause AI uses a graph-based workflow powered by LangGraph.

```text
                 START
                   |
                   v
                PLANNER
                   |
                   v
              INVESTIGATOR
                   |
                   v
                EVALUATOR
                   |
          +--------+--------+
          |                 |
       Sufficient       Insufficient
          |                 |
          v                 v
       FINALIZER       INVESTIGATOR
          |           (Retry within
          |            attempt limit)
          v
      HUMAN APPROVAL
          |
          v
          END
```

### Main Components

| Component | Responsibility |
|---|---|
| Planner | Creates the investigation plan |
| Investigator | Uses project tools to inspect source code |
| Evaluator | Determines whether evidence is sufficient |
| Finalizer | Generates the debugging report |
| Human Approval | Pauses the workflow for human review |

## Technology Stack

- Python
- LangGraph
- LangChain
- LangChain Groq
- Groq LLM API
- Pydantic
- python-dotenv
- pytest

## Project Structure

```text
root-cause-ai/
│
├── app/
│   ├── agent/
│   │   ├── approval.py
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   ├── prompts.py
│   │   ├── state.py
│   │   └── workflow.py
│   │
│   ├── llm/
│   │   └── model.py
│   │
│   ├── tools/
│   │   ├── file_tools.py
│   │   ├── registry.py
│   │   ├── search_tools.py
│   │   └── traceback_tool.py
│   │
│   ├── analyzer.py
│   └── main.py
│
├── tests/
│   ├── test_analyzer.py
│   ├── test_workflow.py
│   └── test_nodes_and_security.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/RimshaJafar/root-cause-ai.git
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

Get an API key from [Groq Console](https://console.groq.com/).

Never commit your `.env` file or expose your API key.

## Running RootCause AI

Start the application from the project root:

```bash
python -m app.main
```

You will be asked to provide:

1. The directory of the project you want to investigate.
2. A description of the reported bug.
3. The traceback, if available.

Type `END` on a new line when you finish entering the traceback.

RootCause AI then starts its investigation workflow and presents the generated report for human approval.

## Running Tests

Run the complete test suite:

```bash
python -m pytest -q
```

The project currently has **26 passing automated tests** covering:

- Traceback analysis
- Investigation workflow routing
- Conditional retries
- Maximum investigation attempts
- Human approval and rejection
- Evaluator decision handling
- Evaluator API failure handling
- Path traversal protection
- Sensitive-file filtering
- Symbolic-link restrictions

## Safety and Limitations

- RootCause AI is designed to inspect project files without modifying them.
- It does not execute shell commands or run proposed fixes.
- Investigation results depend on the supplied bug description, traceback, available source code, and LLM responses.
- Suggested fixes are recommendations and are not automatically applied or verified.
- Filesystem protections reduce unintended access but are not a substitute for operating-system-level isolation.
- Workflow checkpoints currently use in-memory storage and are not persisted across application restarts.
- An internet connection and a working Groq API key are required for LLM-powered investigation.

## Project Status

**Milestone 1:** Traceback Analysis

**Milestone 2:** Tool-Based AI Investigation

**Milestone 3:** Agentic Investigation Workflow

Implemented Milestone 3 capabilities include planning, investigation, evidence evaluation, conditional retries, report generation, and human approval.

Further development is planned.

## Author

**Rimsha Jafar**

GitHub: [RimshaJafar](https://github.com/RimshaJafar)

LinkedIn: [Rimsha Jafar](https://www.linkedin.com/in/rimsha-jafar/)