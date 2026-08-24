"""FastAPI Router for Semantic Metadata Catalog, Data Lineage, Quality Agent, Ask ORBIT-X & Human Feedback."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any

from app.core.schemas import (
    DataCatalogResponse,
    DataCatalogEntry,
    DataLineageResponse,
    DataLineageNode,
    DataQualityReport,
    TrustLayerResponse,
    HumanFeedbackRequest,
    HumanFeedbackResponse,
    ContextQualityMetrics,
    GovernedContextStep,
    GovernedContextAuditReport,
    AgentEvalSuiteReport,
)
from app.simulation.simulator import get_simulator
from app.intelligence.context_graph import get_context_graph_engine
from app.intelligence.data_quality_agent import get_data_quality_agent
from app.intelligence.trust_layer import get_trust_layer_engine
from app.context.evaluation.context_evaluator import get_context_quality_evaluator
from app.context.evaluation.agent_evaluator import get_agent_evaluation_suite

router = APIRouter(prefix="/api/context", tags=["Context Layer, Lineage & Semantic Metadata"])


@router.get("/governance/entities", response_model=List[DataLineageNode])
async def get_governed_entities(satellite_id: Optional[str] = "SAT-03"):
    """
    Returns all 10 canonical context graph entities with complete governance state:
    asset_status (VERIFIED, DRAFT, DEPRECATED), owner, last_reviewed, freshness, quality_score, schema_version.
    """
    engine = get_context_graph_engine()
    return engine.get_governed_entities(satellite_id=satellite_id or "SAT-03")


@router.get("/governance/audit", response_model=GovernedContextAuditReport)
async def audit_context_governance():
    """
    Audits the entire 10-entity context graph against the governance policy:
    distinguishes trusted assets from untrusted, draft, deprecated, or stale assets.
    """
    engine = get_context_graph_engine()
    return engine.validate_context_governance()


@router.get("/catalog", response_model=DataCatalogResponse)
async def get_data_catalog():
    """Returns the full semantic metadata catalog of operational and ML datasets."""
    engine = get_context_graph_engine()
    return engine.get_catalog()


@router.get("/catalog/search", response_model=List[DataCatalogEntry])
async def search_data_catalog(q: str = Query(..., description="Natural language search query across dataset metadata")):
    """Searches dataset catalog by name, column descriptions, and downstream consumers."""
    engine = get_context_graph_engine()
    return engine.search_datasets(q)


@router.get("/catalog/{dataset_name}", response_model=DataCatalogEntry)
async def get_dataset_metadata(dataset_name: str):
    """Fetches comprehensive metadata for a specific dataset."""
    engine = get_context_graph_engine()
    meta = engine.get_dataset_metadata(dataset_name)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found in catalog.")
    return meta


@router.get("/catalog/{dataset_name}/dependencies")
async def get_dataset_dependencies(dataset_name: str) -> Dict[str, Any]:
    """Returns downstream ML models and decision pipelines dependent on this dataset."""
    engine = get_context_graph_engine()
    return engine.get_dataset_dependencies(dataset_name)


@router.get("/lineage/{mission_id}", response_model=DataLineageResponse)
async def get_decision_lineage(mission_id: str, satellite_id: Optional[str] = None):
    """
    Traverses the Data Lineage Graph for a given mission assignment:
    Raw Telemetry -> Cleaned Dataset -> Feature Table -> ML Prediction -> CP-SAT Optimization -> Decision -> Outcome.
    """
    engine = get_context_graph_engine()
    return engine.trace_decision_lineage(mission_id=mission_id, satellite_id=satellite_id)


@router.get("/quality/audit", response_model=DataQualityReport)
async def audit_telemetry_quality():
    """Runs the Data Quality Agent over current constellation telemetry frames."""
    sim = get_simulator()
    agent = get_data_quality_agent()
    frames = [s.telemetry for s in sim.satellites]
    return agent.audit_telemetry_stream(frames)


@router.get("/quality/metrics", response_model=ContextQualityMetrics)
async def get_context_quality_metrics():
    """
    Returns empirical, measured Context Quality metrics across all 6 pillars:
    metadata completeness, lineage coverage, freshness SLA compliance, overall quality,
    verified asset ratio, retrieval groundedness, and stale context rate.
    """
    evaluator = get_context_quality_evaluator()
    return evaluator.evaluate()


@router.post("/evaluation/agent-eval/run", response_model=AgentEvalSuiteReport)
async def run_agent_eval_suite():
    """
    Executes the formal reproducible Agent Evaluation Suite measuring all 7 dimensions:
    context_relevance, tool_selection_accuracy, evidence_completeness, unsupported_claim_rate,
    missing_context_detection, tool_failure_recovery, and decision_consistency on real operational data.
    """
    suite = get_agent_evaluation_suite()
    return suite.run_suite()


@router.get("/evaluation/agent-eval/latest", response_model=AgentEvalSuiteReport)
async def get_latest_agent_eval_report():
    """
    Returns the latest evaluated Agent Benchmark Report across all 7 dimensions.
    """
    suite = get_agent_evaluation_suite()
    return suite.get_latest_report()


@router.get("/governed-pipeline/preview", response_model=List[GovernedContextStep])
async def get_governed_pipeline_preview():
    """
    Demonstrates the 6-step governed context execution sequence:
    discover_context -> identify_authoritative_dataset -> check_quality_freshness -> inspect_lineage -> retrieve_data -> reason.
    """
    trust_engine = get_trust_layer_engine()
    res = trust_engine.ask_orbitx("Why is Mission M-204 at risk?")
    return res.governed_context_steps


@router.get("/quality/drift_report", response_model=DataQualityReport)
async def get_synthetic_drift_report():
    """Returns a synthetic schema drift and missing value audit report for demonstrations."""
    agent = get_data_quality_agent()
    return agent.generate_synthetic_drift_test_report()


@router.post("/ask", response_model=TrustLayerResponse)
async def ask_orbitx(query: str = Query(..., description="Operational query for Ask ORBIT-X Trust Layer")):
    """
    'Ask ORBIT-X' Hero Endpoint: Combines RAG, Telemetry, Models, SHAP XAI,
    Lineage, and Tool Use to generate a grounded, auditable response with confidence scoring.
    """
    trust_engine = get_trust_layer_engine()
    return trust_engine.ask_orbitx(query=query)


@router.post("/feedback", response_model=HumanFeedbackResponse)
async def submit_operator_feedback(req: HumanFeedbackRequest):
    """
    Human-in-the-Loop Feedback: Logs human operator approval, rejection, or investigation
    to the persistent feedback database for continuous agent and model evaluation.
    """
    trust_engine = get_trust_layer_engine()
    return trust_engine.record_feedback(req)


@router.get("/lineage/provenance/{decision_id}")
async def get_decision_provenance(decision_id: str, mission_id: Optional[str] = None, satellite_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Traces backwards from a Decision ID to discover exact raw telemetry, datasets, features, models,
    anomalies, and constraints that influenced the decision.
    Answers: 'What data influenced this decision?'
    """
    engine = get_context_graph_engine()
    return engine.what_data_influenced_decision(decision_id=decision_id, mission_id=mission_id, satellite_id=satellite_id)


@router.get("/graph/schema")
async def get_relational_graph_schema() -> Dict[str, Any]:
    """
    Returns the PostgreSQL relational table schema representing the context & lineage graph.
    """
    engine = get_context_graph_engine()
    return engine.get_relational_schema()


@router.get("/feedback/history")
async def get_feedback_history() -> List[Dict[str, Any]]:
    """Returns recorded human-in-the-loop review actions."""
    trust_engine = get_trust_layer_engine()
    return trust_engine.get_all_feedback()


@router.get("/feedback/analytics")
async def get_feedback_analytics() -> Dict[str, Any]:
    """
    Returns aggregated human-in-the-loop review metrics:
    approval rate, rejection rate, investigation rate, and decision rationale breakdown.
    """
    trust_engine = get_trust_layer_engine()
    return trust_engine.get_feedback_analytics()


@router.get("/lineage/pipeline")
async def get_seven_stage_lineage_pipeline(
    decision_id: str = "DEC-20260824-M204",
    mission_id: Optional[str] = "M-204",
    satellite_id: Optional[str] = "SAT-17",
) -> Dict[str, Any]:
    """
    Returns the visible and queryable 7-stage end-to-end data lineage pipeline:
    Raw Telemetry -> Cleaning & Validation -> Feature Table -> Anomaly Model -> Prediction -> Decision -> Agent Response.
    """
    engine = get_context_graph_engine()
    return engine.get_seven_stage_pipeline_trace(decision_id=decision_id, mission_id=mission_id, satellite_id=satellite_id)


@router.get("/lineage/column-level")
async def get_column_level_lineage() -> List[Dict[str, Any]]:
    """
    Returns Column-Level Lineage (CLL) tracking raw sensor fields through cleaning,
    feature extraction, ML modeling, and CP-SAT decision constraints.
    """
    engine = get_context_graph_engine()
    return engine.get_column_level_lineage()


@router.get("/lineage/query")
async def query_lineage_get(q: str = "Why was this decision made?") -> Dict[str, Any]:
    """
    Answers natural language queries about data lineage and root-cause provenance:
    e.g. 'Why was this decision made?', 'Trace battery_soc', 'What if telemetry drifts?'
    """
    engine = get_context_graph_engine()
    return engine.query_lineage(query_str=q)


@router.post("/lineage/query")
async def query_lineage_post(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Answers natural language queries about data lineage and root-cause provenance.
    """
    query_str = body.get("query", "Why was this decision made?")
    engine = get_context_graph_engine()
    return engine.query_lineage(query_str=query_str)


@router.get("/lineage/dependencies/{dataset_name}")
async def get_dataset_dependencies(dataset_name: str) -> Dict[str, Any]:
    """
    Returns downstream ML models, feature tables, and pipelines dependent on a dataset.
    """
    engine = get_context_graph_engine()
    return engine.get_dataset_dependencies(dataset_name=dataset_name)

