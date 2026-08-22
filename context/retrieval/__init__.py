"""Context retrieval engine combining dense vector search, BM25, and structured metadata."""

from typing import Dict, Any, List
from backend.app.intelligence.hybrid_mission_rag import HybridMissionQAEngine, get_hybrid_qa_engine

# Compatibility alias
ContextRetriever = HybridMissionQAEngine
get_context_retriever = get_hybrid_qa_engine

__all__ = [
    "HybridMissionQAEngine",
    "get_hybrid_qa_engine",
    "ContextRetriever",
    "get_context_retriever",
]
