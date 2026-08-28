import React, { useState } from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import {
  X,
  Users,
  RefreshCw,
  Award,
  ShieldCheck,
  Flame,
  Network,
  Activity,
  GitBranch,
  CheckCircle2,
} from 'lucide-react';
import type { AuctionResult, AgentBid } from '../types';

export const MultiAgentModal: React.FC = () => {
  const show = useSimulationStore((s) => s.showAuctionModal);
  const setShow = useSimulationStore((s) => s.setShowAuctionModal);
  const results = useSimulationStore((s) => s.auctionResults);
  const isLoading = useSimulationStore((s) => s.isLoadingAuctions);
  const fetchAuctions = useSimulationStore((s) => s.fetchAuctions);

  const [activeTab, setActiveTab] = useState<'auction' | 'swarm'>('swarm');
  const [isSwarmRunning, setIsSwarmRunning] = useState(false);
  const [swarmData, setSwarmData] = useState<any>({
    mission_id: 'M-204',
    consensus_status: 'CONSENSUS_REACHED',
    decision: {
      assigned_satellite_id: 'SAT-01',
      consensus_status: 'CONSENSUS_REACHED',
      winning_utility: 0.884,
      total_candidates_evaluated: 3,
      ranked_pool: [
        { satellite_id: 'SAT-01', composite_utility: 0.884, thermal_score: 0.87, astrodynamics_score: 0.85, isl_latency_ms: 12.5 },
        { satellite_id: 'SAT-04', composite_utility: 0.742, thermal_score: 0.78, astrodynamics_score: 0.62, isl_latency_ms: 25.0 },
      ],
      arbitration_summary: 'Flight Director unanimously awarded Mission M-204 to SAT-01 (Utility: 0.884) with zero hard safety violations.',
    },
    thermal_evaluations: {
      'SAT-01': { verdict: 'APPROVED', safety_score: 0.87, battery_soc_projected: 0.874, thermal_margin_c: 23.6 },
      'SAT-03': { verdict: 'REJECTED_THERMAL_RISK', safety_score: 0.0, battery_soc_projected: 0.399, thermal_margin_c: -1.8 },
      'SAT-04': { verdict: 'APPROVED', safety_score: 0.78, battery_soc_projected: 0.807, thermal_margin_c: 21.0 },
    },
    isl_evaluations: {
      'SAT-01': { verdict: 'FEASIBLE', hop_count: 1, bandwidth_gbps: 7.5, latency_ms: 12.5 },
      'SAT-03': { verdict: 'FEASIBLE', hop_count: 1, bandwidth_gbps: 5.0, latency_ms: 12.5 },
      'SAT-04': { verdict: 'FEASIBLE', hop_count: 2, bandwidth_gbps: 5.0, latency_ms: 25.0 },
    },
    astrodynamics_evaluations: {
      'SAT-01': { verdict: 'OPTIMAL_PASS', geometry_score: 0.85, contact_duration_s: 335, slew_settle_s: 8.0 },
      'SAT-03': { verdict: 'OPTIMAL_PASS', geometry_score: 0.89, contact_duration_s: 369, slew_settle_s: 5.0 },
      'SAT-04': { verdict: 'FEASIBLE', geometry_score: 0.62, contact_duration_s: 275, slew_settle_s: 14.0 },
    },
    deliberation_log: [
      { agent: 'ThermalPowerSafetyAgent', satellite_id: 'SAT-01', verdict: 'APPROVED', rationale: 'Temp: 21.4°C (Margin: 23.6°C) | SoC: 92%' },
      { agent: 'ThermalPowerSafetyAgent', satellite_id: 'SAT-03', verdict: 'REJECTED_THERMAL_RISK', rationale: 'Temp: 46.8°C (Excursion +1.8°C above ceiling) | SoC: 42%' },
      { agent: 'ISLMeshRoutingAgent', satellite_id: 'SAT-01', verdict: 'FEASIBLE', rationale: '3 ISL active laser links | 1-hop route (12.5ms)' },
      { agent: 'AstrodynamicsAgent', satellite_id: 'SAT-01', verdict: 'OPTIMAL_PASS', rationale: 'Max El: 74.5° | Slew: 8.0s | Pass: 335s' },
      { agent: 'FlightDirectorOrchestratorAgent', satellite_id: 'SAT-01', verdict: 'CONSENSUS_REACHED', rationale: 'Flight Director unanimously awarded Mission M-204 to SAT-01 with zero hard safety violations.' },
    ],
  });

  const handleRunSwarmArbitration = async () => {
    setIsSwarmRunning(true);
    try {
      const res = await fetch('/api/multi-agent/swarm', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setSwarmData(data);
      }
    } catch (e) {
      console.error('Failed to run swarm arbitration', e);
    } finally {
      setIsSwarmRunning(false);
    }
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="hud-panel max-w-5xl w-full rounded-xl border border-indigo-500/40 p-6 flex flex-col max-h-[90vh] overflow-hidden shadow-2xl space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-indigo-500/20">
          <div className="flex items-center gap-2">
            <Users className="w-6 h-6 text-indigo-400" />
            <div>
              <h2 className="font-orbitron font-bold text-sm tracking-wider text-white">
                MULTI-AGENT CONSTELLATION INTELLIGENCE
              </h2>
              <p className="text-[10px] font-mono text-slate-400">
                LangGraph Swarm Consensus Arbitration &bull; Combinatorial Auction Ledger
              </p>
            </div>
          </div>
          <button
            onClick={() => setShow(false)}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Toggle */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab('swarm')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
              activeTab === 'swarm'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <GitBranch className="w-4 h-4 text-indigo-300" />
            LangGraph Swarm Consensus (Specialist Agents)
          </button>
          <button
            onClick={() => setActiveTab('auction')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
              activeTab === 'auction'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Users className="w-4 h-4 text-indigo-300" />
            Combinatorial Auction Ledger
          </button>
        </div>

        {/* Body Content */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-1">
          {activeTab === 'swarm' ? (
            <div className="space-y-4">
              {/* Swarm Trigger Bar */}
              <div className="p-4 rounded-xl bg-slate-900/80 border border-indigo-500/30 flex flex-col sm:flex-row items-center justify-between gap-3">
                <div>
                  <div className="text-xs font-mono font-bold text-indigo-300 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    Mission: {swarmData.mission_id} &bull; Consensus: {swarmData.consensus_status}
                  </div>
                  <p className="text-[11px] font-mono text-slate-400 mt-0.5">
                    {swarmData.decision?.arbitration_summary}
                  </p>
                </div>
                <button
                  onClick={handleRunSwarmArbitration}
                  disabled={isSwarmRunning}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-mono text-xs font-bold flex items-center gap-2 transition disabled:opacity-50 cursor-pointer shadow-lg shadow-indigo-600/30"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isSwarmRunning ? 'animate-spin' : ''}`} />
                  {isSwarmRunning ? 'DELIBERATING SWARM...' : 'RUN SWARM ARBITRATION'}
                </button>
              </div>

              {/* Specialist Agents Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {/* 1. Thermal & Power Safety Agent */}
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2 font-mono text-xs">
                  <div className="flex items-center justify-between text-amber-400 font-bold">
                    <span className="flex items-center gap-1.5">
                      <Flame className="w-4 h-4" />
                      Thermal & Power Agent
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300">
                      Stefan-Boltzmann ODE
                    </span>
                  </div>
                  <div className="space-y-1.5 pt-1 text-[11px]">
                    {Object.entries(swarmData.thermal_evaluations || {}).map(([satId, evalData]: [string, any]) => (
                      <div key={satId} className="flex items-center justify-between p-1.5 rounded bg-slate-900/60 border border-slate-800/80">
                        <span className="font-bold text-slate-200">{satId}</span>
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          evalData.verdict === 'APPROVED' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'
                        }`}>
                          {evalData.verdict}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 2. ISL Mesh Routing Agent */}
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2 font-mono text-xs">
                  <div className="flex items-center justify-between text-cyan-400 font-bold">
                    <span className="flex items-center gap-1.5">
                      <Network className="w-4 h-4" />
                      ISL Mesh Routing Agent
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                      Laser Relays
                    </span>
                  </div>
                  <div className="space-y-1.5 pt-1 text-[11px]">
                    {Object.entries(swarmData.isl_evaluations || {}).map(([satId, evalData]: [string, any]) => (
                      <div key={satId} className="flex items-center justify-between p-1.5 rounded bg-slate-900/60 border border-slate-800/80">
                        <span className="font-bold text-slate-200">{satId}</span>
                        <span className="text-cyan-300 text-[10px]">
                          {evalData.hop_count} Hop ({evalData.latency_ms}ms)
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 3. Astrodynamics Agent */}
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2 font-mono text-xs">
                  <div className="flex items-center justify-between text-emerald-400 font-bold">
                    <span className="flex items-center gap-1.5">
                      <Activity className="w-4 h-4" />
                      Astrodynamics Agent
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                      SGP4 Pass Geometry
                    </span>
                  </div>
                  <div className="space-y-1.5 pt-1 text-[11px]">
                    {Object.entries(swarmData.astrodynamics_evaluations || {}).map(([satId, evalData]: [string, any]) => (
                      <div key={satId} className="flex items-center justify-between p-1.5 rounded bg-slate-900/60 border border-slate-800/80">
                        <span className="font-bold text-slate-200">{satId}</span>
                        <span className="text-emerald-300 text-[10px]">
                          Pass: {evalData.contact_duration_s}s ({evalData.verdict})
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Swarm Deliberation Log */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-indigo-400" />
                  LangGraph Multi-Agent Deliberation Trace
                </div>
                <div className="space-y-1.5 max-h-48 overflow-y-auto font-mono text-[11px]">
                  {swarmData.deliberation_log?.map((log: any, idx: number) => (
                    <div key={idx} className="p-2 rounded bg-slate-900/60 border border-slate-800/80 flex items-start gap-2">
                      <span className="px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold text-[10px] whitespace-nowrap">
                        {log.agent}
                      </span>
                      <span className="text-slate-300">{log.rationale}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Tab 2: Auction Ledger */
            <div className="space-y-4">
              {isLoading ? (
                <div className="flex flex-col items-center justify-center py-16 gap-3 text-indigo-300 font-mono text-xs">
                  <RefreshCw className="w-8 h-8 animate-spin text-indigo-400" />
                  <span>Collecting satellite agent sealed bids and resolving contention...</span>
                </div>
              ) : results && results.length > 0 ? (
                results.map((res: AuctionResult) => (
                  <div
                    key={res.mission_id}
                    className="hud-card p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-3"
                  >
                    {/* Mission Header */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-orbitron font-bold text-xs text-indigo-300">
                          {res.mission_id}
                        </span>
                        {res.conflict_resolved && (
                          <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-amber-500/20 border border-amber-500/50 text-amber-300">
                            ⚡ Contested Conflict Resolved ({res.all_bids.length} Bids)
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2 text-xs font-mono">
                        <Award className="w-4 h-4 text-emerald-400" />
                        <span className="font-bold text-emerald-300">
                          {res.winning_satellite_id ? `Winner: ${res.winning_satellite_id} (Score: ${res.winning_bid_value.toFixed(1)})` : 'Unassigned'}
                        </span>
                      </div>
                    </div>

                    <p className="text-xs font-mono text-slate-300">
                      {res.rationale}
                    </p>

                    {/* Bids Table */}
                    {res.all_bids.length > 0 && (
                      <div className="border border-slate-800 rounded-lg overflow-hidden">
                        <table className="w-full text-left text-[11px] font-mono">
                          <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                            <tr>
                              <th className="p-2">Satellite Agent</th>
                              <th className="p-2">Bid Value</th>
                              <th className="p-2">Energy Cost</th>
                              <th className="p-2">Post-Mission SoC</th>
                              <th className="p-2">Slew Penalty</th>
                              <th className="p-2">Max Elevation</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800/60 bg-slate-900/40">
                            {res.all_bids.map((b: AgentBid) => {
                              const isWinner = b.satellite_id === res.winning_satellite_id;

                              return (
                                <tr
                                  key={b.satellite_id}
                                  className={isWinner ? 'bg-indigo-950/40 font-semibold' : ''}
                                >
                                  <td className="p-2 font-bold text-white flex items-center gap-1.5">
                                    {b.satellite_name} ({b.satellite_id})
                                    {isWinner && <span className="text-[9px] text-emerald-400">★ WON</span>}
                                  </td>
                                  <td className="p-2 font-bold text-cyan-300">{b.bid_value.toFixed(1)}</td>
                                  <td className="p-2 text-slate-300">{b.battery_cost_wh.toFixed(1)} Wh</td>
                                  <td className="p-2 text-emerald-300">{(b.marginal_soc_remaining * 100).toFixed(1)}%</td>
                                  <td className="p-2 text-amber-300">-{b.slew_penalty.toFixed(0)}</td>
                                  <td className="p-2 text-slate-300">{b.imaging_window.max_elevation_deg.toFixed(1)}°</td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-12 text-xs font-mono text-slate-400">
                  No auction results found.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-indigo-500/20 flex items-center justify-between">
          <button
            onClick={fetchAuctions}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-indigo-600/30 border border-indigo-500/60 text-indigo-300 text-xs font-mono hover:bg-indigo-600/40 transition disabled:opacity-50 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh Auction Ledger
          </button>

          <button
            onClick={() => setShow(false)}
            className="px-4 py-1.5 rounded-lg bg-slate-800 text-slate-200 text-xs font-mono hover:bg-slate-700 transition cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
export default MultiAgentModal;
