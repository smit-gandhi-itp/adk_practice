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





code_writer = LlmAgent(
    name="code_writer_agent",
    model=ollama_llm,
    description="An agent that generates python code based on user requirements.",
    instruction="""
    You are a python code generation agent. Given a user's request, generate the appropriate code snippet.
    Ensure the code is efficient and follows best practices.
    Important: Return only the code without any additional text or explanations
    Output the code in ```python...``` format.
    """,
    output_key = "generated_code"
)