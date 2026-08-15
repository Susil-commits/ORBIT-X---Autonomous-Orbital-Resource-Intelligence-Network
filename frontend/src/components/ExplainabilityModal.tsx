import React from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import { X, CheckCircle2, XCircle, Battery, Sparkles } from 'lucide-react';
import type { CandidateEvaluation } from '../types';

export const ExplainabilityModal: React.FC = () => {
  const show = useSimulationStore((s) => s.showExplainModal);
  const setShow = useSimulationStore((s) => s.setShowExplainModal);
  const explanation = useSimulationStore((s) => s.activeExplanation);

  if (!show || !explanation) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="hud-panel max-w-2xl w-full rounded-xl border border-cyan-500/40 p-6 flex flex-col max-h-[85vh] overflow-hidden shadow-2xl">
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-cyan-500/20">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            <h2 className="font-orbitron font-bold text-sm tracking-wider text-white">
              DECISION EXPLAINABILITY & REASONING TRAIL
            </h2>
          </div>
          <button
            onClick={() => setShow(false)}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto py-4 space-y-4">
          {/* Mission & Winner Banner */}
          <div className="bg-slate-900/80 p-4 rounded-lg border border-slate-700/60 flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="font-orbitron font-bold text-sm text-cyan-300">
                {explanation.mission_name} ({explanation.mission_id})
              </span>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                Priority {explanation.priority}
              </span>
            </div>
            <p className="text-xs font-mono text-slate-300 leading-relaxed">
              {explanation.selection_rationale}
            </p>
          </div>

          {/* Binding Constraints & Battery Margin */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <span className="text-[10px] uppercase font-mono text-slate-400">Binding Constraints</span>
              <div className="flex flex-wrap gap-1.5 mt-2">
                {explanation.binding_constraints.map((c, i) => (
                  <span
                    key={i}
                    className="text-[9px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 border border-indigo-500/40 text-indigo-300"
                  >
                    {c}
                  </span>
                ))}
              </div>
            </div>

            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 flex flex-col justify-between">
              <span className="text-[10px] uppercase font-mono text-slate-400">Energy Safety Margin</span>
              <div className="flex items-center gap-2 mt-1">
                <Battery className="w-4 h-4 text-emerald-400" />
                <span className="font-mono text-sm font-bold text-emerald-300">
                  +{explanation.battery_margin_pct.toFixed(1)}% above 20% floor
                </span>
              </div>
            </div>
          </div>

          {/* Candidate Satellites Evaluation Table */}
          <div>
            <h3 className="font-orbitron font-semibold text-xs text-slate-300 mb-2">
              Candidate Evaluations & Counterfactuals ({explanation.candidates_evaluated.length} Nodes)
            </h3>
            <div className="border border-slate-800 rounded-lg overflow-hidden">
              <table className="w-full text-left text-[11px] font-mono">
                <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="p-2">Satellite</th>
                    <th className="p-2">Eligible</th>
                    <th className="p-2">Bid Score</th>
                    <th className="p-2">Proj. SoC</th>
                    <th className="p-2">Reason / Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                  {explanation.candidates_evaluated.map((c: CandidateEvaluation) => {
                    const isWinner = c.satellite_id === explanation.selected_satellite_id;

                    return (
                      <tr
                        key={c.satellite_id}
                        className={isWinner ? 'bg-cyan-950/30 font-semibold' : ''}
                      >
                        <td className="p-2 font-bold text-white flex items-center gap-1">
                          {c.satellite_id}
                          {isWinner && <span className="text-[9px] text-cyan-400 font-normal">★ WINNER</span>}
                        </td>
                        <td className="p-2">
                          {c.eligible ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          ) : (
                            <XCircle className="w-4 h-4 text-rose-500" />
                          )}
                        </td>
                        <td className="p-2 text-cyan-300">{c.bid_score.toFixed(1)}</td>
                        <td className="p-2">{(c.projected_soc_after_mission * 100).toFixed(0)}%</td>
                        <td className="p-2 text-slate-300 text-[10px]">
                          {isWinner ? (
                            <span className="text-emerald-400">Selected: optimal CP-SAT objective score</span>
                          ) : (
                            <span className="text-slate-400">{c.rejection_reason || 'Out-bid by higher scoring candidate'}</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="pt-3 border-t border-cyan-500/20 flex justify-end">
          <button
            onClick={() => setShow(false)}
            className="px-4 py-1.5 rounded-lg bg-slate-800 text-slate-200 text-xs font-mono hover:bg-slate-700 transition"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
