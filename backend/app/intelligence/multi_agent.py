"""Multi-Agent Cooperative Auction & Bidding Mechanism."""

from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel, Field

from app.core.schemas import (
    SatelliteState,
    MissionRequest,
    AccessWindow,
    GroundStation,
    HealthStatus,
    WindowType,
)


class AgentBid(BaseModel):
    satellite_id: str
    satellite_name: str
    mission_id: str
    imaging_window: AccessWindow
    bid_value: float
    battery_cost_wh: float
    marginal_soc_remaining: float
    slew_penalty: float
    health_discount: float


class AuctionResult(BaseModel):
    mission_id: str
    winning_satellite_id: Optional[str]
    winning_bid_value: float
    winning_window: Optional[AccessWindow]
    all_bids: List[AgentBid] = []
    conflict_resolved: bool = False
    rationale: str = ""


class MultiAgentCoordinator:
    """
    Simulates cooperative multi-agent bidding across constellation nodes
    to resolve mission and ground station contention.
    """

    @staticmethod
    def calculate_agent_bid(
        satellite: SatelliteState,
        mission: MissionRequest,
        window: AccessWindow,
        existing_assigned_windows: List[AccessWindow],
    ) -> Optional[AgentBid]:
        """Calculates a satellite agent's autonomous bid for a target imaging window."""
        # Hard exclusions
        if satellite.health_status == HealthStatus.CRITICAL_FAULT:
            return None
        if satellite.battery.soc < 0.22:
            return None
        if window.end_time_s > mission.deadline_s:
            return None
            
        # Check temporal overlap with already scheduled tasks on this satellite
        for existing in existing_assigned_windows:
            if max(window.start_time_s, existing.start_time_s) < min(window.end_time_s, existing.end_time_s):
                return None  # Overlap conflict
                
        # Slew / transition penalty if close to another task
        slew_penalty = 0.0
        for existing in existing_assigned_windows:
            gap = abs(window.start_time_s - existing.end_time_s)
            if gap < 60.0:  # Need at least 60s to settle attitude
                slew_penalty += 30.0
                
        # Battery cost calculation
        energy_wh = mission.energy_cost_wh
        proj_soc = max(0.0, satellite.battery.soc - (energy_wh / satellite.battery.capacity_wh))
        if proj_soc < 0.20:
            return None
            
        # Health penalty
        health_discount = 0.0
        if satellite.health_status == HealthStatus.DEGRADED:
            health_discount = 40.0
            
        # Autonomous Valuation Function
        # Satellites with higher battery and higher elevation bid more aggressively
        priority_value = mission.priority * 25.0
        elevation_value = (window.max_elevation_deg / 90.0) * 35.0
        battery_surplus = (satellite.battery.soc - 0.20) * 50.0
        storage_available = (1.0 - (satellite.onboard_storage_used_gb / satellite.max_storage_gb)) * 20.0
        sunlit_bonus = 15.0 if window.is_sunlit else 0.0
        
        bid_value = (
            priority_value
            + elevation_value
            + battery_surplus
            + storage_available
            + sunlit_bonus
            - slew_penalty
            - health_discount
        )
        
        return AgentBid(
            satellite_id=satellite.id,
            satellite_name=satellite.name,
            mission_id=mission.id,
            imaging_window=window,
            bid_value=round(bid_value, 2),
            battery_cost_wh=energy_wh,
            marginal_soc_remaining=round(proj_soc, 3),
            slew_penalty=slew_penalty,
            health_discount=health_discount,
        )

    @classmethod
    def run_auction(
        cls,
        missions: List[MissionRequest],
        satellites: List[SatelliteState],
        candidate_windows_map: Dict[str, Dict[str, List[AccessWindow]]],  # [mission_id][sat_id] -> windows
    ) -> List[AuctionResult]:
        """
        Runs a sealed-bid combinatorial auction across all missions and satellites.
        Resolves conflicts greedily by highest bid.
        """
        results: List[AuctionResult] = []
        assigned_sat_windows: Dict[str, List[AccessWindow]] = {s.id: [] for s in satellites}
        sat_map = {s.id: s for s in satellites}
        
        # Sort missions by priority (descending) and deadline (ascending)
        sorted_missions = sorted(missions, key=lambda m: (-m.priority, m.deadline_s))
        
        for mission in sorted_missions:
            bids_for_mission: List[AgentBid] = []
            m_windows = candidate_windows_map.get(mission.id, {})
            
            for sat in satellites:
                sat_windows = m_windows.get(sat.id, [])
                for win in sat_windows:
                    bid = cls.calculate_agent_bid(
                        satellite=sat,
                        mission=mission,
                        window=win,
                        existing_assigned_windows=assigned_sat_windows[sat.id],
                    )
                    if bid:
                        bids_for_mission.append(bid)
                        
            if bids_for_mission:
                # Select winning bid
                bids_for_mission.sort(key=lambda b: b.bid_value, reverse=True)
                winning_bid = bids_for_mission[0]
                
                # Commit window assignment
                assigned_sat_windows[winning_bid.satellite_id].append(winning_bid.imaging_window)
                
                results.append(
                    AuctionResult(
                        mission_id=mission.id,
                        winning_satellite_id=winning_bid.satellite_id,
                        winning_bid_value=winning_bid.bid_value,
                        winning_window=winning_bid.imaging_window,
                        all_bids=bids_for_mission,
                        conflict_resolved=len(bids_for_mission) > 1,
                        rationale=f"Agent {winning_bid.satellite_name} won auction with bid {winning_bid.bid_value:.1f} (competing against {len(bids_for_mission) - 1} bids).",
                    )
                )
            else:
                results.append(
                    AuctionResult(
                        mission_id=mission.id,
                        winning_satellite_id=None,
                        winning_bid_value=0.0,
                        winning_window=None,
                        all_bids=[],
                        conflict_resolved=False,
                        rationale="No viable agent bids submitted within battery/deadline/visibility constraints.",
                    )
                )
                
        return results
