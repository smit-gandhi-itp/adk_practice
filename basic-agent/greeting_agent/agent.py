from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


ollama_llm = LiteLlm(
    model=f"ollama_chat/{OLLAMA_MODEL}",
    api_base=OLLAMA_API_BASE,
)

root_agent = LlmAgent(
    name="greeting_agent",
    description="An agent that greets the user and offers assistance.",
    model=ollama_llm
)
