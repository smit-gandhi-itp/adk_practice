from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


ollama_llm = LiteLlm(
    model=f"ollama_chat/{OLLAMA_MODEL}",
    api_base=OLLAMA_API_BASE
)


question_answer_agent = LlmAgent(
    name="question_answer_agent", 
    description="""An agent that can answer user questions using web search.""",
    model=ollama_llm,
    instruction="""You are a helpful assistant that answers questions about the user's preferences.

    Here is some information about the user:
    Name: 
    {user_name}
    Preferences: 
    {user_preferences}""",
)

