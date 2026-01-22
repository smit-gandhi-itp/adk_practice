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



code_reviewer = LlmAgent(
    name="code_reviewer_agent",
    model=ollama_llm,
    description="An agent that reviews python code snippets and suggests improvements.",
    instruction="""
    Review the code from previous step from {generated_code}.
    You are a python code reviewer agent. Given a code snippet, analyze it and suggest improvements or point out potential issues.
    Ensure your feedback is constructive and follows best practices.
    Important: Return only your review comments without any additional text.
    If excellent say no major issues found.
    """,
    output_key="review_comments"
)
