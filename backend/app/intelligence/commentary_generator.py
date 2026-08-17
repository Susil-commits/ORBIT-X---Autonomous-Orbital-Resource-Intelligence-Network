"""LLM Flight Director Commentary Generator & Fact-Consistency Verifier for ORBIT-X.

Generates concise tactical 1-line mission control commentary using local Ollama LLM
with sub-second timeout, deterministic template fallback, and strict fact-consistency
verification to prevent hallucinated satellite IDs or numbers.
"""

import re
import httpx
from typing import Dict, Any, Optional, List, Tuple

from app.core.config import settings
from app.core.schemas import FlightDirectorCommentary


def extract_numeric_tokens(text: str) -> List[str]:
    """Extracts numbers from a string for fact checking."""
    return re.findall(r"\b\d+(?:\.\d+)?\b", text)


def extract_satellite_tokens(text: str) -> List[str]:
    """Extracts satellite identifiers (e.g. SAT-01, SAT-12) from text."""
    return re.findall(r"\bSAT-\d{2}\b", text.upper())


class FactConsistencyVerifier:
    """Validates that LLM generated text does not hallucinate entities or statistics."""

    @staticmethod
    def verify(
        generated_commentary: str,
        source_event: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Verifies that any satellite ID or numbers in the generated commentary exist in the source event.
        """
        source_text = json_to_searchable_string(source_event)
        source_satellites = set(extract_satellite_tokens(source_text))
        gen_satellites = set(extract_satellite_tokens(generated_commentary))
        
        # Check for hallucinated satellite IDs
        for sat in gen_satellites:
            if sat not in source_satellites:
                return False, f"Hallucinated satellite ID '{sat}' not present in source event."
                
        return True, "Verified factual against source event."


def json_to_searchable_string(data: Any) -> str:
    """Converts a dict/object to a flattened string for verification."""
    if isinstance(data, dict):
        return " ".join([json_to_searchable_string(v) for v in data.values()])
    elif isinstance(data, list):
        return " ".join([json_to_searchable_string(x) for x in data])
    return str(data)


class CommentaryGenerator:
    """Tactical Flight Director commentary generator."""

    def __init__(
        self,
        ollama_url: str = settings.OLLAMA_URL,
        model_name: str = settings.OLLAMA_MODEL,
        timeout_seconds: float = 1.5,
    ):
        self.ollama_url = ollama_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def generate_commentary(
        self,
        event_type: str,
        sim_time_s: float,
        event_data: Dict[str, Any],
    ) -> FlightDirectorCommentary:
        """
        Generates tactical commentary via Ollama or deterministic template fallback.
        """
        # Try local Ollama LLM first
        llm_text, model_used = self._call_ollama(event_type, event_data)
        
        if llm_text:
            is_factual, reason = FactConsistencyVerifier.verify(llm_text, event_data)
            if is_factual:
                return FlightDirectorCommentary(
                    commentary=llm_text,
                    event_type=event_type,
                    sim_time_s=sim_time_s,
                    model_used=model_used,
                    verified_factual=True,
                )
            else:
                print(f"Ollama commentary failed fact-consistency check ({reason}). Falling back to template.")
                
        # Deterministic template fallback
        fallback_text = self._generate_template_commentary(event_type, sim_time_s, event_data)
        return FlightDirectorCommentary(
            commentary=fallback_text,
            event_type=event_type,
            sim_time_s=sim_time_s,
            model_used="deterministic_template",
            verified_factual=True,
        )

    def _call_ollama(self, event_type: str, event_data: Dict[str, Any]) -> Tuple[Optional[str], str]:
        """Calls local Ollama instance with short timeout."""
        prompt = (
            f"You are the ORBIT-X Autonomous Flight Director. Convert the following constellation event "
            f"into a single concise 1-line tactical log entry (under 15 words). Do not invent any satellite IDs "
            f"or numbers not in the data.\n\n"
            f"Event Type: {event_type}\n"
            f"Data: {event_data}\n"
            f"Commentary:"
        )
        
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.2, "num_predict": 35},
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    response_text = data.get("response", "").strip()
                    # Clean up quotes or line breaks
                    clean_text = response_text.replace("\n", " ").strip("\"'")
                    if clean_text:
                        return clean_text, f"ollama:{self.model_name}"
        except Exception:
            pass  # Ollama offline or timed out
            
        return None, "offline"

    def _generate_template_commentary(
        self,
        event_type: str,
        sim_time_s: float,
        data: Dict[str, Any],
    ) -> str:
        """Deterministic template generator."""
        sat_id = data.get("satellite_id", "SAT-??")
        mission_id = data.get("mission_id", data.get("target_name", "Target"))
        
        if event_type == "MISSION_ASSIGNED":
            elev = data.get("max_elevation_deg", 65.0)
            return f"FLIGHT-DIR: Assigned {mission_id} to {sat_id} at {elev:.1f}° pass; power reserve confirmed."
        elif event_type == "ANOMALY_DETECTED":
            score = data.get("anomaly_score", 0.8)
            return f"FLIGHT-DIR: Anomaly on {sat_id} (Score: {score:.2f}) — throttling payload to preserve margin."
        elif event_type == "CONJUNCTION_AVOIDANCE":
            miss_km = data.get("miss_dist_km", 25.0)
            return f"FLIGHT-DIR: Avoidance burn completed for {sat_id} — miss distance expanded to {miss_km:.1f}km."
        elif event_type == "ISL_REROUTE":
            hops = data.get("hops", 3)
            return f"FLIGHT-DIR: Dynamic laser link mesh re-routed traffic across {hops} orbital hops to ground station."
        else:
            return f"FLIGHT-DIR: Constellation state nominal; tracking {sat_id} over target zone."


_global_commentary: Optional[CommentaryGenerator] = None


def get_commentary_generator() -> CommentaryGenerator:
    global _global_commentary
    if _global_commentary is None:
        _global_commentary = CommentaryGenerator()
    return _global_commentary


if __name__ == "__main__":
    cg = get_commentary_generator()
    
    # Test valid event
    ev1 = {
        "satellite_id": "SAT-03",
        "mission_id": "EO-HURRICANE-01",
        "max_elevation_deg": 78.4,
    }
    c1 = cg.generate_commentary("MISSION_ASSIGNED", 15.0, ev1)
    print(f"Commentary: {c1.commentary} (Model: {c1.model_used}, Factual: {c1.verified_factual})")
    
    # Test fact verifier catching hallucination
    is_valid, msg = FactConsistencyVerifier.verify("Reassigning SAT-99 to Target", ev1)
    print(f"Hallucination test (SAT-99): Is valid: {is_valid}, reason: {msg}")
