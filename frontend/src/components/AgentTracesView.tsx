import React, { useState } from 'react';
import {
  Activity,
  Clock,
  Terminal,
} from 'lucide-react';

export const AgentTracesView: React.FC = () => {
  const [selectedTraceId, setSelectedTraceId] = useState('trace-m204-opt');

  const TRACES = [
    {
      id: 'trace-m204-opt',
      query: 'Why is Mission M-204 at risk and what should we do?',
      status: 'SUCCESS',
      totalLatencyMs: 142,
      groundingScore: 0.96,
      model: 'AutonomousAgent-v2 + CrossAttention-v2.1',
      steps: [
        {
          step: 1,
          action: 'Plan Generation',
          tool: 'agent.planner',
          input: { query: 'Why is Mission M-204 at risk?' },
          output: { steps: ['resolve_mission', 'query_telemetry', 'check_anomalies', 'evaluate_candidates', 'solve_cpsat'] },
          latencyMs: 18,
          status: 'SUCCESS',
        },
        {
          step: 2,
          action: 'Telemetry Ingestion & Quality Check',
          tool: 'mcp.get_constellation_status',
          input: { include_telemetry: true, filter_faults: true },
          output: { total_nodes: 12, anomalous_nodes: ['SAT-03'], quality_score: 0.998 },
          latencyMs: 24,
          status: 'SUCCESS',
        },
        {
          step: 3,
          action: 'Anomaly Inspection & Isolation',
          tool: 'anomaly_detection.isolation_forest',
          input: { sat_id: 'SAT-03', features: ['temp_c', 'battery_soc', 'slew_rate'] },
          output: { anomaly_score: 0.789, is_anomaly: true, reason: 'Thermal excursion +3.2σ (38.4°C)' },
          latencyMs: 14,
          status: 'SUCCESS',
        },
        {
          step: 4,
          action: 'Cross-Attention Neural Token Ranking',
          tool: 'ml.cross_attention_ranker',
          input: { mission_id: 'M-204', candidates: ['SAT-01', 'SAT-02', 'SAT-03', 'SAT-04'] },
          output: { ranked: [{ id: 'SAT-01', score: 0.942 }, { id: 'SAT-04', score: 0.887 }] },
          latencyMs: 32,
          status: 'SUCCESS',
        },
        {
          step: 5,
          action: 'Deterministic Constraint Optimization',
          tool: 'optimization.cp_sat_solver',
          input: { candidate_scores: { 'SAT-01': 0.942, 'SAT-04': 0.887 }, hard_invariants: ['los', 'soc', 'thermal'] },
          output: { optimal_assignment: 'SAT-01', solver_status: 'OPTIMAL', hard_violations: 0 },
          latencyMs: 28,
          status: 'SUCCESS',
        },
        {
          step: 6,
          action: 'Trust & Grounding Verification',
          tool: 'trust_layer.grounding_verifier',
          input: { evidence_sources: 3, claim: 'SAT-01 optimal candidate' },
          output: { grounding_verified: true, citation_count: 3, refusal: false },
          latencyMs: 16,
          status: 'SUCCESS',
        },
      ],
    },
    {
      id: 'trace-rag-refusal',
      query: 'What was the orbital inclination of satellite SAT-999 during 2021 launch?',
      status: 'REFUSAL_GROUNDED',
      totalLatencyMs: 48,
      groundingScore: 1.0,
      model: 'HybridMissionRAG + TrustLayer',
      steps: [
        {
          step: 1,
          action: 'Semantic RAG Query',
          tool: 'mcp.ask_mission_history',
          input: { query: 'SAT-999 2021 launch inclination' },
          output: { bm25_hits: 0, dense_hits: 0, confidence: 0.12 },
          latencyMs: 32,
          status: 'INSUFFICIENT_EVIDENCE',
        },
        {
          step: 2,
          action: 'Honest Hallucination Refusal Gate',
          tool: 'trust_layer.refusal_engine',
          input: { confidence: 0.12, threshold: 0.70 },
          output: { refusal_triggered: true, message: 'I cannot verify information regarding SAT-999 as it is not in the verified constellation catalog.' },
          latencyMs: 16,
          status: 'SUCCESS',
        },
      ],
    },
  ];

  const currentTrace = TRACES.find((t) => t.id === selectedTraceId) || TRACES[0];

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto bg-slate-950 p-6 space-y-6">
      {/* View Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-cyan-500/20 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-400/30 text-emerald-400">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold font-orbitron tracking-wider text-slate-100">
                  Agent Traces & MCP
                </h1>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono">
                  Deterministic Tools
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-mono">
                  MCP Server
                </span>
              </div>
              <p className="text-sm text-slate-400 mt-0.5">
                Inspect Agent Planner &bull; Tool Call Execution Timings &bull; Trust Grounding & Honest Refusals
              </p>
            </div>
          </div>
        </div>

        {/* Trace selector */}
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl p-1.5 font-mono text-xs">
          <span className="text-slate-500 px-2">Trace Session:</span>
          {TRACES.map((t) => (
            <button
              key={t.id}
              onClick={() => setSelectedTraceId(t.id)}
              className={`px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                selectedTraceId === t.id
                  ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {t.id}
            </button>
          ))}
        </div>
      </div>

      {/* Trace Overview Card */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div className="space-y-1">
            <div className="text-xs font-mono text-slate-400">Prompt / Intent:</div>
            <div className="text-sm font-semibold text-slate-100 font-mono">"{currentTrace.query}"</div>
          </div>
          <div className="flex items-center gap-3 font-mono text-xs">
            <div className="px-3 py-1 rounded-lg bg-slate-800 text-slate-300">
              Total Latency: <span className="text-cyan-400 font-bold">{currentTrace.totalLatencyMs}ms</span>
            </div>
            <div className="px-3 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold">
              Grounding: {Math.round(currentTrace.groundingScore * 100)}%
            </div>
          </div>
        </div>

        {/* Step-by-Step Tool Waterfall */}
        <div className="space-y-3 pt-2">
          <h4 className="text-xs font-semibold uppercase tracking-wider font-orbitron text-slate-300 flex items-center gap-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            Execution Trace & Tool Calls ({currentTrace.steps.length} steps)
          </h4>

          <div className="space-y-3">
            {currentTrace.steps.map((st) => (
              <div
                key={st.step}
                className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 hover:border-cyan-500/30 transition-all space-y-2"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-300 flex items-center justify-center font-bold text-[11px]">
                      {st.step}
                    </span>
                    <span className="font-semibold text-slate-200">{st.action}</span>
                    <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-cyan-400 text-[10px]">
                      {st.tool}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-slate-400 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      {st.latencyMs}ms
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      st.status === 'SUCCESS'
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : 'bg-amber-500/20 text-amber-300'
                    }`}>
                      {st.status}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-xs font-mono">
                  <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase mb-1">Tool Input:</div>
                    <pre className="text-slate-300 overflow-x-auto text-[11px]">
                      {JSON.stringify(st.input, null, 2)}
                    </pre>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase mb-1">Tool Output:</div>
                    <pre className="text-emerald-300/90 overflow-x-auto text-[11px]">
                      {JSON.stringify(st.output, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
export default AgentTracesView;
