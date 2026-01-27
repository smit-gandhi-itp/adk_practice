import os
from dotenv import load_dotenv, find_dotenv


from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .prompts import AGENT_DESCRIPTION , AGENT_INSTRUCTION
from ..schemas import *


# ==================================================
# Environment
# ==================================================

load_dotenv(find_dotenv())

# ==================================================
# Phase 3 – Structured System Design Schema
# (LLM must fully populate all fields)
# ==================================================


# ==================================================
# LLM Configuration (Ollama via LiteLLM)
# ==================================================

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ollama_chat/phi3")

ollama_llm = LiteLlm(
    model=OLLAMA_MODEL
    # api_base=OLLAMA_API_BASE,
)


# ==================================================
# Phase 3 System Design Agent
# ==================================================

design_document_agent = LlmAgent(
    name="design_document_agent",
    model=ollama_llm,
    output_schema=Phase3SystemDesign,
    description=AGENT_DESCRIPTION,
    instruction=AGENT_INSTRUCTION,
    output_key="phase_3_system_design"
)

# ==================================================
# End of file
# ==================================================
