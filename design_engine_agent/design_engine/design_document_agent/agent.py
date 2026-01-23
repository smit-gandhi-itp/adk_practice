from __future__ import annotations

import os
from dotenv import load_dotenv, find_dotenv
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .prompts import AGENT_DESCRIPTION , AGENT_INSTRUCTION

# ==================================================
# Environment
# ==================================================

load_dotenv(find_dotenv())

# ==================================================
# Phase 3 – Structured System Design Schema
# (LLM must fully populate all fields)
# ==================================================


class UserScale(BaseModel):
    expected_active_users: str = Field(..., description="Example: 10k-100k MAU")
    concurrent_users: int = Field(..., description="Estimated peak concurrent users")


class ExecutiveSummary(BaseModel):
    title: str
    project_type: str
    purpose: str
    core_features: List[str]
    constraints: List[str]
    user_scale: UserScale


class UserFlowStep(BaseModel):
    name: str
    description: str
    entry_points: List[str]
    success_criteria: str


class SystemOverview(BaseModel):
    functional_goals: List[str]
    non_functional_requirements: List[str]
    primary_user_personas: List[str]
    user_flows: List[UserFlowStep]
    assumptions: List[str]


class Component(BaseModel):
    name: str
    responsibility: str
    technologies: List[str]
    interfaces: List[str]
    notes: str


class ArchitectureDesign(BaseModel):
    overview: str
    components: List[Component]
    data_flow_diagram_refs: List[str]
    critical_interactions: List[str]
    rationale: List[str]


class TableColumn(BaseModel):
    name: str
    type: str
    nullable: bool
    description: str


class TableSchema(BaseModel):
    table_name: str
    description: str
    columns: List[TableColumn]
    indexes: List[str]


class DatabaseDesign(BaseModel):
    db_type: str
    storage_characteristics: str
    schemas: List[TableSchema]
    relationships: List[str]
    transactions_and_consistency: str
    backup_and_replication: List[str]


class AuthStrategy(BaseModel):
    method: str
    identity_provider: str
    session_management: str


class SecurityAndCompliance(BaseModel):
    authentication: AuthStrategy
    authorization: List[str]
    encryption: List[str]
    compliance: List[str]
    monitoring_and_alerting: List[str]
    incident_response: str


class DeploymentStrategy(BaseModel):
    model: str
    containerization: List[str]
    orchestration: str
    ci_cd: List[str]
    rollout_strategy: List[str]
    infra_as_code: str


class ScalabilityAndReliability(BaseModel):
    load_balancing: List[str]
    autoscaling: List[str]
    caching_strategy: List[str]
    failover_and_dr: List[str]
    monitoring_metrics: List[str]
    slo_sla_targets: Dict[str, Any]


class CostItem(BaseModel):
    name: str
    monthly_estimate_usd: float
    rationale: str


class CostAndResourceEstimation(BaseModel):
    cost_items: List[CostItem]
    one_time_costs: List[CostItem]
    assumptions: List[str]
    licensing: List[str]


class TestPlan(BaseModel):
    name: str
    scope: str
    tools: List[str]
    success_criteria: str


class TestingAndQAStrategy(BaseModel):
    unit_testing: TestPlan
    integration_testing: TestPlan
    e2e_testing: TestPlan
    load_and_stress: TestPlan
    security_testing: TestPlan
    acceptance_criteria: List[str]


class GlossaryItem(BaseModel):
    term: str
    definition: str


class DiagramRef(BaseModel):
    id: str
    title: str
    filename: str
    description: str


class Appendices(BaseModel):
    glossary: List[GlossaryItem]
    diagrams: List[DiagramRef]
    references: List[str]
    additional_notes: str


class Phase3SystemDesign(BaseModel):
    """
    Fully structured Phase 3 output.
    This model is intentionally strict so the LLM must
    generate rich, Word-friendly data (lists, tables, sections).
    """

    executive_summary: ExecutiveSummary
    system_overview: SystemOverview
    architecture_design: ArchitectureDesign
    database_design: DatabaseDesign
    security_and_compliance: SecurityAndCompliance
    deployment_strategy: DeploymentStrategy
    scalability_and_reliability: ScalabilityAndReliability
    cost_and_resource_estimation: CostAndResourceEstimation
    testing_and_qa_strategy: TestingAndQAStrategy
    appendices: Appendices


# ==================================================
# LLM Configuration (Ollama via LiteLLM)
# ==================================================

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ollama_chat/phi3")

ollama_llm = LiteLlm(
    model=OLLAMA_MODEL,
    api_base=OLLAMA_API_BASE,
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
