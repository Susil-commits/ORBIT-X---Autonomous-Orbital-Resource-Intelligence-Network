"""Unit tests for Grounded Decision History RAG & Mission QA with citations."""

import pytest
from app.intelligence.mission_qa import get_mission_qa_engine
from app.intelligence.decision_logger import get_decision_logger


def test_rag_grounded_answer():
    """Validates grounded retrieval with citation on a relevant query."""
    qa = get_mission_qa_engine()
    res = qa.ask("Why was satellite 3 assigned to Hurricane Alpha?")
    
    assert res.grounded is True
    assert res.confidence_score >= 0.25
    assert len(res.citations) >= 1
    assert any("SAT-03" in c.summary or "HURRICANE" in c.summary for c in res.citations)


def test_rag_honest_refusal():
    """Validates honest refusal on out-of-domain query."""
    qa = get_mission_qa_engine()
    res = qa.ask("What is the recipe for chocolate chip cookies?")
    
    assert res.grounded is False
    assert "Refusal" in res.answer
    assert len(res.citations) == 0
