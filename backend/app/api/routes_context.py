"""FastAPI Router for Semantic Metadata Catalog, Data Lineage, Quality Agent, Ask ORBIT-X & Human Feedback."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any

from app.core.schemas import (
    DataCatalogResponse,
    DataCatalogEntry,
    DataLineageResponse,
    DataQualityReport,
    TrustLayerResponse,
    HumanFeedbackRequest,
    HumanFeedbackResponse,
)
from app.simulation.simulator import get_simulator
from app.intelligence.context_graph import get_context_graph_engine
from app.intelligence.data_quality_agent import get_data_quality_agent
from app.intelligence.trust_layer import get_trust_layer_engine

router = APIRouter(prefix="/api/context", tags=["Context Layer, Lineage & Semantic Metadata"])


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
