from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

ollama_llm = LiteLlm(
    model=f"ollama_chat/{OLLAMA_MODEL}",
    api_base=OLLAMA_API_BASE
)

news_analyst = LlmAgent(
    name="news_analyst",
    model=ollama_llm,
    description="News analyst agent",
    instruction="""
    You are a helpful assistant that can analyze news articles and provide a summary of the news.
    """
)