"""Tests for Hybrid Dense (FAISS) + BM25 RAG & Mission QA Engine."""

import os
import tempfile
from pathlib import Path
import pytest

from app.intelligence.hybrid_mission_rag import (
    BM25Retriever,
    HybridMissionQAEngine,
    MissionRAGRetriever,
    get_hybrid_mission_qa_engine,
)
from app.intelligence.decision_logger import DecisionLogger


def test_bm25_retriever():
    bm25 = BM25Retriever()
    docs = [
        "Satellite SAT-01 completed high-priority optical imaging over Tokyo with 98% battery.",
        "Debris collision alert triggered for SAT-04 at altitude 550km miss distance 12km.",
        "Solar storm geomagnetic disturbance detected affecting solar panel array power on SAT-02.",
    ]
    bm25.fit(docs)

    scores = bm25.score("collision SAT-04 debris")
    assert len(scores) == 3
    assert scores[1] > scores[0]
    assert scores[1] > scores[2]


def test_hybrid_qa_engine_with_faiss():
    logger = DecisionLogger()
    logger.log_event(
        event_type="MISSION_ASSIGNMENT",
        tick=10,
        sim_time_s=100.0,
        summary="SAT-01 assigned to Emergency Target Alpha with elevation 72 deg.",
        satellite_id="SAT-01",
        mission_id="M-ALPHA",
        severity="INFO",
    )
    logger.log_event(
        event_type="ANOMALY_RESOLVED",
        tick=12,
        sim_time_s=120.0,
        summary="Thermal anomaly on battery pack 2 cleared autonomously by load shedding.",
        satellite_id="SAT-01",
        severity="WARN",
    )

    qa = HybridMissionQAEngine(logger=logger)
    res = qa.ask("Why was SAT-01 assigned to Target Alpha?", top_k=2)

    assert res.grounded is True
    assert len(res.citations) > 0
    assert "SAT-01" in res.answer
    assert qa.faiss_index is not None
    assert qa.faiss_index.ntotal >= 2


def test_faiss_index_disk_persistence():
    """Tests saving and reloading FAISS dense index from disk."""
    with tempfile.TemporaryDirectory() as tmpdir:
        index_file = Path(tmpdir) / "test_faiss.bin"
        meta_file = Path(tmpdir) / "test_faiss_meta.json"

        logger = DecisionLogger()
        logger.log_event(
            event_type="COLLISION_AVOIDANCE",
            tick=50,
            sim_time_s=500.0,
            summary="SAT-04 executed 12m/s delta-V burn for debris avoidance.",
            satellite_id="SAT-04",
            severity="HIGH",
        )

        qa1 = HybridMissionQAEngine(logger=logger, index_path=index_file, meta_path=meta_file)
        res1 = qa1.ask("debris burn maneuver SAT-04")
        assert res1.grounded is True
        assert index_file.exists()
        assert meta_file.exists()

        # Reload in a new instance
        qa2 = HybridMissionQAEngine(logger=logger, index_path=index_file, meta_path=meta_file)
        assert qa2.faiss_index is not None
        assert qa2.cached_event_count == len(logger.get_all_events())
        res2 = qa2.ask("debris burn maneuver SAT-04")
        assert res2.grounded is True
        assert len(res2.citations) >= 1


def test_langchain_base_retriever_interface():
    """Validates LangChain BaseRetriever compliance and Document generation."""
    logger = DecisionLogger()
    logger.log_event(
        event_type="SOLAR_FLARE_MITIGATION",
        tick=80,
        sim_time_s=800.0,
        summary="SAT-02 entered safe hold due to X-class solar flare detection.",
        satellite_id="SAT-02",
        severity="CRITICAL",
    )

    qa = HybridMissionQAEngine(logger=logger)
    retriever = qa.as_langchain_retriever(top_k=2)
    assert isinstance(retriever, MissionRAGRetriever)

    # Invoke standard LangChain retriever interface
    docs = retriever.invoke("solar flare safe hold SAT-02")
    assert len(docs) >= 1
    doc = docs[0]
    assert "SAT-02" in doc.page_content
    assert doc.metadata["event_type"] == "SOLAR_FLARE_MITIGATION"
    assert doc.metadata["grounded"] is True
    assert doc.metadata["relevance_score"] > 0.0


def test_hybrid_qa_refusal():
    logger = DecisionLogger()
    qa = HybridMissionQAEngine(logger=logger)
    res = qa.ask("What is the current stock price of Apple Inc?")
    assert res.grounded is False
    assert len(res.citations) == 0
