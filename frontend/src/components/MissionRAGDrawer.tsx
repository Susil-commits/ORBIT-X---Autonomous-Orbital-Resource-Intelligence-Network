import React, { useState } from 'react';
import {
  X,
  Search,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Sparkles,
  Send,
  Loader2,
  ShieldCheck,
  Cpu,
  Layers,
  ThumbsUp,
  ThumbsDown,
  HelpCircle,
  Activity,
  Check,
} from 'lucide-react';
import type { TrustLayerResponse, HumanFeedbackResponse } from '../types';
import { API_BASE } from '../config';

interface MissionRAGDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const SAMPLE_QUERIES = [
  "Why was satellite 3 assigned to Hurricane Alpha?",
  "Why did the system reject SAT-02 for the Tokyo SAR mission?",
  "Explain the battery thermal anomaly on SAT-07 and how the AI responded.",
  "Show data lineage and model features for Mission M-204.",
  "What is the capital of France?", // Out of domain test
];

export const MissionRAGDrawer: React.FC<MissionRAGDrawerProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [trustResult, setTrustResult] = useState<TrustLayerResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [feedbackStatus, setFeedbackStatus] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleAsk = async (queryText: string) => {
    if (!queryText.trim()) return;
    setIsLoading(true);
    setError(null);
    setFeedbackStatus(null);
    try {
      const response = await fetch(`${API_BASE}/api/context/ask?query=${encodeURIComponent(queryText)}`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`API error ${response.status}: ${response.statusText}`);
      }
      const data: TrustLayerResponse = await response.json();
      setTrustResult(data);
    } catch (err: any) {
      console.error('Ask ORBIT-X query failed:', err);
      setError(err.message || 'Failed to query Ask ORBIT-X Trust Layer.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (type: 'APPROVE' | 'REJECT' | 'INVESTIGATE') => {
    if (!trustResult) return;
    try {
      const res = await fetch(`${API_BASE}/api/context/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision_record_id: `DEC-${Date.now().toString().slice(-6)}`,
          mission_id: 'EO-OPERATIONAL',
          feedback_type: type,
          operator_notes: `Operator submitted ${type} action through Ask ORBIT-X HUD.`,
        }),
      });
      if (res.ok) {
        const data: HumanFeedbackResponse = await res.json();
        setFeedbackStatus(`Feedback '${type}' successfully logged to continuous evaluation database (${data.feedback_id}).`);
      }
    } catch (e) {
      console.error('Failed to submit feedback:', e);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleAsk(query);
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm animate-fade-in font-sans">
      <div className="w-full max-w-2xl h-full bg-slate-950 border-l border-cyan-500/30 flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-slate-900 border-b border-slate-800 px-6 py-4 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                Ask ORBIT-X: Decision Intelligence Copilot
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                  Trust Layer
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Auditable decision reasoning combining Telemetry, ML Models, CP-SAT, SHAP & Citations.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Query Bar */}
          <form onSubmit={handleFormSubmit} className="space-y-3">
            <div className="relative flex items-center">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask why a mission was assigned, check anomalies, trace lineage..."
                className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-10 pr-24 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition shadow-inner"
              />
              <Search className="w-4 h-4 text-slate-500 absolute left-3.5" />
              <button
                type="submit"
                disabled={isLoading || !query.trim()}
                className="absolute right-2 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-medium text-xs flex items-center gap-1.5 transition shadow-sm"
              >
                {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                <span>Ask</span>
              </button>
            </div>

            {/* Quick Sample Queries */}
            <div className="flex flex-wrap gap-1.5 pt-1">
              <span className="text-[11px] font-mono text-slate-500 self-center mr-1">Suggestions:</span>
              {SAMPLE_QUERIES.map((sq, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setQuery(sq);
                    handleAsk(sq);
                  }}
                  className="text-[11px] font-mono bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 hover:border-cyan-500/50 rounded-md px-2 py-1 transition text-left"
                >
                  {sq}
                </button>
              ))}
            </div>
          </form>

          {/* Error Message */}
          {error && (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-start gap-3">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Query Failed</p>
                <p className="opacity-90">{error}</p>
              </div>
            </div>
          )}

          {/* Trust Result Card */}
          {trustResult && (
            <div className="space-y-5 animate-fade-in">
              {/* Answer Box */}
              <div className="p-5 rounded-xl bg-slate-900/90 border border-cyan-500/30 text-slate-100 shadow-lg space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <span className="flex items-center gap-1 text-xs font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      AUDITED REASONING
                    </span>
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                      trustResult.confidence_level === 'HIGH'
                        ? 'bg-cyan-950 text-cyan-400 border-cyan-800'
                        : 'bg-amber-950 text-amber-400 border-amber-800'
                    }`}>
                      Confidence: {(trustResult.confidence_score * 100).toFixed(1)}% ({trustResult.confidence_level})
                    </span>
                  </div>
                  <div className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                    <Cpu className="w-3 h-3 text-cyan-400" />
                    <span>Tools: {trustResult.tools_used.length}</span>
                  </div>
                </div>

                <p className="text-sm leading-relaxed whitespace-pre-wrap text-slate-200">
                  {trustResult.answer}
                </p>

                {trustResult.lineage_summary && (
                  <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 text-xs text-slate-300 font-mono space-y-1">
                    <div className="text-[10px] uppercase font-bold text-cyan-400 flex items-center gap-1.5">
                      <Layers className="w-3 h-3" />
                      Data Lineage Path
                    </div>
                    <p className="text-[11px] text-slate-400">{trustResult.lineage_summary}</p>
                  </div>
                )}
              </div>

              {/* Multi-source Evidence List */}
              {trustResult.evidence && trustResult.evidence.length > 0 && (
                <div className="space-y-2.5">
                  <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-cyan-400" />
                    Audited Multi-Source Evidence ({trustResult.evidence.length})
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                    {trustResult.evidence.map((ev, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition space-y-1"
                      >
                        <div className="flex items-center justify-between text-[10px] font-mono">
                          <span className="font-bold text-cyan-400 bg-cyan-950/80 px-1.5 py-0.5 rounded border border-cyan-800/50">
                            {ev.evidence_type}
                          </span>
                          <span className="text-emerald-400 flex items-center gap-1">
                            <Check className="w-3 h-3" /> Verified
                          </span>
                        </div>
                        <p className="text-xs text-slate-300 font-mono line-clamp-2">
                          {ev.summary}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Verified Citations Section */}
              {trustResult.citations && trustResult.citations.length > 0 && (
                <div className="space-y-2.5">
                  <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-cyan-400" />
                    Verified Citations ({trustResult.citations.length})
                  </h3>
                  <div className="space-y-2">
                    {trustResult.citations.map((cit, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono space-y-1"
                      >
                        <div className="flex items-center justify-between text-[11px]">
                          <span className="font-bold text-cyan-400">[{cit.record_id}] {cit.event_type}</span>
                          <span className="text-slate-500">T+{cit.sim_time_s.toFixed(0)}s</span>
                        </div>
                        <p className="text-slate-300 text-[11px]">{cit.summary}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Human-in-the-Loop Action Bar */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-cyan-400" />
                    Human-in-the-Loop Review
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">Continuous AI Alignment</span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleFeedback('APPROVE')}
                    className="flex-1 py-2 px-3 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 text-xs font-medium flex items-center justify-center gap-1.5 transition"
                  >
                    <ThumbsUp className="w-3.5 h-3.5" />
                    Approve Decision
                  </button>
                  <button
                    onClick={() => handleFeedback('REJECT')}
                    className="flex-1 py-2 px-3 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/40 text-rose-300 text-xs font-medium flex items-center justify-center gap-1.5 transition"
                  >
                    <ThumbsDown className="w-3.5 h-3.5" />
                    Reject
                  </button>
                  <button
                    onClick={() => handleFeedback('INVESTIGATE')}
                    className="flex-1 py-2 px-3 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/40 text-cyan-300 text-xs font-medium flex items-center justify-center gap-1.5 transition"
                  >
                    <HelpCircle className="w-3.5 h-3.5" />
                    Investigate
                  </button>
                </div>

                {feedbackStatus && (
                  <p className="text-[11px] text-emerald-400 font-mono animate-fade-in bg-emerald-950/40 p-2 rounded border border-emerald-800/50">
                    ✓ {feedbackStatus}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Placeholder / Empty State */}
          {!trustResult && !isLoading && (
            <div className="p-8 border border-dashed border-slate-800 rounded-2xl text-center space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mx-auto">
                <Sparkles className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-semibold text-slate-200">Ask ORBIT-X: Decision Intelligence Copilot</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                Connects real-time telemetry, Cross-Attention neural predictions, CP-SAT constraints, and SHAP attributions into an auditable decision trail with human review actions.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
