"""Intersatellite Optical Laser Links (ISL) Mesh Network & Multi-Hop Relay Routing."""

import math
import heapq
from typing import List, Dict, Tuple, Optional, Set
import numpy as np

from app.core.schemas import (
    SatelliteState,
    GroundStation,
    ISLLink,
    ISLRoute,
    ISLMeshState,
    Position3D,
)
from app.physics.access_model import compute_elevation_and_range
from app.physics.orbit_propagator import EARTH_RADIUS_KM

# Speed of light in vacuum (km/s)
SPEED_OF_LIGHT_KM_S = 299792.458
DEFAULT_MAX_ISL_RANGE_KM = 6200.0
ATMOSPHERE_OCCLUSION_ALT_KM = 100.0  # Dense atmosphere limb buffer


def is_line_of_sight_occluded(
    r1: np.ndarray,
    r2: np.ndarray,
    earth_radius_km: float = EARTH_RADIUS_KM,
    atmosphere_km: float = ATMOSPHERE_OCCLUSION_ALT_KM,
) -> bool:
    """
    Evaluates whether the optical ray path between two satellites in ECI coordinates
    is occluded by Earth's oblate spheroid/atmosphere limb.
    
    Ray segment: r(t) = r1 + t * (r2 - r1), for t in [0, 1].
    Finds point of closest approach to Earth's center (0, 0, 0).
    """
    d = r2 - r1
    d_mag_sq = np.dot(d, d)
    if d_mag_sq == 0.0:
        return False
        
    # Parameter t of closest approach on infinite line
    t = -np.dot(r1, d) / d_mag_sq
    # Clamp to line segment between the two satellites
    t_clamped = max(0.0, min(1.0, float(t)))
    
    r_closest = r1 + t_clamped * d
    min_dist_to_center = np.linalg.norm(r_closest)
    
    min_safe_radius = earth_radius_km + atmosphere_km
    return bool(min_dist_to_center < min_safe_radius)


def build_isl_mesh(
    satellites: List[SatelliteState],
    ground_stations: List[GroundStation],
    max_range_km: float = DEFAULT_MAX_ISL_RANGE_KM,
) -> ISLMeshState:
    """
    Computes real-time pairwise intersatellite optical laser cross-links,
    filters Earth-occluded paths, and solves multi-hop shortest paths to ground stations.
    """
    links: List[ISLLink] = []
    active_links: List[ISLLink] = []
    
    sat_positions: Dict[str, np.ndarray] = {
        s.id: np.array([s.position_eci.x, s.position_eci.y, s.position_eci.z], dtype=float)
        for s in satellites
    }
    
    # Graph representation: adj[sat_id] = [(neighbor_id, distance_km, latency_ms)]
    adj: Dict[str, List[Tuple[str, float, float]]] = {s.id: [] for s in satellites}
    
    sat_ids = list(sat_positions.keys())
    num_sats = len(sat_ids)
    max_possible_links = (num_sats * (num_sats - 1)) // 2
    
    for i in range(num_sats):
        id1 = sat_ids[i]
        r1 = sat_positions[id1]
        for j in range(i + 1, num_sats):
            id2 = sat_ids[j]
            r2 = sat_positions[id2]
            
            dist = float(np.linalg.norm(r2 - r1))
            latency_ms = (dist / SPEED_OF_LIGHT_KM_S) * 1000.0
            
            if dist > max_range_km:
                status = "OUT_OF_RANGE"
                is_active = False
            elif is_line_of_sight_occluded(r1, r2):
                status = "OCCLUDED"
                is_active = False
            else:
                status = "ACTIVE"
                is_active = True
                adj[id1].append((id2, dist, latency_ms))
                adj[id2].append((id1, dist, latency_ms))
                
            link_obj = ISLLink(
                sat_1_id=id1,
                sat_2_id=id2,
                distance_km=round(dist, 1),
                latency_ms=round(latency_ms, 2),
                throughput_gbps=10.0,
                status=status,
                is_in_use=False,
            )
            links.append(link_obj)
            if is_active:
                active_links.append(link_obj)
                
    # Identify which satellites currently have direct ground station visibility
    sats_with_gs_contact: Dict[str, str] = {}  # sat_id -> ground_station_id
    best_sat_gs_pair: Tuple[str, str, float] = ("", "", -999.0)  # sat_id, gs_id, elevation
    
    for s in satellites:
        for gs in ground_stations:
            if not gs.is_active:
                continue
            el, _, _ = compute_elevation_and_range(
                sat_ecef=np.array([s.position_ecef.x, s.position_ecef.y, s.position_ecef.z]),
                site_geo=gs.location,
            )
            if el > best_sat_gs_pair[2]:
                best_sat_gs_pair = (s.id, gs.id, el)
            if el >= gs.min_elevation_deg:
                sats_with_gs_contact[s.id] = gs.id
                break
                
    # If no satellite currently has strict elevation >= min_elevation_deg, use highest elevation anchor
    if not sats_with_gs_contact and best_sat_gs_pair[0]:
        sats_with_gs_contact[best_sat_gs_pair[0]] = best_sat_gs_pair[1]
                
    # Dijkstra Shortest-Path Multi-Hop Routing to nearest Ground Station
    routes: List[ISLRoute] = []
    
    for s in satellites:
        # If satellite has direct contact, direct 0-hop route
        if s.id in sats_with_gs_contact:
            gs_id = sats_with_gs_contact[s.id]
            routes.append(
                ISLRoute(
                    source_sat_id=s.id,
                    target_gs_id=gs_id,
                    hops=[s.id, gs_id],
                    total_distance_km=0.0,
                    total_latency_ms=2.5,
                    bottleneck_throughput_gbps=10.0,
                )
            )
            continue
            
        # Find shortest multi-hop path to any satellite with active GS contact
        pq = [(0.0, s.id, [s.id], 0.0)]
        visited: Set[str] = set()
        best_route: Optional[ISLRoute] = None
        
        while pq:
            cost, curr, path, dist_accum = heapq.heappop(pq)
            if curr in visited:
                continue
            visited.add(curr)
            
            if curr in sats_with_gs_contact:
                gs_id = sats_with_gs_contact[curr]
                best_route = ISLRoute(
                    source_sat_id=s.id,
                    target_gs_id=gs_id,
                    hops=path + [gs_id],
                    total_distance_km=round(dist_accum, 1),
                    total_latency_ms=round(cost + 2.5, 2),
                    bottleneck_throughput_gbps=10.0,
                )
                break
                
            for neighbor, n_dist, n_lat in adj.get(curr, []):
                if neighbor not in visited:
                    heapq.heappush(pq, (cost + n_lat, neighbor, path + [neighbor], dist_accum + n_dist))
                    
        if best_route:
            routes.append(best_route)
            # Mark links on the active route as in_use
            for k in range(len(best_route.hops) - 2):
                h1, h2 = best_route.hops[k], best_route.hops[k+1]
                for lk in active_links:
                    if (lk.sat_1_id == h1 and lk.sat_2_id == h2) or (lk.sat_1_id == h2 and lk.sat_2_id == h1):
                        lk.is_in_use = True
                        
    avg_latency = float(np.mean([lk.latency_ms for lk in active_links])) if active_links else 0.0
    
    return ISLMeshState(
        active_links_count=len(active_links),
        max_links_possible=max_possible_links,
        average_latency_ms=round(avg_latency, 2),
        routes=routes,
        links=links,
    )

