from __future__ import annotations
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator , StrictStr, ConfigDict

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MultiChoiceQuestion(StrictBaseModel):
    type: Literal["multi_choice"]
    options: List[str]


# class ClarificationQuestions(StrictBaseModel):
#     questions: Dict[str, MultiChoiceQuestion]


## ---------- ##
## FOR GROQ ##
## ---------- ##

class ClarificationQuestionItem(StrictBaseModel):
    question_text: str
    type: Literal["multi_choice"]
    options: List[str]


class ClarificationQuestions(StrictBaseModel):
    questions: List[ClarificationQuestionItem]





class UserScale(StrictBaseModel):
    expected_active_users: str = Field(..., description="Example: 10k-100k MAU")
    concurrent_users: int = Field(..., description="Estimated peak concurrent users")


class ExecutiveSummary(StrictBaseModel):
    title: str
    project_type: str
    purpose: str
    core_features: List[str]
    constraints: List[str]
    user_scale: UserScale


class UserFlowStep(StrictBaseModel):
    name: str
    description: str
    entry_points: List[str]
    success_criteria: str


class SystemOverview(StrictBaseModel):
    functional_goals: List[str]
    non_functional_requirements: List[str]
    primary_user_personas: List[str]
    user_flows: List[UserFlowStep]
    assumptions: List[str]


class Component(StrictBaseModel):
    name: str
    responsibility: str
    technologies: List[str]
    interfaces: List[str]
    notes: str


class ArchitectureDesign(StrictBaseModel):
    overview: str
    components: List[Component]
    data_flow_diagram_refs: List[str]
    critical_interactions: List[str]
    rationale: List[str]


class TableColumn(StrictBaseModel):
    name: str
    type: str
    nullable: bool
    description: str


class TableSchema(StrictBaseModel):
    table_name: str
    description: str
    columns: List[TableColumn]
    indexes: List[str]


class DatabaseDesign(StrictBaseModel):
    db_type: str
    storage_characteristics: str
    schemas: List[TableSchema]
    relationships: List[str]
    transactions_and_consistency: str
    backup_and_replication: List[str]


class AuthStrategy(StrictBaseModel):
    method: str
    identity_provider: str
    session_management: str


class SecurityAndCompliance(StrictBaseModel):
    authentication: AuthStrategy
    authorization: List[str]
    encryption: List[str]
    compliance: List[str]
    monitoring_and_alerting: List[str]
    incident_response: str


class DeploymentStrategy(StrictBaseModel):
    model: str
    containerization: List[str]
    orchestration: str
    ci_cd: List[str]
    rollout_strategy: List[str]
    infra_as_code: str

class SloSlaTarget(StrictBaseModel):
    metric: str
    target: str
    measurement_window: str
    notes: str



class ScalabilityAndReliability(StrictBaseModel):
    load_balancing: List[str]
    autoscaling: List[str]
    caching_strategy: List[str]
    failover_and_dr: List[str]
    monitoring_metrics: List[str]
    slo_sla_targets: List[SloSlaTarget]


class CostItem(StrictBaseModel):
    name: str
    monthly_estimate_usd: float
    rationale: str


class CostAndResourceEstimation(StrictBaseModel):
    cost_items: List[CostItem]
    one_time_costs: List[CostItem]
    assumptions: List[str]
    licensing: List[str]


class TestPlan(StrictBaseModel):
    name: str
    scope: str
    tools: List[str]
    success_criteria: str


class TestingAndQAStrategy(StrictBaseModel):
    unit_testing: TestPlan
    integration_testing: TestPlan
    e2e_testing: TestPlan
    load_and_stress: TestPlan
    security_testing: TestPlan
    acceptance_criteria: List[str]


class GlossaryItem(StrictBaseModel):
    term: str
    definition: str


class DiagramRef(StrictBaseModel):
    id: str
    title: str
    filename: str
    description: str


class Appendices(StrictBaseModel):
    glossary: List[GlossaryItem]
    references: List[str]
    additional_notes: str


class MermaidDiagrams(StrictBaseModel):
    system_architecture: str
    user_flows: str
    database_er: str



class Phase3SystemDesign(StrictBaseModel):
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
    mermaid_diagrams: MermaidDiagrams




