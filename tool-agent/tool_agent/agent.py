from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.models.lite_llm import LiteLlm
import os
from datetime import datetime

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


ollama_llm = LiteLlm(
    model=f"ollama_chat/{OLLAMA_MODEL}",
    api_base=OLLAMA_API_BASE
)

def get_current_time() -> dict:
    return {"current_time": datetime.now().isoformat()}

root_agent = LlmAgent(
    name="tool_agent", 
    description="""An agent that can use tools to assist the user with various tasks.""",
    model=ollama_llm,
    tools= [get_current_time],
    instruction="""You have access to the following tools:
    - get_current_time: Use this tool to get the current time in ISO format.
    When the user asks for the current time, use the get_current_time tool to provide an accurate response.""",
)

