"""Agent Query Interface and Mission Intent Parsing."""

from backend.app.intelligence.mission_qa import MissionQAEngine, get_mission_qa_engine

# Compatibility alias
AgentQueryEngine = MissionQAEngine
get_agent_query_engine = get_mission_qa_engine

__all__ = [
    "MissionQAEngine",
    "get_mission_qa_engine",
    "AgentQueryEngine",
    "get_agent_query_engine",
]
