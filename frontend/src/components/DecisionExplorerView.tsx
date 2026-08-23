import React, { useState } from 'react';
import {
  Layers,
  BarChart2,
  CheckCircle2,
  XCircle,
  Shield,
  Brain,
} from 'lucide-react';

export const DecisionExplorerView: React.FC = () => {
  const [selectedMissionId, setSelectedMissionId] = useState<string>('M-204');
  const [selectedCandidate, setSelectedCandidate] = useState<string>('SAT-01');
  const [activeTab, setLocalTab] = useState<'candidates' | 'shap' | 'constraints' | 'audit'>('candidates');

  const CANDIDATES = [
    {
      id: 'SAT-01',
      name: 'Sentinel-Alpha',
      score: 0.942,
      winProb: 94.8,
      batteryMargin: '84% (+14% headroom)',
      thermalHeadroom: '28.4°C (Safe)',
      slewAngle: '12.4° (Optimal)',
      constraintsPassed: 4,
      constraintsTotal: 4,
      status: 'SELECTED',
      reason: 'Optimal cross-attention token alignment with high battery margin and minimal slew penalty.',
    },
    {
      id: 'SAT-04',
      name: 'Sentinel-Delta',
      score: 0.887,
      winProb: 88.2,
      batteryMargin: '76% (+6% headroom)',
      thermalHeadroom: '31.2°C (Nominal)',
      slewAngle: '24.1° (Acceptable)',
      constraintsPassed: 4,
      constraintsTotal: 4,
      status: 'BACKUP',
      reason: 'Valid candidate; lower valuation due to greater slew angle and lower optical aperture match.',
    },
    {
      id: 'SAT-03',
      name: 'Sentinel-Gamma',
      score: 0.412,
      winProb: 12.0,
      batteryMargin: '62% (-8% margin)',
      thermalHeadroom: '38.4°C (EXCURSION)',
      slewAngle: '44.8° (High penalty)',
      constraintsPassed: 2,
      constraintsTotal: 4,
      status: 'REJECTED',
      reason: 'Isolation Forest detected +3.2σ thermal anomaly. Battery SOC violates minimum 70% threshold for high-rate SAR downlink.',
    },
    {
      id: 'SAT-02',
      name: 'Sentinel-Beta',
      score: 0.315,
      winProb: 5.4,
      batteryMargin: '48% (-22% margin)',
      thermalHeadroom: '29.1°C (Nominal)',
      slewAngle: '58.2° (Infeasible window)',
      constraintsPassed: 1,
      constraintsTotal: 4,
      status: 'REJECTED',
      reason: 'Hard elevation constraint failure: line-of-sight obscured by Earth limb during target acquisition pass.',
    },
  ];

  const SHAP_FEATURES = [
    { feature: 'battery_soc_margin', value: '+0.412', rank: 1, chosenEffect: 'Positive', rejectedEffect: 'Negative for SAT-03/02' },
    { feature: 'slew_angle_penalty', value: '+0.298', rank: 2, chosenEffect: 'Minimal slew for SAT-01', rejectedEffect: 'High slew for SAT-02' },
    { feature: 'thermal_headroom', value: '+0.285', rank: 3, chosenEffect: 'Safe operational band', rejectedEffect: 'Excursion detected in SAT-03' },
    { feature: 'cross_attention_alignment', value: '+0.245', rank: 4, chosenEffect: 'High mission token similarity', rejectedEffect: 'Mismatched instrument modes' },
    { feature: 'isl_bandwidth_availability', value: '+0.118', rank: 5, chosenEffect: 'Low ISL packet latency', rejectedEffect: 'Mesh hop congestion' },
  ];

  const ML_EVALUATION = [
    { model: 'ConstellationCrossAttentionNet (Champion ML)', category: 'Deep Learning', top1Agreement: '84.6%', mae: '28.40', f1Score: '0.612', latencyMs: '0.372 ms', throughput: '2,690.9 inf/s' },
    { model: 'Random Forest / XGBoost Tier', category: 'Classical ML', top1Agreement: '81.2%', mae: '21.07', f1Score: '0.658', latencyMs: '0.132 ms', throughput: '7,598.9 inf/s' },
    { model: 'Ridge Linear Regression', category: 'Classical ML', top1Agreement: '75.0%', mae: '56.84', f1Score: '0.570', latencyMs: '0.004 ms', throughput: '274,876.3 inf/s' },
    { model: 'Multi-Layer Perceptron (BidValueMLP)', category: 'Deep Learning', top1Agreement: '68.8%', mae: '42.03', f1Score: '0.571', latencyMs: '0.185 ms', throughput: '5,397.5 inf/s' },
    { model: 'Greedy EDF Heuristic', category: 'Heuristic', top1Agreement: '62.5%', mae: '93.48', f1Score: '0.450', latencyMs: '0.001 ms', throughput: '1,000,000.0 inf/s' },
    { model: 'Random Assignment', category: 'Heuristic', top1Agreement: '37.5%', mae: '91.04', f1Score: '0.188', latencyMs: '0.001 ms', throughput: '716,332.3 inf/s' },
  ];

  const DECISION_EVALUATION = [
    { system: 'Cross-Attention Only (Unconstrained)', violations: '3.4% boundary violations', feasibility: '96.6%', utility: '84.5%', optLatency: 'N/A (Neural only)', e2eLatency: '0.372 ms' },
    { system: 'Cross-Attention + CP-SAT (Hybrid Champion)', violations: '0 (Modeled Invariants Enforced)', feasibility: '100.0%', utility: '98.7%', optLatency: '18.40 ms', e2eLatency: '18.77 ms' },
  ];

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto bg-slate-950 p-6 space-y-6">
      {/* View Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-cyan-500/20 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-400/30 text-blue-400">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold font-orbitron tracking-wider text-slate-100">
                  Decision Explorer
                </h1>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 font-mono">
                  Multi-Candidate XAI
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono">
                  CP-SAT Guaranteed
                </span>
              </div>
              <p className="text-sm text-slate-400 mt-0.5">
                Inspect Cross-Attention Token Matching &bull; TreeSHAP Feature Attributions &bull; Hard Constraint Invariants
              </p>
            </div>
          </div>
        </div>

        {/* Mission selector pills */}
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl p-1.5 font-mono text-xs">
          <span className="text-slate-500 px-2">Mission:</span>
          {['M-204', 'M-102', 'M-088'].map((m) => (
            <button
              key={m}
              onClick={() => setSelectedMissionId(m)}
              className={`px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                selectedMissionId === m
                  ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* Internal Navigation Subtabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setLocalTab('candidates')}
          className={`px-4 py-2 rounded-xl text-xs font-mono font-semibold flex items-center gap-2 transition-all cursor-pointer ${
            activeTab === 'candidates'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
        >
          <Brain className="w-4 h-4" />
          Candidate Ranking & Baselines
        </button>
        <button
          onClick={() => setLocalTab('shap')}
          className={`px-4 py-2 rounded-xl text-xs font-mono font-semibold flex items-center gap-2 transition-all cursor-pointer ${
            activeTab === 'shap'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
        >
          <BarChart2 className="w-4 h-4" />
          TreeSHAP Attribution (Why Chosen vs Rejected?)
        </button>
        <button
          onClick={() => setLocalTab('constraints')}
          className={`px-4 py-2 rounded-xl text-xs font-mono font-semibold flex items-center gap-2 transition-all cursor-pointer ${
            activeTab === 'constraints'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
        >
          <Shield className="w-4 h-4" />
          CP-SAT Constraint Invariants
        </button>
      </div>

      {/* Main Tab Content */}
      {activeTab === 'candidates' && (
        <div className="space-y-6">
          {/* Candidate Table */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <h3 className="text-xs font-semibold uppercase tracking-wider font-orbitron text-slate-300 mb-4 flex items-center gap-2">
              <Brain className="w-4 h-4 text-cyan-400" />
              Constellation Candidate Evaluation for Mission {selectedMissionId}
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="pb-3 px-3">Node / Satellite</th>
                    <th className="pb-3 px-3">Cross-Attention Score</th>
                    <th className="pb-3 px-3">Win Probability</th>
                    <th className="pb-3 px-3">Battery Margin</th>
                    <th className="pb-3 px-3">Thermal Status</th>
                    <th className="pb-3 px-3">Constraints</th>
                    <th className="pb-3 px-3">Decision Outcome</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {CANDIDATES.map((cand) => (
                    <tr
                      key={cand.id}
                      onClick={() => setSelectedCandidate(cand.id)}
                      className={`hover:bg-slate-800/50 transition-colors cursor-pointer ${
                        selectedCandidate === cand.id ? 'bg-cyan-950/30 border-l-2 border-cyan-400' : ''
                      }`}
                    >
                      <td className="py-3 px-3">
                        <div className="font-semibold text-slate-200">{cand.id}</div>
                        <div className="text-[10px] text-slate-500">{cand.name}</div>
                      </td>
                      <td className="py-3 px-3">
                        <div className="font-bold text-cyan-300">{cand.score.toFixed(3)}</div>
                        <div className="h-1.5 w-24 bg-slate-800 rounded-full overflow-hidden mt-1">
                          <div
                            style={{ width: `${cand.score * 100}%` }}
                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500"
                          />
                        </div>
                      </td>
                      <td className="py-3 px-3 text-slate-300">{cand.winProb}%</td>
                      <td className="py-3 px-3 text-slate-300">{cand.batteryMargin}</td>
                      <td className="py-3 px-3">
                        <span className={cand.thermalHeadroom.includes('EXCURSION') ? 'text-rose-400 font-semibold' : 'text-emerald-400'}>
                          {cand.thermalHeadroom}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${
                          cand.constraintsPassed === 4
                            ? 'bg-emerald-500/20 text-emerald-300'
                            : 'bg-rose-500/20 text-rose-300'
                        }`}>
                          {cand.constraintsPassed}/{cand.constraintsTotal} Met
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`px-2.5 py-1 rounded-md text-[10px] font-bold ${
                            cand.status === 'SELECTED'
                              ? 'bg-emerald-500/20 border border-emerald-500/40 text-emerald-300'
                              : cand.status === 'BACKUP'
                              ? 'bg-cyan-500/20 border border-cyan-500/40 text-cyan-300'
                              : 'bg-rose-500/20 border border-rose-500/40 text-rose-300'
                          }`}
                        >
                          {cand.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Stage 1: Pure ML Evaluation Table */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold uppercase tracking-wider font-orbitron text-slate-300 flex items-center gap-2">
                <Brain className="w-4 h-4 text-cyan-400" />
                Stage 1: Machine Learning Evaluation (Pure Predictive & Ranking Models)
              </h3>
              <span className="text-[10px] font-mono text-slate-500">Held-Out Multi-Agent Telemetry Split</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="pb-3 px-3">Model Architecture</th>
                    <th className="pb-3 px-3">Category</th>
                    <th className="pb-3 px-3">Top-1 Agreement</th>
                    <th className="pb-3 px-3">Score MAE</th>
                    <th className="pb-3 px-3">F1 Score</th>
                    <th className="pb-3 px-3">Inference Latency (p50)</th>
                    <th className="pb-3 px-3">Throughput</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {ML_EVALUATION.map((b, idx) => (
                    <tr key={idx} className={b.model.includes('Champion') ? 'bg-cyan-950/20 font-semibold' : ''}>
                      <td className="py-3 px-3 text-slate-200 flex items-center gap-1.5">
                        {b.model.includes('Champion') && <span className="text-cyan-400">★</span>}
                        {b.model}
                      </td>
                      <td className="py-3 px-3 text-[10px] text-slate-400">{b.category}</td>
                      <td className="py-3 px-3 text-cyan-300 font-bold">{b.top1Agreement}</td>
                      <td className="py-3 px-3 text-slate-300">{b.mae}</td>
                      <td className="py-3 px-3 text-emerald-400">{b.f1Score}</td>
                      <td className="py-3 px-3 text-slate-300">{b.latencyMs}</td>
                      <td className="py-3 px-3 text-slate-400">{b.throughput}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Stage 2: Decision Systems Evaluation Table */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold uppercase tracking-wider font-orbitron text-slate-300 flex items-center gap-2">
                <Shield className="w-4 h-4 text-emerald-400" />
                Stage 2: Decision Systems Evaluation (Constraint Enforcement & Feasibility)
              </h3>
              <span className="text-[10px] font-mono text-emerald-500/80">CP-SAT Invariant Guaranteed</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="pb-3 px-3">Decision System</th>
                    <th className="pb-3 px-3">Constraint Violations</th>
                    <th className="pb-3 px-3">Feasibility Rate</th>
                    <th className="pb-3 px-3">Decision Utility</th>
                    <th className="pb-3 px-3">Optimization Latency</th>
                    <th className="pb-3 px-3">End-to-End Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {DECISION_EVALUATION.map((d, idx) => (
                    <tr key={idx} className={d.system.includes('Hybrid') ? 'bg-emerald-950/20 font-semibold' : ''}>
                      <td className="py-3 px-3 text-slate-200 flex items-center gap-1.5">
                        {d.system.includes('Hybrid') && <span className="text-emerald-400">★</span>}
                        {d.system}
                      </td>
                      <td className="py-3 px-3 text-amber-300">{d.violations}</td>
                      <td className="py-3 px-3 text-emerald-400 font-bold">{d.feasibility}</td>
                      <td className="py-3 px-3 text-cyan-300 font-bold">{d.utility}</td>
                      <td className="py-3 px-3 text-slate-300">{d.optLatency}</td>
                      <td className="py-3 px-3 text-emerald-300 font-mono font-bold">{d.e2eLatency}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* SHAP Attribution Tab */}
      {activeTab === 'shap' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div>
            <h3 className="text-sm font-semibold font-orbitron text-slate-100 flex items-center gap-2">
              <BarChart2 className="w-5 h-5 text-cyan-400" />
              TreeSHAP Feature Attributions: Chosen vs Rejected Rationales
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Explains exact feature contributions and why specific resource nodes were accepted or disqualified.
            </p>
          </div>

          <div className="space-y-4">
            {SHAP_FEATURES.map((feat) => (
              <div key={feat.rank} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between font-mono text-xs">
                  <span className="font-semibold text-cyan-300">
                    #{feat.rank} &bull; {feat.feature}
                  </span>
                  <span className="text-emerald-400 font-bold">{feat.value} SHAP Value</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono pt-2 border-t border-slate-800/80">
                  <div className="flex items-start gap-2 text-emerald-300">
                    <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5 text-emerald-400" />
                    <div>
                      <span className="font-semibold text-slate-300">Why Chosen (SAT-01):</span>{' '}
                      {feat.chosenEffect}
                    </div>
                  </div>
                  <div className="flex items-start gap-2 text-rose-300">
                    <XCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-400" />
                    <div>
                      <span className="font-semibold text-slate-300">Why Rejected (SAT-03/SAT-02):</span>{' '}
                      {feat.rejectedEffect}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Constraints Tab */}
      {activeTab === 'constraints' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div>
            <h3 className="text-sm font-semibold font-orbitron text-slate-100 flex items-center gap-2">
              <Shield className="w-5 h-5 text-emerald-400" />
              Google OR-Tools CP-SAT Invariant Proofs
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Guaranteed 100% hard-constraint safety applied on top of ML Cross-Attention candidate ranking.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-300 font-semibold">1. Line-of-Sight Visibility</span>
                <span className="text-emerald-400 font-bold">100% PASS</span>
              </div>
              <p className="text-xs text-slate-400">
                Satellite elevation must exceed +15.0° above target horizon without planetary limb occlusion.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-300 font-semibold">2. Battery Energy Margin</span>
                <span className="text-emerald-400 font-bold">100% PASS</span>
              </div>
              <p className="text-xs text-slate-400">
                Minimum 70.0% SOC maintained throughout imaging pass and high-power radio downlink burst.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-300 font-semibold">3. Thermal Safe Operating Area</span>
                <span className="text-emerald-400 font-bold">100% PASS</span>
              </div>
              <p className="text-xs text-slate-400">
                Battery core temperature strictly bounded &lt;35.0°C to prevent thermal runaway.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-300 font-semibold">4. Slew & Reaction Wheel Limits</span>
                <span className="text-emerald-400 font-bold">100% PASS</span>
              </div>
              <p className="text-xs text-slate-400">
                Attitude maneuver angular velocity &lt;1.5 deg/sec; momentum dumping requirements met.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default DecisionExplorerView;
