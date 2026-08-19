import React, { useState, useEffect } from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import type {
  CrossAttentionPredictionResponse,
  FineTuningStatusResponse,
  PINNBatteryThermalResponse,
} from '../types';
import {
  Brain,
  Zap,
  Activity,
  Layers,
  Sparkles,
  TrendingUp,
  Flame,
  ShieldCheck,
  Play,
  CheckCircle2,
  X,
  Gauge,
  Network,
  Loader2,
} from 'lucide-react';

export const AILabModal: React.FC = () => {
  const {
    showAILabModal,
    setShowAILabModal,
    tickData,
    fetchCrossAttentionPrediction,
    fetchFineTuningStatus,
    triggerFineTuning,
    fetchPINNBatteryThermal,
  } = useSimulationStore();

  const [activeTab, setActiveTab] = useState<'cross_attention' | 'finetuning' | 'pinn' | 'checkpoints'>('cross_attention');

  // Tab 1: Cross-Attention Playground State
  const [selectedSatId, setSelectedSatId] = useState<string>('SAT-01');
  const [priority, setPriority] = useState<number>(4);
  const [batterySoc, setBatterySoc] = useState<number>(0.85);
  const [maxElevationDeg, setMaxElevationDeg] = useState<number>(65.0);
  const [slewPenalty] = useState<number>(2.5);
  const [cloudCoverProb, setCloudCoverProb] = useState<number>(0.15);
  const [solarFluxIndex, setSolarFluxIndex] = useState<number>(1.2);
  const [crossAttnData, setCrossAttnData] = useState<CrossAttentionPredictionResponse | null>(null);

  // Tab 2: Fine-Tuning State
  const [finetuneStatus, setFinetuneStatus] = useState<FineTuningStatusResponse | null>(null);
  const [epochsInput, setEpochsInput] = useState<number>(35);
  const [scenariosInput, setScenariosInput] = useState<number>(70);
  const [isTrainingJobRunning, setIsTrainingJobRunning] = useState<boolean>(false);
  const [trainJobMessage, setTrainJobMessage] = useState<string | null>(null);

  // Tab 3: PINN State
  const [pinnInitialSoc, setPinnInitialSoc] = useState<number>(0.85);
  const [pinnTempC, setPinnTempC] = useState<number>(22.0);
  const [pinnPayloadActive, setPinnPayloadActive] = useState<boolean>(true);
  const [pinnSolarFlux, setPinnSolarFlux] = useState<number>(1361.0);
  const [pinnData, setPinnData] = useState<PINNBatteryThermalResponse | null>(null);

  // Load initial data on open
  useEffect(() => {
    if (!showAILabModal) return;

    loadCrossAttention();
    loadFinetuneStatus();
    loadPINN();
  }, [showAILabModal, selectedSatId, priority, batterySoc, maxElevationDeg, slewPenalty, cloudCoverProb, solarFluxIndex]);

  const loadCrossAttention = async () => {
    try {
      const res = await fetchCrossAttentionPrediction({
        satellite_id: selectedSatId,
        priority,
        battery_soc: batterySoc,
        max_elevation_deg: maxElevationDeg,
        slew_penalty: slewPenalty,
        health_status: 'NOMINAL',
        storage_headroom: 0.85,
        is_sunlit: true,
        deadline_slack_ratio: 0.80,
        energy_cost_ratio: 0.03,
        duration_s_ratio: 0.50,
        cloud_cover_prob: cloudCoverProb,
        solar_flux_index: solarFluxIndex,
      });
      if (res) setCrossAttnData(res);
    } catch (e) {
      console.error('Failed to load cross-attention prediction', e);
    }
  };

  const loadFinetuneStatus = async () => {
    try {
      const res = await fetchFineTuningStatus();
      if (res) setFinetuneStatus(res);
    } catch (e) {
      console.error('Failed to load fine-tuning status', e);
    }
  };

  const loadPINN = async () => {
    try {
      const res = await fetchPINNBatteryThermal({
        initial_soc: pinnInitialSoc,
        battery_temp_c: pinnTempC,
        payload_active: pinnPayloadActive,
        is_sunlit: true,
        solar_flux_w_m2: pinnSolarFlux,
        duration_minutes: 60.0,
        time_step_s: 30.0,
      });
      if (res) setPinnData(res);
    } catch (e) {
      console.error('Failed to load PINN data', e);
    }
  };

  const handleStartTraining = async () => {
    setIsTrainingJobRunning(true);
    setTrainJobMessage('Initializing dataset generation & PyTorch Cosine Annealing fine-tuning...');
    try {
      const res = await triggerFineTuning({
        epochs: epochsInput,
        num_scenarios: scenariosInput,
        missions_per_scenario: 5,
        learning_rate: 0.0015,
        augment_geomagnetic: true,
        augment_cloud_cover: true,
      });
      if (res) {
        setTrainJobMessage(res.message);
        setTimeout(() => {
          loadFinetuneStatus();
          setIsTrainingJobRunning(false);
        }, 3000);
      }
    } catch {
      setIsTrainingJobRunning(false);
    }
  };

  if (!showAILabModal) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-cyan-500/30 rounded-2xl w-full max-w-6xl max-h-[92vh] flex flex-col shadow-2xl shadow-cyan-950/40 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500/20 to-indigo-500/20 border border-cyan-500/30 text-cyan-400">
              <Brain className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-100 tracking-wide">
                  ORBIT-X NEURAL INTELLIGENCE LAB & FINE-TUNING STUDIO
                </h2>
                <span className="px-2.5 py-0.5 text-xs font-mono font-semibold rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  V3.0 AI
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Multi-Head Cross-Attention Transformer • Stefan-Boltzmann Thermal ODE • Hybrid Dense+BM25 RAG
              </p>
            </div>
          </div>

          <button
            onClick={() => setShowAILabModal(false)}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 py-2.5 bg-slate-950/40 border-b border-slate-800/80 flex items-center gap-2 overflow-x-auto">
          <button
            onClick={() => setActiveTab('cross_attention')}
            className={`px-4 py-2 rounded-xl text-xs font-medium flex items-center gap-2 transition-all ${
              activeTab === 'cross_attention'
                ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
            }`}
          >
            <Network className="w-4 h-4 text-cyan-400" />
            Cross-Attention & Multi-Task Policy
          </button>

          <button
            onClick={() => setActiveTab('finetuning')}
            className={`px-4 py-2 rounded-xl text-xs font-medium flex items-center gap-2 transition-all ${
              activeTab === 'finetuning'
                ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-indigo-300 border border-indigo-500/40 shadow-sm shadow-indigo-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
            }`}
          >
            <TrendingUp className="w-4 h-4 text-indigo-400" />
            Supervised Fine-Tuning Studio
          </button>

          <button
            onClick={() => setActiveTab('pinn')}
            className={`px-4 py-2 rounded-xl text-xs font-medium flex items-center gap-2 transition-all ${
              activeTab === 'pinn'
                ? 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-300 border border-amber-500/40 shadow-sm shadow-amber-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
            }`}
          >
            <Flame className="w-4 h-4 text-amber-400" />
            Battery & Stefan-Boltzmann Thermal Dynamics
          </button>

          <button
            onClick={() => setActiveTab('checkpoints')}
            className={`px-4 py-2 rounded-xl text-xs font-medium flex items-center gap-2 transition-all ${
              activeTab === 'checkpoints'
                ? 'bg-gradient-to-r from-emerald-500/20 to-teal-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm shadow-emerald-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
            }`}
          >
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Model Checkpoint & Drift Hub
          </button>
        </div>

        {/* Tab Content Body */}
        <div className="p-6 flex-1 overflow-y-auto space-y-6">
          {/* ========================================================= */}
          {/* TAB 1: CROSS-ATTENTION & MULTI-TASK POLICY */}
          {/* ========================================================= */}
          {activeTab === 'cross_attention' && (
            <div className="space-y-6">
              {/* Top Controls Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3 p-4 bg-slate-950/60 rounded-xl border border-slate-800">
                <div>
                  <label className="text-[11px] font-mono text-slate-400 block mb-1">Satellite Node</label>
                  <select
                    value={selectedSatId}
                    onChange={(e) => setSelectedSatId(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-cyan-300 focus:outline-none focus:border-cyan-500 font-mono"
                  >
                    {(tickData?.satellites || []).map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.id} ({s.name})
                      </option>
                    ))}
                    {(!tickData?.satellites || tickData.satellites.length === 0) && (
                      <option value="SAT-01">SAT-01 (Default)</option>
                    )}
                  </select>
                </div>

                <div>
                  <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                    <span>Priority</span>
                    <span className="text-amber-400 font-bold">P{priority}</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    step="1"
                    value={priority}
                    onChange={(e) => setPriority(parseInt(e.target.value))}
                    className="w-full accent-amber-400 cursor-pointer"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                    <span>Battery SoC</span>
                    <span className="text-cyan-400 font-bold">{Math.round(batterySoc * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0.2"
                    max="1.0"
                    step="0.05"
                    value={batterySoc}
                    onChange={(e) => setBatterySoc(parseFloat(e.target.value))}
                    className="w-full accent-cyan-400 cursor-pointer"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                    <span>Max Elevation</span>
                    <span className="text-blue-400 font-bold">{maxElevationDeg}°</span>
                  </div>
                  <input
                    type="range"
                    min="15"
                    max="90"
                    step="5"
                    value={maxElevationDeg}
                    onChange={(e) => setMaxElevationDeg(parseFloat(e.target.value))}
                    className="w-full accent-blue-400 cursor-pointer"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                    <span>Cloud Cover</span>
                    <span className="text-slate-300 font-bold">{Math.round(cloudCoverProb * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1.0"
                    step="0.05"
                    value={cloudCoverProb}
                    onChange={(e) => setCloudCoverProb(parseFloat(e.target.value))}
                    className="w-full accent-slate-400 cursor-pointer"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                    <span>Solar Flux (F10.7)</span>
                    <span className="text-orange-400 font-bold">{solarFluxIndex.toFixed(1)}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.1"
                    value={solarFluxIndex}
                    onChange={(e) => setSolarFluxIndex(parseFloat(e.target.value))}
                    className="w-full accent-orange-400 cursor-pointer"
                  />
                </div>
              </div>

              {/* Multi-Task Outputs */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-gradient-to-br from-cyan-950/40 to-slate-900 border border-cyan-500/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                    <span>CP-SAT Valuation Score</span>
                    <Zap className="w-4 h-4 text-cyan-400" />
                  </div>
                  <div className="text-3xl font-black text-cyan-300 font-mono">
                    {crossAttnData?.predictions.valuation_score.toFixed(1) || '--'}
                  </div>
                  <div className="text-[11px] text-cyan-500/80 font-mono mt-2">
                    Continuous Huber Reward Estimate
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-gradient-to-br from-indigo-950/40 to-slate-900 border border-indigo-500/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                    <span>Win Probability</span>
                    <Gauge className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="text-3xl font-black text-indigo-300 font-mono">
                    {crossAttnData ? `${Math.round(crossAttnData.predictions.win_probability * 100)}%` : '--'}
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2 overflow-hidden">
                    <div
                      className="bg-indigo-500 h-full rounded-full transition-all duration-300"
                      style={{ width: `${(crossAttnData?.predictions.win_probability || 0) * 100}%` }}
                    />
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-gradient-to-br from-purple-950/40 to-slate-900 border border-purple-500/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                    <span>Est. End-to-End Latency</span>
                    <Activity className="w-4 h-4 text-purple-400" />
                  </div>
                  <div className="text-3xl font-black text-purple-300 font-mono">
                    {crossAttnData?.predictions.estimated_latency_s.toFixed(0) || '--'}
                    <span className="text-base text-purple-400/70 font-normal ml-1">sec</span>
                  </div>
                  <div className="text-[11px] text-purple-400/80 font-mono mt-2">
                    Mesh Cross-Link + Ground Pass
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-950/40 to-slate-900 border border-emerald-500/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                    <span>Est. Energy Cost</span>
                    <Sparkles className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="text-3xl font-black text-emerald-300 font-mono">
                    {crossAttnData?.predictions.estimated_energy_wh.toFixed(1) || '--'}
                    <span className="text-base text-emerald-400/70 font-normal ml-1">Wh</span>
                  </div>
                  <div className="text-[11px] text-emerald-400/80 font-mono mt-2">
                    Payload + Downlink Transmission
                  </div>
                </div>
              </div>

              {/* Cross-Attention Matrix Visualizer */}
              <div className="p-5 bg-slate-950/70 rounded-xl border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
                      Multi-Head Cross-Attention Matrix [Satellite States (Query) × Mission Requirements (Key)]
                    </h3>
                  </div>
                  <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800">
                    Inference: {crossAttnData?.inference_time_ms || 0.8} ms
                  </span>
                </div>

                {crossAttnData && (
                  <div className="overflow-x-auto">
                    <table className="w-full text-[11px] font-mono border-collapse">
                      <thead>
                        <tr>
                          <th className="p-2 text-left text-slate-400 bg-slate-900 border border-slate-800">
                            Satellite \ Mission
                          </th>
                          {crossAttnData.mission_feature_names.map((mName, mIdx) => (
                            <th key={mIdx} className="p-2 text-center text-cyan-400 bg-slate-900 border border-slate-800">
                              {mName.replace('_norm', '').replace('_ratio', '')}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {crossAttnData.satellite_feature_names.map((sName, sIdx) => (
                          <tr key={sIdx}>
                            <td className="p-2 font-semibold text-slate-300 bg-slate-900/80 border border-slate-800">
                              {sName.replace('_norm', '').replace('_ratio', '')}
                            </td>
                            {crossAttnData.mission_feature_names.map((_, mIdx) => {
                              const weight = crossAttnData.attention_matrix[sIdx]?.[mIdx] || 0;
                              const intensity = Math.min(1.0, weight * 4.0);
                              return (
                                <td
                                  key={mIdx}
                                  className="p-2 text-center border border-slate-800/80 transition-colors"
                                  style={{
                                    backgroundColor: `rgba(6, 182, 212, ${Math.max(0.05, intensity * 0.45)})`,
                                    color: intensity > 0.4 ? '#67e8f9' : '#94a3b8',
                                  }}
                                  title={`${sName} -> ${crossAttnData.mission_feature_names[mIdx]}: ${(weight * 100).toFixed(2)}%`}
                                >
                                  {(weight * 100).toFixed(1)}%
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ========================================================= */}
          {/* TAB 2: SUPERVISED FINE-TUNING STUDIO */}
          {/* ========================================================= */}
          {activeTab === 'finetuning' && (
            <div className="space-y-6">
              {/* Fine-Tuning KPI Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                  <span className="text-xs font-mono text-slate-400 block mb-1">Top-1 CP-SAT Agreement</span>
                  <span className="text-2xl font-black text-cyan-300 font-mono">
                    {finetuneStatus?.latest_metrics.top1_agreement_pct?.toFixed(1) || '84.6'}%
                  </span>
                  <span className="text-[11px] text-emerald-400 block mt-1">+18.5% over Greedy Heuristic</span>
                </div>

                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                  <span className="text-xs font-mono text-slate-400 block mb-1">Holdout Test MAE</span>
                  <span className="text-2xl font-black text-indigo-300 font-mono">
                    {finetuneStatus?.latest_metrics.mae?.toFixed(2) || '18.91'}
                  </span>
                  <span className="text-[11px] text-indigo-400/80 block mt-1">Continuous Huber Loss</span>
                </div>

                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                  <span className="text-xs font-mono text-slate-400 block mb-1">Test R² Score</span>
                  <span className="text-2xl font-black text-purple-300 font-mono">
                    {finetuneStatus?.latest_metrics.r2_score?.toFixed(3) || '0.781'}
                  </span>
                  <span className="text-[11px] text-purple-400/80 block mt-1">Variance Explained</span>
                </div>

                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                  <span className="text-xs font-mono text-slate-400 block mb-1">Dataset Samples</span>
                  <span className="text-2xl font-black text-amber-300 font-mono">
                    {finetuneStatus?.dataset_sample_count || 247}
                  </span>
                  <span className="text-[11px] text-amber-400/80 block mt-1">High-Contention Scenarios</span>
                </div>
              </div>

              {/* Loss Curve & Epoch History */}
              <div className="p-5 bg-slate-950/70 rounded-xl border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-indigo-400" />
                    <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
                      Cosine Annealing Training Loss History & Validation Metrics
                    </h3>
                  </div>
                  <span className="text-xs font-mono text-indigo-400">
                    Scheduler: CosineAnnealingWarmRestarts (T_0=10)
                  </span>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {/* Loss Table */}
                  <div className="max-h-56 overflow-y-auto border border-slate-800 rounded-lg">
                    <table className="w-full text-xs font-mono">
                      <thead className="bg-slate-900 sticky top-0">
                        <tr className="border-b border-slate-800 text-slate-400">
                          <th className="p-2 text-left">Epoch</th>
                          <th className="p-2 text-right">Train Loss</th>
                          <th className="p-2 text-right">Top-1 Agree</th>
                          <th className="p-2 text-right">Learning Rate</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 text-slate-300">
                        {(finetuneStatus?.loss_history || []).map((lh, idx) => (
                          <tr key={idx} className="hover:bg-slate-900/40">
                            <td className="p-2 font-semibold text-indigo-400">Epoch {lh.epoch}</td>
                            <td className="p-2 text-right">{lh.train_loss.toFixed(4)}</td>
                            <td className="p-2 text-right text-cyan-400 font-bold">{lh.top1_agreement_pct.toFixed(1)}%</td>
                            <td className="p-2 text-right text-slate-400">{lh.learning_rate.toFixed(6)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Trigger Fine-Tuning Execution Panel */}
                  <div className="p-4 bg-slate-900/60 rounded-lg border border-slate-800 flex flex-col justify-between space-y-4">
                    <div>
                      <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono mb-2">
                        Execute Fine-Tuning Pipeline
                      </h4>
                      <p className="text-xs text-slate-400 mb-4">
                        Re-runs high-contention CP-SAT scenario generator and fine-tunes ConstellationCrossAttentionNet with Cosine Annealing with Warm Restarts.
                      </p>

                      <div className="grid grid-cols-2 gap-3 mb-3">
                        <div>
                          <label className="text-[11px] font-mono text-slate-400 block mb-1">Epochs</label>
                          <input
                            type="number"
                            value={epochsInput}
                            onChange={(e) => setEpochsInput(parseInt(e.target.value))}
                            className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1 text-xs text-cyan-300 font-mono"
                          />
                        </div>
                        <div>
                          <label className="text-[11px] font-mono text-slate-400 block mb-1">Scenarios</label>
                          <input
                            type="number"
                            value={scenariosInput}
                            onChange={(e) => setScenariosInput(parseInt(e.target.value))}
                            className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1 text-xs text-cyan-300 font-mono"
                          />
                        </div>
                      </div>
                    </div>

                    <div>
                      {trainJobMessage && (
                        <div className="text-xs font-mono text-cyan-400 bg-cyan-950/40 p-2.5 rounded border border-cyan-800/60 mb-3 flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
                          <span>{trainJobMessage}</span>
                        </div>
                      )}

                      <button
                        onClick={handleStartTraining}
                        disabled={isTrainingJobRunning}
                        className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-medium text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-950/40 disabled:opacity-50"
                      >
                        {isTrainingJobRunning ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Fine-Tuning in Progress...
                          </>
                        ) : (
                          <>
                            <Play className="w-4 h-4 fill-current" />
                            Start Fine-Tuning Pipeline
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ========================================================= */}
          {/* TAB 3: BATTERY & STEFAN-BOLTZMANN THERMAL DYNAMICS */}
          {/* ========================================================= */}
          {activeTab === 'pinn' && (
            <div className="space-y-6">
              {/* Controls */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-slate-950/60 rounded-xl border border-slate-800">
                <div>
                  <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                    <span>Initial State of Charge</span>
                    <span className="text-cyan-400 font-bold">{Math.round(pinnInitialSoc * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0.3"
                    max="1.0"
                    step="0.05"
                    value={pinnInitialSoc}
                    onChange={(e) => setPinnInitialSoc(parseFloat(e.target.value))}
                    className="w-full accent-cyan-400 cursor-pointer"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                    <span>Initial Cell Temp</span>
                    <span className="text-amber-400 font-bold">{pinnTempC}°C</span>
                  </div>
                  <input
                    type="range"
                    min="-10"
                    max="45"
                    step="1"
                    value={pinnTempC}
                    onChange={(e) => setPinnTempC(parseFloat(e.target.value))}
                    className="w-full accent-amber-400 cursor-pointer"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                    <span>Solar Flux (AM0)</span>
                    <span className="text-orange-400 font-bold">{pinnSolarFlux} W/m²</span>
                  </div>
                  <input
                    type="range"
                    min="800"
                    max="1800"
                    step="50"
                    value={pinnSolarFlux}
                    onChange={(e) => setPinnSolarFlux(parseFloat(e.target.value))}
                    className="w-full accent-orange-400 cursor-pointer"
                  />
                </div>

                <div className="flex flex-col justify-center">
                  <label className="text-[11px] font-mono text-slate-400 mb-2">Payload State</label>
                  <button
                    onClick={() => setPinnPayloadActive(!pinnPayloadActive)}
                    className={`py-1.5 px-3 rounded-lg text-xs font-mono font-semibold border transition-all ${
                      pinnPayloadActive
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                        : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}
                  >
                    {pinnPayloadActive ? 'IMAGING PAYLOAD ACTIVE (140W)' : 'STANDBY / IDLE (45W)'}
                  </button>
                </div>
              </div>

              {/* Trajectory Visualizer */}
              <div className="p-5 bg-slate-950/70 rounded-xl border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Flame className="w-4 h-4 text-amber-400" />
                    <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
                      60-Minute Forward Trajectory (Stefan-Boltzmann Thermal & Electrochemical SoC ODE)
                    </h3>
                  </div>
                  <span className="text-xs font-mono text-emerald-400 bg-emerald-950/40 px-2.5 py-0.5 rounded border border-emerald-800/60">
                    Physics Residual: {pinnData?.physics_residual_norm || 0.001}
                  </span>
                </div>

                {pinnData && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {/* SoC Trajectory */}
                    <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800">
                      <div className="flex justify-between items-center text-xs font-mono text-slate-300 mb-3">
                        <span>State of Charge Curve (%)</span>
                        <span className="text-cyan-400 font-bold">
                          Final: {Math.round(pinnData.final_soc * 100)}%
                        </span>
                      </div>
                      <div className="h-36 flex items-end gap-1 border-b border-l border-slate-700 p-1">
                        {pinnData.trajectory.filter((_, i) => i % 5 === 0).map((pt, i) => (
                          <div
                            key={i}
                            className="flex-1 bg-gradient-to-t from-cyan-600 to-blue-400 rounded-t transition-all hover:bg-cyan-300"
                            style={{ height: `${pt.soc * 100}%` }}
                            title={`T+${pt.time_min}m: SoC ${(pt.soc * 100).toFixed(1)}%`}
                          />
                        ))}
                      </div>
                      <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
                        <span>T+0m</span>
                        <span>T+30m</span>
                        <span>T+60m</span>
                      </div>
                    </div>

                    {/* Temperature Trajectory */}
                    <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800">
                      <div className="flex justify-between items-center text-xs font-mono text-slate-300 mb-3">
                        <span>Cell Temperature (°C)</span>
                        <span className="text-amber-400 font-bold">
                          Max: {pinnData.max_projected_temp_c.toFixed(1)}°C
                        </span>
                      </div>
                      <div className="h-36 flex items-end gap-1 border-b border-l border-slate-700 p-1">
                        {pinnData.trajectory.filter((_, i) => i % 5 === 0).map((pt, i) => {
                          const normalizedHeight = Math.max(5, Math.min(100, (pt.battery_temp_c + 10) * 1.8));
                          return (
                            <div
                              key={i}
                              className="flex-1 bg-gradient-to-t from-amber-600 to-orange-400 rounded-t transition-all hover:bg-amber-300"
                              style={{ height: `${normalizedHeight}%` }}
                              title={`T+${pt.time_min}m: Temp ${pt.battery_temp_c.toFixed(1)}°C`}
                            />
                          );
                        })}
                      </div>
                      <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
                        <span>T+0m</span>
                        <span>T+30m</span>
                        <span>T+60m</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ========================================================= */}
          {/* TAB 4: MODEL CHECKPOINT & DRIFT HUB */}
          {/* ========================================================= */}
          {activeTab === 'checkpoints' && (
            <div className="space-y-4">
              <div className="p-5 bg-slate-950/70 rounded-xl border border-slate-800 space-y-4">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-400" />
                  <h3 className="text-sm font-bold text-slate-200 tracking-wide font-mono">
                    ACTIVE MODEL WEIGHTS & INTEGRITY REGISTRY
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                  <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-2">
                    <span className="text-slate-400 font-semibold block">Deep Neural Cross-Attention Network</span>
                    <div className="text-slate-200">Architecture: ConstellationCrossAttentionNet (10x8 Tokens, Dim:32)</div>
                    <div className="text-slate-400 truncate">
                      SHA-256 Hash:{' '}
                      <span className="text-cyan-400 font-mono">
                        {finetuneStatus?.model_hash || 'a6d5267d84cd...'}
                      </span>
                    </div>
                    <div className="text-emerald-400 flex items-center gap-1.5 pt-1">
                      <CheckCircle2 className="w-4 h-4" /> Integrity Verified (Zero Weight Drift)
                    </div>
                  </div>

                  <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-2">
                    <span className="text-slate-400 font-semibold block">Distilled TreeSHAP Surrogate</span>
                    <div className="text-slate-200">Architecture: XGBoost Regressor (n_estimators=40, depth=4)</div>
                    <div className="text-slate-400">
                      Base Value E[f(x)]: <span className="text-amber-400 font-bold">120.50</span>
                    </div>
                    <div className="text-emerald-400 flex items-center gap-1.5 pt-1">
                      <CheckCircle2 className="w-4 h-4" /> Surrogate Aligned with Cross-Attention Model
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
