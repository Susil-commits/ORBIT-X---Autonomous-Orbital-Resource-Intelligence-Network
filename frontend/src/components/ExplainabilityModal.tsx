import React, { useState, useEffect } from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import {
  X,
  CheckCircle2,
  XCircle,
  Battery,
  Sparkles,
  Cpu,
  ShieldCheck,
  TrendingUp,
  TrendingDown,
  Loader2,
} from 'lucide-react';
import type { CandidateEvaluation, NeuralBidPreviewResponse } from '../types';

export const ExplainabilityModal: React.FC = () => {
  const show = useSimulationStore((s) => s.showExplainModal);
  const setShow = useSimulationStore((s) => s.setShowExplainModal);
  const explanation = useSimulationStore((s) => s.activeExplanation);

  const [selectedSat, setSelectedSat] = useState<string | null>(null);
  const [neuralPreview, setNeuralPreview] = useState<NeuralBidPreviewResponse | null>(null);
  const [isLoadingNeural, setIsLoadingNeural] = useState(false);

  useEffect(() => {
    if (explanation?.selected_satellite_id) {
      setSelectedSat(explanation.selected_satellite_id);
    }
  }, [explanation]);

  useEffect(() => {
    if (!selectedSat || !explanation) return;
    const fetchNeuralBid = async () => {
      setIsLoadingNeural(true);
      try {
        const res = await fetch('http://localhost:8000/api/ai/preview_bid', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            satellite_id: selectedSat,
            priority: explanation.priority || 4,
            max_elevation_deg: 65.0,
            slew_penalty: 0.0,
          }),
        });
        if (res.ok) {
          const data: NeuralBidPreviewResponse = await res.json();
          setNeuralPreview(data);
        }
      } catch (e) {
        console.error('Failed to preview neural bid', e);
      } finally {
        setIsLoadingNeural(false);
      }
    };
    fetchNeuralBid();
  }, [selectedSat, explanation]);

  if (!show || !explanation) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="hud-panel max-w-3xl w-full rounded-2xl border border-cyan-500/40 p-6 flex flex-col max-h-[90vh] overflow-hidden shadow-2xl font-sans">
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-cyan-500/20">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-orbitron font-bold text-sm tracking-wider text-white flex items-center gap-2">
                DECISION EXPLAINABILITY & TREESHAP REASONING TRAIL
              </h2>
              <p className="text-xs text-slate-400 font-mono">
                CP-SAT Global Objective • PyTorch BidValueMLP • Distilled TreeSHAP Attributions
              </p>
            </div>
          </div>
          <button
            onClick={() => setShow(false)}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto py-4 space-y-4">
          {/* Mission & Winner Banner */}
          <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-700/60 flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="font-orbitron font-bold text-sm text-cyan-300">
                {explanation.mission_name} ({explanation.mission_id})
              </span>
              <span className="text-xs font-mono px-2.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                Priority {explanation.priority}
              </span>
            </div>
            <p className="text-xs font-mono text-slate-300 leading-relaxed">
              {explanation.selection_rationale}
            </p>
          </div>

          {/* Binding Constraints & Battery Margin */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
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

            <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800 flex flex-col justify-between">
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
            <h3 className="font-orbitron font-semibold text-xs text-slate-300 mb-2 flex items-center justify-between">
              <span>Candidate Evaluations & Counterfactuals</span>
              <span className="text-[10px] font-mono text-slate-500">Click a node below to inspect TreeSHAP</span>
            </h3>
            <div className="border border-slate-800 rounded-xl overflow-hidden">
              <table className="w-full text-left text-[11px] font-mono">
                <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="p-2.5">Satellite</th>
                    <th className="p-2.5">Eligible</th>
                    <th className="p-2.5">Bid Score</th>
                    <th className="p-2.5">Proj. SoC</th>
                    <th className="p-2.5">Reason / Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                  {explanation.candidates_evaluated.map((c: CandidateEvaluation) => {
                    const isWinner = c.satellite_id === explanation.selected_satellite_id;
                    const isInspecting = c.satellite_id === selectedSat;

                    return (
                      <tr
                        key={c.satellite_id}
                        onClick={() => setSelectedSat(c.satellite_id)}
                        className={`cursor-pointer transition ${
                          isInspecting
                            ? 'bg-cyan-950/50 border-l-2 border-cyan-400'
                            : isWinner
                            ? 'bg-cyan-950/20 font-semibold hover:bg-slate-900'
                            : 'hover:bg-slate-900/60'
                        }`}
                      >
                        <td className="p-2.5 font-bold text-white flex items-center gap-1.5">
                          {c.satellite_id}
                          {isWinner && <span className="text-[9px] text-cyan-400 font-normal">★ WINNER</span>}
                        </td>
                        <td className="p-2.5">
                          {c.eligible ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          ) : (
                            <XCircle className="w-4 h-4 text-rose-500" />
                          )}
                        </td>
                        <td className="p-2.5 text-cyan-300">{c.bid_score.toFixed(1)}</td>
                        <td className="p-2.5">{(c.projected_soc_after_mission * 100).toFixed(0)}%</td>
                        <td className="p-2.5 text-slate-300 text-[10px]">
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

          {/* Distilled TreeSHAP Local Feature Attribution Breakdown */}
          {selectedSat && (
            <div className="bg-slate-900/90 border border-cyan-500/30 rounded-xl p-4 space-y-3 font-mono">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-cyan-400" />
                  <span className="text-xs font-bold text-slate-100">
                    PyTorch Neural Valuation & Distilled TreeSHAP ({selectedSat})
                  </span>
                </div>
                {neuralPreview && (
                  <div className="flex items-center gap-2 text-[10px]">
                    <span className="bg-cyan-950 text-cyan-300 border border-cyan-800 px-2 py-0.5 rounded">
                      NN Score: <strong className="text-white">{neuralPreview.predicted_bid_score.toFixed(1)}</strong>
                    </span>
                    <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                      CP-SAT Prob: <strong>{(neuralPreview.cpsat_agreement_prob * 100).toFixed(0)}%</strong>
                    </span>
                    <span className="flex items-center gap-1 bg-emerald-950 text-emerald-300 border border-emerald-800 px-1.5 py-0.5 rounded">
                      <ShieldCheck className="w-3 h-3 text-emerald-400" />
                      Hash Aligned
                    </span>
                  </div>
                )}
              </div>

              {isLoadingNeural ? (
                <div className="py-6 flex items-center justify-center gap-2 text-xs text-slate-400">
                  <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
                  <span>Computing TreeSHAP feature attributions...</span>
                </div>
              ) : neuralPreview ? (
                <div className="space-y-2">
                  <div className="text-[11px] text-slate-400 flex items-center justify-between">
                    <span>Base Value E[f(x)]: {neuralPreview.explanation.base_value.toFixed(1)}</span>
                    <span className="text-[10px] text-slate-500">
                      Surrogate: XGBRegressor Distillation (is_distilled=true)
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                    {neuralPreview.explanation.feature_attributions.map((attr, idx) => {
                      const isPositive = attr.contribution_direction === 'POSITIVE';
                      const barWidth = Math.min(100, Math.abs(attr.shap_value) * 3);

                      return (
                        <div
                          key={idx}
                          className="bg-slate-950 p-2 rounded-lg border border-slate-800 flex flex-col justify-between gap-1 text-[10px]"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-slate-300 font-medium truncate">{attr.description}</span>
                            <span className={`font-bold flex items-center gap-0.5 ${isPositive ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                              {attr.shap_value > 0 ? `+${attr.shap_value.toFixed(2)}` : attr.shap_value.toFixed(2)}
                            </span>
                          </div>

                          <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden flex">
                            <div
                              className={`h-full rounded-full ${isPositive ? 'bg-emerald-500' : 'bg-amber-500'}`}
                              style={{ width: `${barWidth}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : null}
            </div>
          )}
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
