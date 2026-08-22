"""Simulation Intersatellite Optical Laser Link Mesh Network.

Provides laser link visibility modeling, line-of-sight Earth occlusion checking,
and Dijkstra shortest-path relay routing across the constellation.
"""

from backend.app.physics.isl_network import (
    is_line_of_sight_occluded,
    build_isl_mesh,
)
from backend.app.core.schemas import (
    ISLLink,
    ISLRoute,
    ISLMeshState,
)

# Compatibility alias
ISLMeshNetwork = build_isl_mesh
MeshRoute = ISLRoute

__all__ = [
    "is_line_of_sight_occluded",
    "build_isl_mesh",
    "ISLMeshNetwork",
    "ISLLink",
    "ISLRoute",
    "MeshRoute",
    "ISLMeshState",
]
