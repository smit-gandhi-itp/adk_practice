from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv, find_dotenv
import os
from pydantic import BaseModel, field_validator
from typing import Literal, List, Dict
from .prompts import AGENT_DESCRIPTION , AGENT_INSTRUCTION


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
    description=AGENT_DESCRIPTION,
    instruction=AGENT_INSTRUCTION,
    output_key="phase_2_clarification_questions",
)
