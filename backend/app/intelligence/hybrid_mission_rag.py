"""Hybrid Dense + Sparse (BM25) RAG & Mission Decision History Engine for ORBIT-X.

Combines dense vector embeddings from SentenceTransformers with BM25 lexical token matching
using Reciprocal Rank Fusion (RRF) for precise retrieval across operational constellation logs,
conjunction avoidance records, and anomaly diagnostics with verifiable citations.
"""

import re
import math
from collections import Counter
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

from app.core.config import settings
from app.core.schemas import (
    Citation,
    MissionQAResponse,
    HybridMissionQARequest,
)
from app.intelligence.decision_logger import (
    DecisionLogger,
    LoggedDecisionEvent,
    get_decision_logger,
)


class BM25Retriever:
    """Lightweight in-memory BM25 lexical ranker for operational log records."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.doc_lens: List[int] = []
        self.doc_term_freqs: List[Counter] = []

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z0-9_\-\.]+\b", text.lower())

    def fit(self, documents: List[str]):
        """Indexes documents for BM25 retrieval."""
        self.corpus_size = len(documents)
        self.doc_term_freqs = []
        self.doc_lens = []
        self.doc_freqs = {}

        if self.corpus_size == 0:
            self.avg_doc_len = 0.0
            return

        total_len = 0
        for doc in documents:
            tokens = self._tokenize(doc)
            tf = Counter(tokens)
            self.doc_term_freqs.append(tf)
            doc_l = len(tokens)
            self.doc_lens.append(doc_l)
            total_len += doc_l

            for token in tf.keys():
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1

        self.avg_doc_len = total_len / max(1, self.corpus_size)

    def score(self, query: str) -> np.ndarray:
        """Computes BM25 score array for query across indexed documents."""
        if self.corpus_size == 0:
            return np.zeros(0, dtype=np.float32)

        q_tokens = self._tokenize(query)
        scores = np.zeros(self.corpus_size, dtype=np.float32)

        for token in q_tokens:
            if token not in self.doc_freqs:
                continue

            df = self.doc_freqs[token]
            idf = math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))

            for doc_idx, tf_map in enumerate(self.doc_term_freqs):
                tf = tf_map.get(token, 0)
                if tf == 0:
                    continue
                doc_len = self.doc_lens[doc_idx]
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1e-5, self.avg_doc_len)))
                scores[doc_idx] += idf * (numerator / denominator)

        # Normalize to [0, 1] range
        max_s = np.max(scores) if np.max(scores) > 0 else 1.0
        return scores / max_s


class HybridMissionQAEngine:
    """
    Hybrid Dense + BM25 RAG engine with Reciprocal Rank Fusion (RRF) and verifiable citation attribution.
    """

    def __init__(self, logger: Optional[DecisionLogger] = None):
        self.logger = logger or get_decision_logger()
        self.model_name = settings.EMBEDDING_MODEL
        print(f"Initializing HybridMissionQAEngine with dense embedder '{self.model_name}' and BM25...", flush=True)
        self.embedder = SentenceTransformer(self.model_name) if SentenceTransformer is not None else None
        self.bm25 = BM25Retriever()
        self.cached_embeddings: Optional[np.ndarray] = None
        self.cached_event_count: int = 0
        self.cached_event_ids: List[str] = []

    def _sync_index(self, events: List[LoggedDecisionEvent]) -> np.ndarray:
        """Syncs dense embeddings and BM25 inverted index with latest logged events."""
        event_ids = [e.record_id for e in events]
        if self.cached_embeddings is not None and event_ids == self.cached_event_ids:
            return self.cached_embeddings

        texts = [
            f"Record {e.record_id} | Tick {e.tick} (T+{e.sim_time_s:.0f}s) | Event {e.event_type} | "
            f"Satellite: {e.satellite_id or 'N/A'} | Mission: {e.mission_id or 'N/A'} | "
            f"Severity: {e.details.get('severity', 'INFO')} | {e.summary}"
            for e in events
        ]

        # 1. Dense Embeddings
        if self.embedder is not None:
            dense_embs = self.embedder.encode(texts, normalize_embeddings=True)
            self.cached_embeddings = np.array(dense_embs, dtype=np.float32)
        else:
            self.cached_embeddings = np.zeros((len(texts), 384), dtype=np.float32)

        # 2. BM25 Inverted Index
        self.bm25.fit(texts)

        self.cached_event_count = len(events)
        self.cached_event_ids = event_ids
        return self.cached_embeddings

    def ask(
        self,
        query: str,
        top_k: int = 5,
        satellite_filter: Optional[str] = None,
        min_severity: Optional[str] = None,
        dense_weight: float = 0.6,
        bm25_weight: float = 0.4,
    ) -> MissionQAResponse:
        """
        Executes hybrid dense + BM25 search with Reciprocal Rank Fusion and factual synthesis.
        """
        all_events = self.logger.get_all_events()
        if not all_events:
            return MissionQAResponse(
                query=query,
                answer="No constellation operational decision records have been logged in memory yet.",
                grounded=False,
                confidence_score=0.0,
                citations=[],
                retrieved_records_count=0,
            )

        # Apply metadata filters
        candidate_indices = []
        for idx, ev in enumerate(all_events):
            ev_sev = ev.details.get("severity", "INFO")
            if satellite_filter and satellite_filter != "ALL" and ev.satellite_id != satellite_filter:
                continue
            if min_severity and min_severity != "ALL" and ev_sev != min_severity:
                continue
            candidate_indices.append(idx)

        if not candidate_indices:
            return MissionQAResponse(
                query=query,
                answer=f"No decision records matched the criteria (Satellite: {satellite_filter}, Severity: {min_severity}).",
                grounded=False,
                confidence_score=0.0,
                citations=[],
                retrieved_records_count=0,
            )

        # Sync dense + BM25 indices
        event_embeddings = self._sync_index(all_events)

        # 1. Dense Scores
        if self.embedder is not None:
            query_emb = self.embedder.encode([query], normalize_embeddings=True)[0]
            dense_scores = np.dot(event_embeddings, query_emb)
        else:
            dense_scores = np.zeros(len(all_events), dtype=np.float32)

        # 2. BM25 Scores
        bm25_scores = self.bm25.score(query)

        # 3. Reciprocal Rank Fusion (RRF)
        # RRF formula: RRF_score(d) = sum(w_i / (k + rank_i(d)))
        rrf_k = 60.0
        dense_ranks = {orig_idx: rank for rank, orig_idx in enumerate(np.argsort(dense_scores)[::-1])}
        bm25_ranks = {orig_idx: rank for rank, orig_idx in enumerate(np.argsort(bm25_scores)[::-1])}

        candidate_rrf_scores = []
        for c_idx in candidate_indices:
            r_dense = dense_ranks[c_idx]
            r_bm25 = bm25_ranks[c_idx]
            rrf_val = (dense_weight / (rrf_k + r_dense)) + (bm25_weight / (rrf_k + r_bm25))
            candidate_rrf_scores.append((c_idx, rrf_val, dense_scores[c_idx], bm25_scores[c_idx]))

        candidate_rrf_scores.sort(key=lambda x: x[1], reverse=True)

        top_candidates = candidate_rrf_scores[:top_k]

        citations: List[Citation] = []
        top_events: List[Tuple[LoggedDecisionEvent, float]] = []

        for c_idx, rrf_score, d_score, b_score in top_candidates:
            ev = all_events[c_idx]
            # Relevance check: either dense or BM25 must have meaningful signal
            if d_score >= 0.22 or b_score >= 0.15:
                top_events.append((ev, float(d_score)))
                citations.append(
                    Citation(
                        record_id=ev.record_id,
                        tick=ev.tick,
                        sim_time_s=ev.sim_time_s,
                        event_type=ev.event_type,
                        summary=ev.summary,
                        relevance_score=round(float(d_score), 3),
                    )
                )

        if not citations:
            return MissionQAResponse(
                query=query,
                answer=(
                    f"Refusal: No verified operational decision records in constellation history match query '{query}' "
                    f"with sufficient factual relevance."
                ),
                grounded=False,
                confidence_score=round(float(dense_scores[np.argmax(dense_scores)]), 3),
                citations=[],
                retrieved_records_count=0,
            )

        # Synthesize grounded answer
        answer_lines = []
        for ev, score in top_events:
            sat_label = f" | {ev.satellite_id}" if ev.satellite_id else ""
            answer_lines.append(
                f"- [Record {ev.record_id} | Tick {ev.tick} | T+{ev.sim_time_s:.0f}s | {ev.event_type}{sat_label}]: "
                f"{ev.summary}"
            )

        synthesized_text = (
            f"Based on {len(top_events)} verified operational decision records via Hybrid Dense+BM25 RAG:\n\n"
            + "\n\n".join(answer_lines)
        )

        avg_conf = round(float(np.mean([s for _, s in top_events])), 3)

        return MissionQAResponse(
            query=query,
            answer=synthesized_text,
            grounded=True,
            confidence_score=avg_conf,
            citations=citations,
            retrieved_records_count=len(citations),
        )


# Global singleton
_GLOBAL_HYBRID_QA_ENGINE: Optional[HybridMissionQAEngine] = None


def get_hybrid_mission_qa_engine() -> HybridMissionQAEngine:
    global _GLOBAL_HYBRID_QA_ENGINE
    if _GLOBAL_HYBRID_QA_ENGINE is None:
        _GLOBAL_HYBRID_QA_ENGINE = HybridMissionQAEngine()
    return _GLOBAL_HYBRID_QA_ENGINE


# Backward-compatible aliases
get_mission_qa_engine = get_hybrid_mission_qa_engine
MissionQAEngine = HybridMissionQAEngine

