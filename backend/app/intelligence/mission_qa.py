"""Grounded Decision History RAG & Mission QA Engine for ORBIT-X.

Embeds logged mission assignments, solver rationale, telemetry anomaly alerts,
and collision maneuvers via sentence-transformers (all-MiniLM-L6-v2).
Provides grounded factual answers with verifiable citations and strictly refuses
to answer on queries lacking supporting logged evidence.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.schemas import (
    MissionQARequest,
    MissionQAResponse,
    Citation,
)
from app.intelligence.decision_logger import (
    DecisionLogger,
    LoggedDecisionEvent,
    get_decision_logger,
)

RELEVANCE_THRESHOLD = 0.25


class MissionQAEngine:
    """RAG engine over ORBIT-X operational logs with citation attribution and honest refusal."""

    def __init__(self, logger: Optional[DecisionLogger] = None):
        self.logger = logger or get_decision_logger()
        self.model_name = settings.EMBEDDING_MODEL
        print(f"Loading embedding model '{self.model_name}' for Mission RAG...")
        self.embedder = SentenceTransformer(self.model_name)
        self.cached_embeddings: Optional[np.ndarray] = None
        self.cached_event_count: int = 0

    def _get_event_embeddings(self, events: List[LoggedDecisionEvent]) -> np.ndarray:
        """Computes and caches dense vectors for logged event summaries."""
        if self.cached_embeddings is not None and len(events) == self.cached_event_count:
            return self.cached_embeddings
            
        texts = [
            f"Event {e.event_type} at Tick {e.tick} (T+{e.sim_time_s:.0f}s): {e.summary}"
            for e in events
        ]
        embeddings = self.embedder.encode(texts, normalize_embeddings=True)
        self.cached_embeddings = np.array(embeddings, dtype=np.float32)
        self.cached_event_count = len(events)
        return self.cached_embeddings

    def ask(self, query: str, top_k: int = 4) -> MissionQAResponse:
        """
        Retrieves relevant logged records and synthesizes a grounded answer.
        Refuses to answer if no records meet relevance threshold.
        """
        events = self.logger.get_all_events()
        if not events:
            return MissionQAResponse(
                query=query,
                answer="No mission decision records have been logged in constellation history yet.",
                grounded=False,
                confidence_score=0.0,
                citations=[],
                retrieved_records_count=0,
            )
            
        # 1. Embed query and events
        event_embeddings = self._get_event_embeddings(events)
        query_emb = self.embedder.encode([query], normalize_embeddings=True)[0]
        
        # 2. Compute cosine similarities
        similarities = np.dot(event_embeddings, query_emb)
        
        # 3. Rank top-k candidates
        ranked_indices = np.argsort(similarities)[::-1]
        
        citations: List[Citation] = []
        top_events: List[Tuple[LoggedDecisionEvent, float]] = []
        
        for idx in ranked_indices[:top_k]:
            sim = float(similarities[idx])
            ev = events[idx]
            if sim >= RELEVANCE_THRESHOLD:
                top_events.append((ev, sim))
                citations.append(
                    Citation(
                        record_id=ev.record_id,
                        tick=ev.tick,
                        sim_time_s=ev.sim_time_s,
                        event_type=ev.event_type,
                        summary=ev.summary,
                        relevance_score=round(sim, 3),
                    )
                )
                
        # 4. Honest refusal check
        if not citations:
            return MissionQAResponse(
                query=query,
                answer=(
                    f"Refusal: No relevant constellation operational records found matching '{query}'. "
                    f"The decision history does not contain verified telemetry or assignment data for this query."
                ),
                grounded=False,
                confidence_score=round(float(similarities[ranked_indices[0]]), 3),
                citations=[],
                retrieved_records_count=0,
            )
            
        # 5. Synthesize grounded answer
        answer_parts = []
        for ev, score in top_events:
            sat_str = f" for {ev.satellite_id}" if ev.satellite_id else ""
            answer_parts.append(
                f"- [Record {ev.record_id} | Tick {ev.tick} | T+{ev.sim_time_s:.0f}s | {ev.event_type}{sat_str}]: "
                f"{ev.summary}"
            )
            
        synthesized_text = (
            f"Based on {len(top_events)} verified decision log records in ORBIT-X history:\n\n"
            + "\n\n".join(answer_parts)
        )
        
        avg_confidence = round(float(np.mean([s for _, s in top_events])), 3)
        
        return MissionQAResponse(
            query=query,
            answer=synthesized_text,
            grounded=True,
            confidence_score=avg_confidence,
            citations=citations,
            retrieved_records_count=len(citations),
        )


_global_qa_engine: Optional[MissionQAEngine] = None


def get_mission_qa_engine() -> MissionQAEngine:
    global _global_qa_engine
    if _global_qa_engine is None:
        _global_qa_engine = MissionQAEngine()
    return _global_qa_engine


if __name__ == "__main__":
    qa = get_mission_qa_engine()
    
    # Test valid grounded query
    q1 = "Why was satellite 7 degraded or what happened to its payload?"
    print(f"\nQuery 1: {q1}")
    res1 = qa.ask(q1)
    print(f"Grounded: {res1.grounded}, Score: {res1.confidence_score}")
    print(res1.answer)
    
    # Test ungrounded refusal query
    q2 = "What is the stock price of Apple Inc in 2024?"
    print(f"\nQuery 2: {q2}")
    res2 = qa.ask(q2)
    print(f"Grounded: {res2.grounded}, Score: {res2.confidence_score}")
    print(res2.answer)
