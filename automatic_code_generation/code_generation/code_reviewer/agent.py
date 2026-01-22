from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os
from dotenv import load_dotenv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")

os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

hf_model = LiteLlm(
    "huggingface/together/deepseek-ai/DeepSeek-R1"
)

code_reviewer = LlmAgent(
    name="code_reviewer_agent",
    model=hf_model,
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
