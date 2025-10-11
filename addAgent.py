# minimal agent that hopefully invokes the proper tool

from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from autogen import AssistantAgent, UserProxyAgent
import os
os.environ.pop("AUTOGEN_CONFIG_LIST", None)

# activate .venv and run:
# pip install -U pyautogen langchain pydantic openai
# export MODEL_BASE_URL=http://localhost:11434/v1
# export MODEL_NAME=qwen2.5:3b-instruct
# export OPENAI_API_KEY=ollama
# python addAgent.py

# 1) llm config
# make sure you have pulled Qwen using the following command: ollama pull qwen2.5:3b-instruct

MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "http://localhost:11434/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:3b-instruct")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")

LLM_CONFIG = {
    "temperature": 0,
    "timeout": 120,
    "config_list": [
        {
            "model": MODEL_NAME,
            "api_key": OPENAI_API_KEY,
            "base_url": MODEL_BASE_URL,
            "api_type": "openai",
            "tool_choice": "required",
        }
    ],
}

# 2) langchain tool
class AddArgs(BaseModel):
    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")

class AddTool(BaseTool):
    name: str = "add"
    description: str = "Add two integers and return the sum as an integer."
    args_schema: Type[BaseModel] = AddArgs

    def _run(self, a: int, b: int) -> int:
        print(f"[AddTool] successfully invoked with a={a}, b={b}")
        return int(a) + int(b)

    async def _arun(self, a: int, b: int) -> int:
        return int(a) + int(b)

_add_tool = AddTool()
def add(a: int, b: int) -> int:
    return _add_tool.invoke({"a": a, "b": b})

# 3) agent building
SYSTEM_MESSAGE = (
    "You are a helpful assistant that MUST call tools when they are available.\n"
    "If the user asks to add numbers, you MUST call the 'add' tool with the correct arguments.\n"
    "Do NOT compute the sum yourself. Return only the final integer as plain text (no JSON, no prose)."
)

def build_agents():
    user = UserProxyAgent(
        name="user",
        human_input_mode="NEVER",
        code_execution_config={"use_docker": False}
    )

    assistant = AssistantAgent(
        name="adder_agent",
        system_message=SYSTEM_MESSAGE,
        llm_config=LLM_CONFIG,
        max_consecutive_auto_reply=3,
    )

    # register_for_llm and register_for_execution: these make the tool visible to the model and allow its execution when the model calls the tool
    assistant.register_for_llm(
        name="add",
        description="Add two integers and return the sum as an integer. Arguments: a (int), b (int).",
    )(add)

    user.register_for_execution(
        name="add",
    )(add)

    return user, assistant

def prompt() -> str:
    return "Add 37 and 23 using the add tool. Do not compute it yourself. Return only the integer."

if __name__ == "__main__":
    user, assistant = build_agents()
    result = user.initiate_chat(assistant, message=prompt())
    print("\nFinal:", result.summary)