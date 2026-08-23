"""ORBIT-X Autonomous Agents & MCP Layer Package.

Provides intent understanding, multi-step planning, tool selection,
and execution across machine learning, anomaly detection, CP-SAT optimization, and data lineage.
"""

from agents.agent_loop.orchestrator import AgentOrchestrator
from agents.tools.mcp_tools import AIToolsRegistry, get_ai_tools_registry

# Backward-compatible re-exports
from backend.app.intelligence.agent_loop import (
    SelfHealingAgent,
    get_self_healing_agent,
)
from backend.app.intelligence.hybrid_mission_rag import MissionQAEngine, get_mission_qa_engine

# Compatibility aliases
AgentLoop = SelfHealingAgent
SelfHealingAgentLoop = SelfHealingAgent

__all__ = [
    "AgentOrchestrator",
    "AIToolsRegistry",
    "get_ai_tools_registry",
    "SelfHealingAgent",
    "get_self_healing_agent",
    "AgentLoop",
    "SelfHealingAgentLoop",
    "MissionQAEngine",
    "get_mission_qa_engine",
]
