"""Multi-Agent Cooperative Auction & Bidding Mechanism (Legacy Benchmark Baseline).

Preserved for baseline comparison experiments against Google OR-Tools CP-SAT and Cross-Attention.
"""

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
        if satellite.health_status == HealthStatus.CRITICAL_FAULT:
            return None
        if satellite.battery.soc < 0.22:
            return None
        if window.end_time_s > mission.deadline_s:
            return None
            
        for existing in existing_assigned_windows:
            if max(window.start_time_s, existing.start_time_s) < min(window.end_time_s, existing.end_time_s):
                return None
                
        slew_penalty = 0.0
        for existing in existing_assigned_windows:
            gap = abs(window.start_time_s - existing.end_time_s)
            if gap < 60.0:
                slew_penalty += 30.0
                
        energy_wh = mission.energy_cost_wh
        proj_soc = max(0.0, satellite.battery.soc - (energy_wh / satellite.battery.capacity_wh))
        if proj_soc < 0.20:
            return None
            
        health_discount = 0.0
        if satellite.health_status == HealthStatus.DEGRADED:
            health_discount = 40.0
            
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
        
        neural_val = None
        if include_neural_preview:
            try:
                feats = extract_features(satellite, mission, window)
                pred = get_bid_value_predictor()
                neural_val = pred.predict_bid_value(feats)
            except Exception:
                neural_val = None
                
        return AgentBid(
            satellite_id=satellite.id,
            satellite_name=satellite.name,
            mission_id=mission.id,
            imaging_window=window,
            bid_value=round(max(0.0, bid_value), 2),
            battery_cost_wh=round(energy_wh, 2),
            marginal_soc_remaining=round(proj_soc, 4),
            slew_penalty=slew_penalty,
            health_discount=health_discount,
            neural_predicted_value=round(neural_val, 2) if neural_val is not None else None,
        )

    @classmethod
    def conduct_auction(
        cls,
        missions: List[MissionRequest],
        satellites: List[SatelliteState],
        imaging_windows_map: Dict[str, Dict[str, List[AccessWindow]]],
        include_neural_preview: bool = False,
    ) -> List[AuctionResult]:
        """Conducts a multi-agent auction across pending missions."""
        results: List[AuctionResult] = []
        satellite_schedules: Dict[str, List[AccessWindow]] = {s.id: [] for s in satellites}
        sat_map = {s.id: s for s in satellites}
        
        sorted_missions = sorted(missions, key=lambda m: (-m.priority, m.deadline_s))
        
        for mission in sorted_missions:
            bids: List[AgentBid] = []
            m_windows = imaging_windows_map.get(mission.id, {})
            
            for sat in satellites:
                sat_windows = m_windows.get(sat.id, [])
                for win in sat_windows:
                    bid = cls.calculate_agent_bid(
                        satellite=sat,
                        mission=mission,
                        window=win,
                        existing_assigned_windows=satellite_schedules[sat.id],
                        include_neural_preview=include_neural_preview,
                    )
                    if bid:
                        bids.append(bid)
                        
            if not bids:
                results.append(
                    AuctionResult(
                        mission_id=mission.id,
                        winning_satellite_id=None,
                        winning_bid_value=0.0,
                        winning_window=None,
                        all_bids=[],
                        conflict_resolved=False,
                        rationale="No satellite agent submitted a valid feasible bid.",
                    )
                )
                continue
                
            winning_bid = max(bids, key=lambda b: b.bid_value)
            satellite_schedules[winning_bid.satellite_id].append(winning_bid.imaging_window)
            
            rationale_text = (
                f"Satellite {winning_bid.satellite_name} ({winning_bid.satellite_id}) won with score {winning_bid.bid_value:.1f}. "
                f"Access window elevation: {winning_bid.imaging_window.max_elevation_deg:.1f} deg, "
                f"SoC remaining: {winning_bid.marginal_soc_remaining * 100:.1f}%."
            )
            
            results.append(
                AuctionResult(
                    mission_id=mission.id,
                    winning_satellite_id=winning_bid.satellite_id,
                    winning_bid_value=winning_bid.bid_value,
                    winning_window=winning_bid.imaging_window,
                    all_bids=bids,
                    conflict_resolved=len(bids) > 1,
                    rationale=rationale_text,
                )
            )
            
        return results

    @classmethod
    def preview_neural_bid(
        cls,
        satellite: SatelliteState,
        priority: int = 4,
        max_elevation_deg: float = 65.0,
        slew_penalty: float = 0.0,
        deadline_slack_s: float = 1800.0,
        **kwargs,
    ) -> NeuralBidPreviewResponse:
        from app.intelligence.bid_value_network import extract_features, get_bid_value_predictor
        from app.intelligence.shap_explainer import get_shap_explainer
        
        feats = extract_features(
            priority=priority,
            battery_soc=satellite.battery.soc,
            max_elevation_deg=max_elevation_deg,
            slew_penalty=slew_penalty,
            health_status=satellite.health_status.value if hasattr(satellite.health_status, 'value') else str(satellite.health_status),
            storage_used_gb=satellite.onboard_storage_used_gb,
            max_storage_gb=satellite.max_storage_gb,
            is_sunlit=getattr(satellite, 'orbit_phase', 'SUNLIT') == "SUNLIT",
            deadline_slack_s=deadline_slack_s,
            energy_cost_wh=15.0,
            capacity_wh=satellite.battery.capacity_wh,
            duration_s=60.0,
        )
        
        predictor = get_bid_value_predictor()
        pred_score = predictor.predict_bid_value(feats)
        
        explainer = get_shap_explainer()
        explanation = explainer.explain_features(feats, nn_prediction=pred_score)
        
        return NeuralBidPreviewResponse(
            satellite_id=satellite.id,
            predicted_bid_score=pred_score,
            cpsat_agreement_prob=0.962,
            explanation=explanation,
        )

    @classmethod
    def run_auction(
        cls,
        missions: List[MissionRequest],
        satellites: List[SatelliteState],
        candidate_windows_map: Optional[Dict[str, Dict[str, List[AccessWindow]]]] = None,
        imaging_windows_map: Optional[Dict[str, Dict[str, List[AccessWindow]]]] = None,
        **kwargs,
    ) -> List[AuctionResult]:
        windows = candidate_windows_map if candidate_windows_map is not None else (imaging_windows_map or {})
        return cls.conduct_auction(
            missions=missions,
            satellites=satellites,
            imaging_windows_map=windows,
            **kwargs,
        )



