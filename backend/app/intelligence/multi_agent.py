"""Multi-Agent Cooperative Auction & Bidding Mechanism with Neural Bid Valuation Preview."""

from typing import List, Dict, Tuple, Optional
import numpy as np
from pydantic import BaseModel, Field

from app.core.schemas import (
    SatelliteState,
    MissionRequest,
    AccessWindow,
    GroundStation,
    HealthStatus,
    WindowType,
    NeuralBidPreviewResponse,
    BidValuationExplanation,
)
from app.intelligence.bid_value_network import extract_features, get_bid_value_predictor
from app.intelligence.shap_explainer import get_shap_explainer


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
    neural_predicted_value: Optional[float] = None


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
    Provides fast neural network approximation previews alongside authoritative bidding.
    """

    @staticmethod
    def calculate_agent_bid(
        satellite: SatelliteState,
        mission: MissionRequest,
        window: AccessWindow,
        existing_assigned_windows: List[AccessWindow],
        include_neural_preview: bool = False,
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
                return None
                
        # Slew / transition penalty if close to another task
        slew_penalty = 0.0
        for existing in existing_assigned_windows:
            gap = abs(window.start_time_s - existing.end_time_s)
            if gap < 60.0:
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
        
        nn_val = None
        if include_neural_preview:
            try:
                predictor = get_bid_value_predictor()
                feats = extract_features(
                    priority=mission.priority,
                    battery_soc=satellite.battery.soc,
                    max_elevation_deg=window.max_elevation_deg,
                    slew_penalty=slew_penalty,
                    health_status=satellite.health_status.value,
                    storage_used_gb=satellite.onboard_storage_used_gb,
                    max_storage_gb=satellite.max_storage_gb,
                    is_sunlit=window.is_sunlit,
                    deadline_slack_s=max(0.0, mission.deadline_s - window.start_time_s),
                    energy_cost_wh=mission.energy_cost_wh,
                    capacity_wh=satellite.battery.capacity_wh,
                    duration_s=mission.duration_s,
                )
                nn_val = round(predictor.predict_single(feats), 2)
            except Exception:
                pass
        
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
            neural_predicted_value=nn_val,
        )

    @classmethod
    def preview_neural_bid(
        cls,
        satellite: SatelliteState,
        priority: int,
        max_elevation_deg: float,
        slew_penalty: float = 0.0,
        deadline_slack_s: float = 1800.0,
        duration_s: float = 30.0,
        energy_cost_wh: float = 15.0,
    ) -> NeuralBidPreviewResponse:
        """
        Sub-millisecond fast neural preview of a satellite's bid with TreeSHAP explainability.
        """
        feats = extract_features(
            priority=priority,
            battery_soc=satellite.battery.soc,
            max_elevation_deg=max_elevation_deg,
            slew_penalty=slew_penalty,
            health_status=satellite.health_status.value,
            storage_used_gb=satellite.onboard_storage_used_gb,
            max_storage_gb=satellite.max_storage_gb,
            is_sunlit=satellite.battery.is_sunlit,
            deadline_slack_s=deadline_slack_s,
            energy_cost_wh=energy_cost_wh,
            capacity_wh=satellite.battery.capacity_wh,
            duration_s=duration_s,
        )
        
        predictor = get_bid_value_predictor()
        pred_val = predictor.predict_single(feats)
        
        explainer = get_shap_explainer()
        explanation = explainer.explain_features(feats)
        
        # Agreement probability heuristic based on test agreement rate
        agreement_prob = 0.72 if satellite.health_status == HealthStatus.NOMINAL else 0.58
        
        return NeuralBidPreviewResponse(
            satellite_id=satellite.id,
            predicted_bid_score=round(pred_val, 2),
            cpsat_agreement_prob=agreement_prob,
            explanation=explanation,
        )

    @classmethod
    def run_auction(
        cls,
        missions: List[MissionRequest],
        satellites: List[SatelliteState],
        candidate_windows_map: Dict[str, Dict[str, List[AccessWindow]]],
    ) -> List[AuctionResult]:
        """
        Runs a sealed-bid combinatorial auction across all missions and satellites.
        Resolves conflicts greedily by highest bid.
        """
        results: List[AuctionResult] = []
        assigned_sat_windows: Dict[str, List[AccessWindow]] = {s.id: [] for s in satellites}
        
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
                        include_neural_preview=True,
                    )
                    if bid:
                        bids_for_mission.append(bid)
                        
            if bids_for_mission:
                bids_for_mission.sort(key=lambda b: b.bid_value, reverse=True)
                winning_bid = bids_for_mission[0]
                
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
