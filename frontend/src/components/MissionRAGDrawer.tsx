import React, { useState } from 'react';
import {
  X,
  Search,
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Sparkles,
  Clock,
  Send,
  Loader2,
} from 'lucide-react';
import type { MissionQAResponse } from '../types';

interface MissionRAGDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const SAMPLE_QUERIES = [
  "Why was satellite 3 assigned to Hurricane Alpha?",
  "What triggered the autonomous CAM burn on SAT-04?",
  "Explain the battery thermal anomaly and how the AI responded.",
  "Why was SAT-02 rejected for the Tokyo SAR mission?",
  "What is the capital of France?", // Out of domain test
];

export const MissionRAGDrawer: React.FC<MissionRAGDrawerProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [qaResult, setQaResult] = useState<MissionQAResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleAsk = async (queryText: string) => {
    if (!queryText.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/ai/mission/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryText, top_k: 4 }),
      });
      if (!response.ok) {
        throw new Error(`API error ${response.status}: ${response.statusText}`);
      }
      const data: MissionQAResponse = await response.json();
      setQaResult(data);
    } catch (err: any) {
      console.error('RAG QA failed:', err);
      setError(err.message || 'Failed to query mission history engine.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleAsk(query);
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-xl h-full bg-slate-950 border-l border-cyan-500/30 flex flex-col shadow-2xl overflow-hidden font-sans">
        {/* Header */}
        <div className="bg-slate-900 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                Mission AI Copilot & Decision RAG
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                  Grounded QA
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Verifiable operational history Q&A with strict source citation grounding.
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
                placeholder="Ask about satellite assignments, anomalies, rejections..."
                className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-10 pr-24 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition"
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

          {/* QA Result Card */}
          {qaResult && (
            <div className="space-y-4 animate-fade-in">
              {/* Answer Box */}
              <div
                className={`p-5 rounded-xl border ${
                  qaResult.grounded
                    ? 'bg-slate-900/80 border-cyan-500/30 text-slate-100'
                    : 'bg-amber-950/20 border-amber-800/40 text-amber-200'
                }`}
              >
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
                  <div className="flex items-center gap-2">
                    {qaResult.grounded ? (
                      <span className="flex items-center gap-1 text-xs font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        GROUNDED ANSWER
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs font-mono font-bold text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800/60">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        HONEST REFUSAL (OUT OF DOMAIN)
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] font-mono text-slate-400">
                    Confidence: <span className="text-cyan-400 font-bold">{(qaResult.confidence_score * 100).toFixed(1)}%</span>
                  </div>
                </div>

                <p className="text-sm leading-relaxed whitespace-pre-wrap font-sans text-slate-200">
                  {qaResult.answer}
                </p>
              </div>

              {/* Verified Citations Section */}
              {qaResult.citations && qaResult.citations.length > 0 && (
                <div className="space-y-2.5">
                  <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-cyan-400" />
                    Verified Operational Source Citations ({qaResult.citations.length})
                  </h3>
                  <div className="space-y-2">
                    {qaResult.citations.map((cit, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition space-y-1.5"
                      >
                        <div className="flex items-center justify-between text-xs">
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-bold text-cyan-400 bg-cyan-950/80 px-1.5 py-0.5 rounded text-[11px] border border-cyan-800/50">
                              [{cit.log_id}]
                            </span>
                            <span className="font-mono text-[10px] text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">
                              {cit.event_type}
                            </span>
                          </div>
                          <div className="flex items-center gap-1 text-[10px] font-mono text-slate-500">
                            <Clock className="w-3 h-3" />
                            <span>{new Date(cit.timestamp_iso).toLocaleTimeString()}</span>
                          </div>
                        </div>
                        <p className="text-xs text-slate-300 font-mono">
                          {cit.summary}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Placeholder / Empty State */}
          {!qaResult && !isLoading && (
            <div className="p-8 border border-dashed border-slate-800 rounded-2xl text-center space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mx-auto">
                <Sparkles className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-semibold text-slate-200">Grounded Decision History Engine</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                ORBIT-X maintains an immutable ring-buffer of multi-agent bids, solver constraints, and anomaly responses. Ask any question to retrieve cited explanations.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
