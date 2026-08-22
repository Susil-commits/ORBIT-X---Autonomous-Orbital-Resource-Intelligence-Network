"""
ORBIT-X GenAI & Agent Package
=============================
Context-aware Retrieval-Augmented Generation (RAG), Model Context Protocol (MCP) server,
autonomous tool-calling agent loop, and evidence-grounded trust layer.
"""

from backend.app.intelligence.hybrid_mission_rag import (
    HybridMissionRAG,
    RAGDocument,
    RAGQueryResult,
)
from backend.app.intelligence.agent_loop import (
    AutonomousAgent,
    AgentPlan,
    ToolExecutionResult,
)
from backend.app.intelligence.trust_layer import (
    TrustVerificationLayer,
    GroundingVerification,
    EvidenceSource,
)
from backend.app.mcp_server.server import (
    ORBITXMCPAdapter,
    MCPToolDefinition,
)

__all__ = [
    "HybridMissionRAG",
    "RAGDocument",
    "RAGQueryResult",
    "AutonomousAgent",
    "AgentPlan",
    "ToolExecutionResult",
    "TrustVerificationLayer",
    "GroundingVerification",
    "EvidenceSource",
    "ORBITXMCPAdapter",
    "MCPToolDefinition",
]
