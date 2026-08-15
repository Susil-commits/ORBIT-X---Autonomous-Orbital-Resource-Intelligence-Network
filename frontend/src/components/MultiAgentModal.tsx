import React from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import { X, Users, RefreshCw, Award } from 'lucide-react';
import type { AuctionResult, AgentBid } from '../types';

export const MultiAgentModal: React.FC = () => {
  const show = useSimulationStore((s) => s.showAuctionModal);
  const setShow = useSimulationStore((s) => s.setShowAuctionModal);
  const results = useSimulationStore((s) => s.auctionResults);
  const isLoading = useSimulationStore((s) => s.isLoadingAuctions);
  const fetchAuctions = useSimulationStore((s) => s.fetchAuctions);

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="hud-panel max-w-4xl w-full rounded-xl border border-indigo-500/40 p-6 flex flex-col max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-indigo-500/20">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-400" />
            <div>
              <h2 className="font-orbitron font-bold text-sm tracking-wider text-white">
                MULTI-AGENT COOPERATIVE BIDDING & AUCTION LEDGER
              </h2>
              <p className="text-[10px] font-mono text-slate-400">
                Decentralized agent cost evaluation & combinatorial slot resolution
              </p>
            </div>
          </div>
          <button
            onClick={() => setShow(false)}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto py-4 space-y-4">
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

        {/* Footer */}
        <div className="pt-3 border-t border-indigo-500/20 flex items-center justify-between">
          <button
            onClick={fetchAuctions}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-indigo-600/30 border border-indigo-500/60 text-indigo-300 text-xs font-mono hover:bg-indigo-600/40 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh Auction Ledger
          </button>

          <button
            onClick={() => setShow(false)}
            className="px-4 py-1.5 rounded-lg bg-slate-800 text-slate-200 text-xs font-mono hover:bg-slate-700 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
