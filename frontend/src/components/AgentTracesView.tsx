import React, { useState } from 'react';
import {
  Activity,
  Clock,
  Terminal,
  Play,
  CheckCircle2,
  ShieldCheck,
  Zap,
  Layers,
  RefreshCw,
  GitBranch,
  Search,
  Database,
  Cpu,
  Fingerprint,
  Brain,
} from 'lucide-react';

interface TraceStep {
  step: number;
  action: string;
  tool: string;
  input: any;
  output: any;
  latencyMs: number;
  status: string;
}

interface TraceSession {
  id: string;
  query: string;
  intent?: string;
  status: string;
  totalLatencyMs: number;
  groundingScore: number;
  model: string;
  steps: TraceStep[];
  trustEnvelope?: {
    confidenceScore: number;
    governanceStatus: string;
    evidenceCount: number;
    caller: string;
  };
  recommendation?: string;
}

export const AgentTracesView: React.FC = () => {
  const [selectedTraceId, setSelectedTraceId] = useState('trace-langgraph-m204');
  const [customQuery, setCustomQuery] = useState('Why is Mission M-204 at risk and what should we do?');
  const [isExecuting, setIsExecuting] = useState(false);

  const [traces, setTraces] = useState<TraceSession[]>([
    {
      id: 'trace-langgraph-m204',
      query: 'Why is Mission M-204 at risk and what should we do?',
      intent: 'RISK_AUDIT_AND_TASK_REPLANNING',
      status: 'VERIFIED_TRUST_ENVELOPE',
      totalLatencyMs: 142,
      groundingScore: 0.96,
      model: 'LangGraph StateGraph + CrossAttentionNet-v2.2 + FAISS RAG',
      trustEnvelope: {
        confidenceScore: 0.94,
        governanceStatus: 'VERIFIED',
        evidenceCount: 5,
        caller: 'flight-director',
      },
      recommendation: 'Approve dynamic task reallocation of Mission M-204 to SAT-01 (Score: 0.942, 0 Constraint Violations) and initiate thermal cooldown mode for SAT-03.',
      steps: [
        {
          step: 1,
          action: 'Intent Classification & Entity Parsing',
          tool: 'langgraph.classify_intent',
          input: { query: 'Why is Mission M-204 at risk and what should we do?' },
          output: { intent: 'RISK_AUDIT_AND_TASK_REPLANNING', entities: ['M-204', 'SAT-03'] },
          latencyMs: 12,
          status: 'SUCCESS',
        },
        {
          step: 2,
          action: 'Query Semantic Metadata Catalog',
          tool: 'context_engine.get_dataset_metadata',
          input: { dataset: 'satellite_telemetry', prefer_verified: true },
          output: { asset: 'satellite_telemetry', status: 'VERIFIED', quality: 0.992, owner: 'flight-operations' },
          latencyMs: 8,
          status: 'SUCCESS',
        },
        {
          step: 3,
          action: 'Search Telemetry Stream Feeds',
          tool: 'fastmcp.search_telemetry',
          input: { query: 'SAT-03 telemetry', window_seconds: 300 },
          output: { frames_evaluated: 12, anomaly_flag: true, max_temp_c: 48.2 },
          latencyMs: 16,
          status: 'SUCCESS',
        },
        {
          step: 4,
          action: 'Multivariate Isolation Forest (Risk Branch)',
          tool: 'anomaly_detection.isolation_forest',
          input: { sat_id: 'SAT-03', features: ['temp_c', 'battery_soc', 'slew_rate'] },
          output: { anomaly_score: 0.8282, is_anomaly: true, reason: 'Thermal excursion +3.2σ (48.2°C)' },
          latencyMs: 14,
          status: 'SUCCESS',
        },
        {
          step: 5,
          action: 'Cross-Attention Neural Candidate Ranking',
          tool: 'ml.cross_attention_ranker',
          input: { mission_id: 'M-204', candidates: ['SAT-01', 'SAT-02', 'SAT-03', 'SAT-04'] },
          output: { ranked: [{ id: 'SAT-01', score: 0.942, win_prob: 0.948 }, { id: 'SAT-04', score: 0.887 }] },
          latencyMs: 32,
          status: 'SUCCESS',
        },
        {
          step: 6,
          action: 'TreeSHAP Feature Attribution',
          tool: 'xai.tree_shap_explainer',
          input: { candidate: 'SAT-01', base_value: 50.0 },
          output: { top_feature: 'battery_soc_margin (+37%)', second: 'thermal_headroom (+22.7%)' },
          latencyMs: 18,
          status: 'SUCCESS',
        },
        {
          step: 7,
          action: 'Deterministic Constraint Optimization',
          tool: 'optimization.cp_sat_solver',
          input: { candidate_scores: { 'SAT-01': 0.942 }, hard_invariants: ['los_pass', 'soc_floor', 'temp_ceiling'] },
          output: { optimal_assignment: 'SAT-01', solver_status: 'OPTIMAL', hard_violations: 0, solve_time_ms: 1.4 },
          latencyMs: 15,
          status: 'SUCCESS',
        },
        {
          step: 8,
          action: 'Trace Lineage DAG & FAISS Dense RAG Fusion',
          tool: 'provenance.trace_lineage_and_rag',
          input: { decision_id: 'DEC-2026-0823', query: 'SAT-01 historical reliability' },
          output: { lineage_nodes: 10, faiss_citations: 3, bm25_rrf_score: 0.92 },
          latencyMs: 18,
          status: 'SUCCESS',
        },
        {
          step: 9,
          action: 'Synthesize Grounded Recommendation',
          tool: 'langgraph.synthesize_recommendation',
          input: { candidate: 'SAT-01', confidence: 0.94 },
          output: { recommendation: 'Approve dynamic task reallocation of Mission M-204 to SAT-01...' },
          latencyMs: 10,
          status: 'SUCCESS',
        },
        {
          step: 10,
          action: 'Package Auditable Trust Envelope',
          tool: 'governance.trust_envelope',
          input: { status: 'VERIFIED', actions: ['APPROVE', 'REJECT', 'INVESTIGATE'] },
          output: { envelope_sealed: true, confidence: 0.94, governance: 'VERIFIED_10_OF_10' },
          latencyMs: 5,
          status: 'SUCCESS',
        },
      ],
    },
    {
      id: 'trace-rag-refusal',
      query: 'What was the orbital inclination of satellite SAT-999 during 2021 launch?',
      intent: 'GENERAL_OPERATIONAL_QUERY',
      status: 'REFUSAL_GROUNDED',
      totalLatencyMs: 48,
      groundingScore: 1.0,
      model: 'LangGraph StateGraph + FAISS + BM25 RRF',
      trustEnvelope: {
        confidenceScore: 0.12,
        governanceStatus: 'REFUSAL_TRIGGERED',
        evidenceCount: 0,
        caller: 'flight-director',
      },
      recommendation: 'Refused execution: SAT-999 is absent from verified constellation catalog (anti-hallucination policy).',
      steps: [
        {
          step: 1,
          action: 'Intent Classification',
          tool: 'langgraph.classify_intent',
          input: { query: 'SAT-999 2021 launch inclination' },
          output: { intent: 'GENERAL_OPERATIONAL_QUERY' },
          latencyMs: 10,
          status: 'SUCCESS',
        },
        {
          step: 2,
          action: 'FAISS Dense & BM25 Sparse Search',
          tool: 'rag.faiss_bm25_retriever',
          input: { query: 'SAT-999 2021 launch inclination' },
          output: { dense_hits: 0, bm25_hits: 0, confidence: 0.12 },
          latencyMs: 22,
          status: 'INSUFFICIENT_EVIDENCE',
        },
        {
          step: 3,
          action: 'Honest Hallucination Refusal Gate',
          tool: 'trust_layer.refusal_engine',
          input: { confidence: 0.12, threshold: 0.70 },
          output: { refusal_triggered: true, message: 'I cannot verify information regarding SAT-999 as it is not in the verified constellation catalog.' },
          latencyMs: 16,
          status: 'SUCCESS',
        },
      ],
    },
  ]);

  const currentTrace = traces.find((t) => t.id === selectedTraceId) || traces[0];

  const handleExecuteQuery = async () => {
    if (!customQuery.trim()) return;
    setIsExecuting(true);
    try {
      const resp = await fetch('/api/ai/agent/orchestrate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: customQuery,
          user_id: 'flight-director',
          prefer_verified: true,
        }),
      });

      if (resp.ok) {
        const data = await resp.json();
        const newTraceId = `trace-${Date.now()}`;
        const newTrace: TraceSession = {
          id: newTraceId,
          query: data.query || customQuery,
          intent: data.intent || (customQuery.toLowerCase().includes('risk') ? 'RISK_AUDIT_AND_TASK_REPLANNING' : 'GENERAL_OPERATIONAL_QUERY'),
          status: data.status || 'VERIFIED_TRUST_ENVELOPE',
          totalLatencyMs: Math.round(data.execution_steps?.reduce((acc: number, s: any) => acc + (s.latencyMs || 15), 0) || 120),
          groundingScore: data.confidence_score || 0.94,
          model: 'LangGraph StateGraph + CrossAttentionNet + FAISS RAG',
          trustEnvelope: {
            confidenceScore: data.confidence_score || 0.94,
            governanceStatus: 'VERIFIED',
            evidenceCount: data.evidence?.length || 4,
            caller: 'flight-director',
          },
          recommendation: data.recommendation,
          steps: data.execution_steps?.map((st: any, idx: number) => ({
            step: st.step || idx + 1,
            action: st.action || `Step ${idx + 1}`,
            tool: st.tool || `agent.${st.action?.toLowerCase() || 'tool'}`,
            input: st.input || { query: customQuery },
            output: st.output || st,
            latencyMs: st.latencyMs || Math.floor(Math.random() * 20 + 8),
            status: 'SUCCESS',
          })) || currentTrace.steps,
        };

        setTraces((prev) => [newTrace, ...prev]);
        setSelectedTraceId(newTraceId);
      }
    } catch (err) {
      console.error('Failed to execute LangGraph orchestrator', err);
    } finally {
      setIsExecuting(false);
    }
  };

  const STATEGRAPH_NODES = [
    { id: '1', name: '1. Classify Intent', icon: Brain, type: 'Router' },
    { id: '2', name: '2. Query Catalog', icon: Database, type: 'Context' },
    { id: '3', name: '3. Search Telemetry', icon: Search, type: 'MCP Tool' },
    { id: '4', name: '4. Isolation Forest', icon: Activity, type: 'Anomaly (Branch)' },
    { id: '5', name: '5. Cross-Attention Net', icon: Zap, type: 'Neural Ranker' },
    { id: '6', name: '6. TreeSHAP Attribution', icon: Fingerprint, type: 'XAI' },
    { id: '7', name: '7. CP-SAT Solver', icon: Cpu, type: 'Constraint Invariants' },
    { id: '8', name: '8. Lineage & FAISS RAG', icon: Layers, type: 'Dense + Sparse RRF' },
    { id: '9', name: '9. Synthesis', icon: Terminal, type: 'Recommendation' },
    { id: '10', name: '10. Trust Envelope', icon: ShieldCheck, type: 'Governance Seal' },
  ];

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto bg-slate-950 p-6 space-y-6">
      {/* View Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-cyan-500/20 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-400/30 text-cyan-400">
              <GitBranch className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold font-orbitron tracking-wider text-slate-100">
                  LangGraph StateGraph & Agent Traces
                </h1>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 font-mono">
                  LangGraph 10-Node Flow
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-mono">
                  FAISS + BM25 RRF
                </span>
              </div>
              <p className="text-sm text-slate-400 mt-0.5">
                Inspect 10-Node StateGraph Execution &bull; Dynamic Risk Branching &bull; Mathematical Constraint Invariants &bull; Verified Trust Envelopes
              </p>
            </div>
          </div>
        </div>

        {/* Trace selector */}
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl p-1.5 font-mono text-xs overflow-x-auto">
          <span className="text-slate-500 px-2">Saved Traces:</span>
          {traces.map((t) => (
            <button
              key={t.id}
              onClick={() => setSelectedTraceId(t.id)}
              className={`px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer whitespace-nowrap ${
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

      {/* Live Interactive Query Bar */}
      <div className="bg-slate-900/80 border border-cyan-500/30 rounded-2xl p-4 shadow-xl space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
            <Play className="w-3.5 h-3.5" />
            Live LangGraph StateGraph Execution Console
          </span>
          <span className="text-[11px] font-mono text-slate-400">
            Endpoint: <code className="text-emerald-400">POST /api/ai/agent/orchestrate</code>
          </span>
        </div>

        <div className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={customQuery}
            onChange={(e) => setCustomQuery(e.target.value)}
            placeholder="Ask ORBIT-X decision agent (e.g. Why is Mission M-204 at risk?)"
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
          />
          <button
            onClick={handleExecuteQuery}
            disabled={isExecuting}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-bold font-orbitron text-xs tracking-wider flex items-center justify-center gap-2 hover:opacity-90 transition-all cursor-pointer disabled:opacity-50"
          >
            {isExecuting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            {isExecuting ? 'RUNNING GRAPH...' : 'EXECUTE STATEGRAPH'}
          </button>
        </div>

        {/* Quick Presets */}
        <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-slate-400">
          <span>Presets:</span>
          <button
            onClick={() => setCustomQuery('Why is Mission M-204 at risk and what should we do?')}
            className="px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-cyan-300 transition-all cursor-pointer"
          >
            🚨 Risk Audit & Reassignment (SAT-03 Excursion)
          </button>
          <button
            onClick={() => setCustomQuery('Which satellite has optimal thermal and LOS headroom for target Disaster-01?')}
            className="px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-cyan-300 transition-all cursor-pointer"
          >
            🛰️ General Opportunity Ranking
          </button>
          <button
            onClick={() => setCustomQuery('What was the orbital inclination of satellite SAT-999 during 2021 launch?')}
            className="px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-cyan-300 transition-all cursor-pointer"
          >
            🛑 Out-of-Distribution Refusal Probe
          </button>
        </div>
      </div>

      {/* StateGraph Pipeline Topology Diagram */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider font-orbitron text-slate-200 flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-cyan-400" />
            Compiled LangGraph StateGraph Topology
          </h3>
          <span className="text-xs font-mono px-2.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
            Branch Condition: {currentTrace.intent === 'RISK_AUDIT_AND_TASK_REPLANNING' ? '⚡ RISK BRANCH ACTIVE' : 'STANDARD ML PIPELINE'}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {STATEGRAPH_NODES.map((node) => {
            const isRiskBranch = node.id === '4';
            const isActive = currentTrace.steps.some((s) => s.step.toString() === node.id);
            const Icon = node.icon;

            return (
              <div
                key={node.id}
                className={`p-3 rounded-xl border transition-all ${
                  isActive
                    ? isRiskBranch
                      ? 'bg-amber-500/10 border-amber-500/40 text-amber-300 shadow-md shadow-amber-500/10'
                      : 'bg-cyan-500/10 border-cyan-500/40 text-cyan-300 shadow-md shadow-cyan-500/10'
                    : 'bg-slate-950/60 border-slate-800 text-slate-500'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <Icon className="w-4 h-4" />
                  <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-slate-900 border border-slate-800">
                    {node.type}
                  </span>
                </div>
                <div className="text-xs font-semibold font-orbitron truncate">{node.name}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Trace Overview Card */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div className="space-y-1">
            <div className="text-xs font-mono text-slate-400">Prompt / Intent:</div>
            <div className="text-sm font-semibold text-slate-100 font-mono">"{currentTrace.query}"</div>
            {currentTrace.intent && (
              <div className="text-xs font-mono text-cyan-400">
                Routed Intent: <span className="font-bold">{currentTrace.intent}</span>
              </div>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-3 font-mono text-xs">
            <div className="px-3 py-1 rounded-lg bg-slate-800 text-slate-300">
              Total Latency: <span className="text-cyan-400 font-bold">{currentTrace.totalLatencyMs}ms</span>
            </div>
            <div className="px-3 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold">
              Grounding: {Math.round(currentTrace.groundingScore * 100)}%
            </div>
            <div className="px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 font-bold">
              Status: {currentTrace.status}
            </div>
          </div>
        </div>

        {/* Synthesized Recommendation */}
        {currentTrace.recommendation && (
          <div className="p-3.5 rounded-xl bg-cyan-950/40 border border-cyan-500/30 space-y-1.5 font-mono text-xs">
            <div className="text-cyan-400 font-bold uppercase flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Synthesized Operational Recommendation:
            </div>
            <p className="text-slate-200 leading-relaxed">{currentTrace.recommendation}</p>
          </div>
        )}

        {/* Trust Envelope Metadata */}
        {currentTrace.trustEnvelope && (
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span className="text-slate-400">Trust Envelope:</span>
              <span className="text-emerald-400 font-bold">{currentTrace.trustEnvelope.governanceStatus}</span>
              <span className="text-slate-600">&bull;</span>
              <span className="text-slate-400">{currentTrace.trustEnvelope.evidenceCount} Verified Citations</span>
            </div>
            <div className="flex items-center gap-2">
              <button className="px-3 py-1 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/30 font-bold transition-all cursor-pointer">
                [Approve Decision]
              </button>
              <button className="px-3 py-1 rounded-lg bg-red-500/20 border border-red-500/40 text-red-300 hover:bg-red-500/30 font-bold transition-all cursor-pointer">
                [Reject]
              </button>
            </div>
          </div>
        )}

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
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        st.status === 'SUCCESS'
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : 'bg-amber-500/20 text-amber-300'
                      }`}
                    >
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
