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


code_writer = LlmAgent(
    name="code_writer_agent",
    model=hf_model,
    description="An agent that generates python code based on user requirements.",
    instruction="""
    You are a python code generation agent. Given a user's request, generate the appropriate code snippet.
    Ensure the code is efficient and follows best practices.
    Important: Return only the code without any additional text or explanations
    Output the code in ```python...``` format.
    """,
    output_key = "generated_code"
)