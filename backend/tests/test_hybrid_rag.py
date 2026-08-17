"""Tests for Hybrid Dense + BM25 RAG & Mission QA Engine."""

import pytest
from app.intelligence.hybrid_mission_rag import (
    BM25Retriever,
    HybridMissionQAEngine,
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


def test_hybrid_qa_engine():
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


def test_hybrid_qa_refusal():
    logger = DecisionLogger()
    qa = HybridMissionQAEngine(logger=logger)
    res = qa.ask("What is the current stock price of Apple Inc?")
    assert res.grounded is False
    assert len(res.citations) == 0
