from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv, find_dotenv
import os
from .prompts import AGENT_DESCRIPTION , AGENT_INSTRUCTION
from ..schemas import ClarificationQuestions , MultiChoiceQuestion


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
# LLM Configuration
# -------------------------

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ollama_chat/phi3")

ollama_llm = LiteLlm(
    model=OLLAMA_MODEL
    # api_base=OLLAMA_API_BASE,
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
