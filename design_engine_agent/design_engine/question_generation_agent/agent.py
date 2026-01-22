from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv, find_dotenv
import os
from pydantic import BaseModel, field_validator
from typing import Literal, List, Dict


load_dotenv(find_dotenv())


# =========================
# Context to this agent will be inputs from phase one inside "phase_1_inputs"
# =========================

# return {
#         "project_name": project_name,
#         "project_type": project_type,
#         "platform": platform,
#         "description": description,
#         "core_features": core_features,
#         "expected_user_scale": expected_user_scale,
#         "constraints": constraints,
#     }


# -------------------------
# Question Shape (ONLY multi_choice)
# -------------------------

class MultiChoiceQuestion(BaseModel):
    type: Literal["multi_choice"]
    options: List[str]

    # @field_validator("options")
    # @classmethod
    # def validate_options(cls, options: List[str]):
    #     if options[-1].lower() != "other":
    #         raise ValueError('The 6th option must be "Other"')
    #     return options


# -------------------------
# Final Output Schema
# -------------------------

class ClarificationQuestions(BaseModel):
    questions: Dict[str, MultiChoiceQuestion]


# -------------------------
# LLM Configuration
# -------------------------

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ollama_chat/phi3")

ollama_llm = LiteLlm(
    model=OLLAMA_MODEL,
    api_base=OLLAMA_API_BASE,
)


# -------------------------
# Question Generation Agent
# -------------------------

question_generation_agent = LlmAgent(
    name="question_generation_agent",
    model=ollama_llm,
    output_schema=ClarificationQuestions,
    description=(
        "Generates clarification questions as multi_choice only. "
        "The last option is 'Other'. "
        "Structured JSON output only."
    ),
    instruction="""
You are a clarification question generation agent.

Input: {phase_1_inputs}

Generate only clarification questions as multi_choice. Rules:
- Each question must be a standalone, human-readable string.
- Each question must have exactly 6 options.
- The last option MUST be 'Other'.
- Options must be clear, mutually exclusive, and realistic.
- Do NOT repeat input from phase_1_inputs.
- Output MUST strictly follow the Pydantic schema:

## Sample Template Output
{
  "questions": {
    "Question text here": {
      "type": "multi_choice",
      "options": ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5", "Other"]
    }
  }
}

- Output JSON ONLY. No explanations, no markdown, no extra text, Don't include the sample template in the output.
""",
output_key="phase_2_clarification_questions",
)
