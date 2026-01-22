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


code_refactorer = LlmAgent(
    name="code_refactorer_agent",
    model=hf_model,
    description="An agent that refactors python code snippets to improve readability and efficiency.",
    instruction="""
    Apply review comments from previous step from {review_comments} to {generated_code} and generate new code snippet.
    Output only the final improve code in ```python...``` format.
    """,
    output_key="refactored_code"
)