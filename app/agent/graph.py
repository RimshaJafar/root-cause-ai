
from langchain.agents import create_agent

from app.agent.prompts import SYSTEM_PROMPT
from app.llm.model import get_model
from app.tools.registry import build_tools


def build_agent(project_root: str):

    model = get_model()
    tools = build_tools(project_root)

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent
