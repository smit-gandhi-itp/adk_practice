from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv, find_dotenv
import os
from pydantic import BaseModel, Field
from typing import List


load_dotenv(find_dotenv())

# =========================
# Phase 3 System Design Output Schema
# =========================

class Phase3SystemDesign(BaseModel):
    executive_summary: str = Field(
        ..., description="High-level overview of the project including name, type, purpose, core features, constraints, and user scale."
    )
    system_overview: str = Field(
        ..., description="Detailed description of the system, functional goals, user flows, and core features."
    )
    architecture_design: str = Field(
        ..., description="High-level architecture, components, data flow, and rationale for design choices."
    )
    database_design: str = Field(
        ..., description="Database type, schema, tables, relationships, transactions, replication, and consistency strategies."
    )
    security_and_compliance: str = Field(
        ..., description="Authentication, authorization, encryption, tokenization, compliance measures, and monitoring for security."
    )
    deployment_strategy: str = Field(
        ..., description="Deployment model, containerization, orchestration, CI/CD pipelines, and rollout strategy."
    )
    scalability_and_reliability: str = Field(
        ..., description="Load balancing, scaling strategies, caching, failover, disaster recovery, monitoring, and alerting."
    )
    cost_and_resource_estimation: str = Field(
        ..., description="Estimated infrastructure and operational costs, licensing, and scaling costs."
    )
    testing_and_qa_strategy: str = Field(
        ..., description="Unit, integration, end-to-end, load, stress, security, and user acceptance testing approach."
    )
    appendices: str = Field(
        ..., description="Glossary, diagrams, references, and any additional supporting material."
    )


# =========================
# LLM Configuration
# =========================

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ollama_chat/phi3")

ollama_llm = LiteLlm(
    model=OLLAMA_MODEL,
    api_base=OLLAMA_API_BASE,
)


# =========================
# Phase 3 System Design Agent
# =========================

design_document_agent = LlmAgent(
    name="design_document_agent",
    model=ollama_llm,
    output_schema=Phase3SystemDesign,
    description=(
        "Generates a full system design document based on Phase 1 inputs and Phase 2 clarification answers. "
        "Outputs all required sections for a Word-ready structured design document."
    ),
    instruction="""
You are a system design generation agent.

You have access to the following inputs:
- {phase_1_inputs}: initial project inputs (name, type, platform, description, core features, expected user scale, constraints)
- {phase_2_answers}: answers to clarification questions from Phase 2

Task:
- Generate a complete system design document in JSON format.
- Include all required sections as defined in the Phase3SystemDesign schema:
    1. executive_summary
    2. system_overview
    3. architecture_design
    4. database_design
    5. security_and_compliance
    6. deployment_strategy
    7. scalability_and_reliability
    8. cost_and_resource_estimation
    9. testing_and_qa_strategy
    10. appendices
- Each section must be fully populated with detailed, realistic content.
- Do NOT omit any section.
- Output MUST strictly follow the Phase3SystemDesign schema.
- Output JSON ONLY. No markdown, no extra text, no explanations.

Focus on providing practical, detailed guidance suitable for a technical team to implement the system.
""",
    output_key="phase_3_system_design"
)
