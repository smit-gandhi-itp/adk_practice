from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os
from dotenv import load_dotenv , find_dotenv
from pathlib import Path


load_dotenv(find_dotenv())

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

ollama_llm = LiteLlm(
    model=f"ollama_chat/{OLLAMA_MODEL}",
    api_base=OLLAMA_API_BASE,
)



code_refactorer = LlmAgent(
    name="code_refactorer_agent",
    model=ollama_llm,
    description="An agent that refactors python code snippets to improve readability and efficiency.",
    instruction="""
    Apply review comments from previous step from {review_comments} to {generated_code} and generate new code snippet.
    Output only the final improve code in ```python...``` format.
    """,
    output_key="refactored_code"
)