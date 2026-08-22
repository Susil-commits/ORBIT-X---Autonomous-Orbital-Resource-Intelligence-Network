import React, { useState } from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import {
  Play,
  Pause,
  FastForward,
  RotateCcw,
  BarChart3,
  Zap,
  ShieldAlert,
  Wifi,
  WifiOff,
  Network,
  Target,
  Download,
  Activity,
  Globe,
  Database,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Loader2,
  Layers,
  GitBranch,
} from 'lucide-react';

export const Header: React.FC = () => {
  const {
    tickData,
    isConnected,
    constellationSource,
    startSim,
    pauseSim,
    stepSim,
    setSpeed,
    resetSim,
    switchConstellationSource,
    runBenchmarks,
    setShowScenarioModal,
    setShowDispatchModal,
    setShowISLModal,
    setShowRAGDrawer,
    triggerAgentHealing,
    fetchISSVerification,
    exportDossier,
    activeTab,
    setActiveTab,
  } = useSimulationStore();

  const [isSwitchingSource, setIsSwitchingSource] = useState(false);
  const [isHealing, setIsHealing] = useState(false);
  const [healingStatus, setHealingStatus] = useState<string | null>(null);
  const [showISSModal, setShowISSModal] = useState(false);
  const [issData, setIssData] = useState<any | null>(null);
  const [isLoadingISS, setIsLoadingISS] = useState(false);

  const speed = tickData?.speed_multiplier || 5.0;
  const simTime = tickData?.sim_time_s || 0;
  const wallClock = tickData?.wall_clock_iso ? new Date(tickData.wall_clock_iso).toLocaleTimeString() : '--:--:--';
  const collisionAlerts = tickData?.collision_alerts?.length || 0;
  const activeAnomalies = tickData?.metrics_summary?.active_anomalies || 0;
  const isScenarioActive = tickData?.active_scenario?.is_active;
  const activeSource = tickData?.data_source || constellationSource || 'synthetic';

  const handleSourceToggle = async () => {
    setIsSwitchingSource(true);
    const nextSource = activeSource === 'synthetic' ? 'celestrak_real' : 'synthetic';
    try {
      await switchConstellationSource(nextSource);
    } finally {
      setIsSwitchingSource(false);
    }
  };

  const handleAgentHealing = async () => {
    setIsHealing(true);
    setHealingStatus(null);
    try {
      const res = await triggerAgentHealing();
      if (res) {
        setHealingStatus(res.status);
        setTimeout(() => setHealingStatus(null), 5000);
      }
    } finally {
      setIsHealing(false);
    }
  };

  const handleOpenISS = async () => {
    setShowISSModal(true);
    setIsLoadingISS(true);
    try {
      const data = await fetchISSVerification();
      setIssData(data);
    } finally {
      setIsLoadingISS(false);
    }
  };

  return (
    <>
      <header className="hud-panel w-full px-6 py-3 flex items-center justify-between z-20 border-b border-cyan-500/20">
        {/* Brand Title & Source Selector */}
        <div className="flex items-center gap-4">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-cyan-950/60 border border-cyan-400/40 shadow-inner">
            <Zap className="w-6 h-6 text-cyan-400 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-orbitron font-bold text-lg tracking-wider bg-gradient-to-r from-cyan-400 via-sky-200 to-indigo-400 bg-clip-text text-transparent">
                ORBIT-X
              </h1>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                AI Decision Intelligence Console
              </span>
            </div>
            
            {/* Constellation Data Source Mode Tag */}
            <div className="flex items-center gap-2 mt-0.5">
              <button
                onClick={handleSourceToggle}
                disabled={isSwitchingSource}
                className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono border transition ${
                  activeSource === 'celestrak_real'
                    ? 'bg-emerald-950 text-emerald-300 border-emerald-500/50 hover:bg-emerald-900'
                    : 'bg-slate-800 text-cyan-300 border-cyan-500/40 hover:bg-slate-700'
                }`}
                title="Click to toggle between Genuine Celestrak TLEs and Synthetic Walker Constellation"
              >
                <Database className="w-3 h-3 text-cyan-400" />
                <span>
                  SOURCE: {activeSource === 'celestrak_real' ? 'CELESTRAK LIVE TLE (STARLINK)' : 'SYNTHETIC WALKER-DELTA'}
                </span>
                {isSwitchingSource && <Loader2 className="w-2.5 h-2.5 animate-spin" />}
              </button>

              <button
                onClick={handleOpenISS}
                className="text-[10px] font-mono text-slate-400 hover:text-cyan-300 underline underline-offset-2 flex items-center gap-1"
                title="Verify ISS Ground-Truth Orbital Period Physics"
              >
                <CheckCircle2 className="w-2.5 h-2.5 text-emerald-400" />
                <span>ISS Period: 92.9m (99.7% parity)</span>
              </button>
            </div>
          </div>
        </div>

        {/* Clock & Constellation Status HUD */}
        <div className="flex items-center gap-6 bg-slate-900/60 px-4 py-2 rounded-lg border border-slate-700/50">
          <div className="flex flex-col">
            <span className="text-[10px] uppercase text-slate-400 font-mono">Mission Clock</span>
            <span className="font-mono text-sm font-semibold text-cyan-300">
              T+{Math.floor(simTime)}s <span className="text-xs text-slate-400">({wallClock} UTC)</span>
            </span>
          </div>

          <div className="h-6 w-px bg-slate-700/60" />

          <div className="flex items-center gap-3">
            <div className="flex flex-col">
              <span className="text-[10px] uppercase text-slate-400 font-mono">Health & Safety</span>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5">
                  <span className={`w-2 h-2 rounded-full ${activeAnomalies > 0 ? 'bg-rose-500 animate-ping' : 'bg-emerald-400'}`} />
                  <span className={`text-xs font-mono font-medium ${activeAnomalies > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {activeAnomalies > 0 ? `${activeAnomalies} Anomaly Alert` : 'Fleet Nominal'}
                  </span>
                </div>
                {collisionAlerts > 0 && (
                  <div className="flex items-center gap-1 text-amber-400 text-xs font-mono">
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>{collisionAlerts} TCA Risk</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="h-6 w-px bg-slate-700/60" />

          <div className="flex items-center gap-1.5">
            {isConnected ? (
              <div className="flex items-center gap-1 text-emerald-400 text-xs font-mono">
                <Wifi className="w-3.5 h-3.5" />
                <span>10Hz Sync</span>
              </div>
            ) : (
              <div className="flex items-center gap-1 text-rose-400 text-xs font-mono">
                <WifiOff className="w-3.5 h-3.5" />
                <span>Offline</span>
              </div>
            )}
          </div>
        </div>

        {/* Simulator Control Bar & Action Modals */}
        <div className="flex items-center gap-2">
          {/* Speed Controls */}
          <div className="flex items-center bg-slate-900/80 rounded-lg p-1 border border-slate-700">
            {[1, 5, 20, 60].map((s) => (
              <button
                key={s}
                onClick={() => setSpeed(s)}
                className={`px-2 py-1 text-xs font-mono rounded ${
                  speed === s
                    ? 'bg-cyan-500 text-slate-950 font-bold shadow'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                {s}x
              </button>
            ))}
          </div>

          {/* Play / Pause / Step / Reset */}
          <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-lg border border-slate-700">
            <button
              onClick={startSim}
              className="p-1.5 rounded hover:bg-cyan-500/20 text-cyan-400 hover:text-cyan-300 transition"
              title="Start Simulation"
            >
              <Play className="w-4 h-4" />
            </button>
            <button
              onClick={pauseSim}
              className="p-1.5 rounded hover:bg-slate-700 text-slate-300 hover:text-white transition"
              title="Pause Simulation"
            >
              <Pause className="w-4 h-4" />
            </button>
            <button
              onClick={stepSim}
              className="p-1.5 rounded hover:bg-slate-700 text-slate-300 hover:text-white transition"
              title="Single Step"
            >
              <FastForward className="w-4 h-4" />
            </button>
            <button
              onClick={resetSim}
              className="p-1.5 rounded hover:bg-rose-500/20 text-rose-400 hover:text-rose-300 transition"
              title="Reset Constellation"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>

          {/* Mission AI Copilot Button */}
          <button
            onClick={() => setShowRAGDrawer(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600/30 border border-cyan-400/60 text-cyan-200 text-xs font-mono hover:bg-cyan-600/50 transition shadow-sm font-semibold"
            title="Ask Grounded RAG Questions about Decision History"
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
            <span>AI Copilot</span>
          </button>

          {/* Self-Healing Agent Verification */}
          <button
            onClick={handleAgentHealing}
            disabled={isHealing}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-indigo-950/60 border border-indigo-500/40 text-indigo-300 text-xs font-mono hover:bg-indigo-900/60 transition shadow-sm"
            title="Trigger Self-Healing Continuous Verification Agent Loop"
          >
            {isHealing ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
            ) : (
              <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
            )}
            <span>{healingStatus ? `Agent: ${healingStatus}` : 'Self-Heal'}</span>
          </button>

          {/* Action Modals */}
          <button
            onClick={() => setShowScenarioModal(true)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-mono transition shadow-sm ${
              isScenarioActive
                ? 'bg-rose-500/30 border-rose-500 text-rose-300 animate-pulse font-bold'
                : 'bg-amber-600/20 border-amber-500/40 text-amber-300 hover:bg-amber-600/30'
            }`}
            title="Extreme Space Weather & Mission Scenarios"
          >
            <Activity className="w-3.5 h-3.5" />
            {isScenarioActive ? 'Scenario Active' : 'Scenarios'}
          </button>

          <button
            onClick={() => setShowISLModal(true)}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-emerald-600/20 border border-emerald-500/40 text-emerald-300 text-xs font-mono hover:bg-emerald-600/30 transition shadow-sm"
            title="Intersatellite Optical Laser Mesh"
          >
            <Network className="w-3.5 h-3.5" />
            ISL Mesh
          </button>

          <button
            onClick={() => setShowDispatchModal(true)}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-cyan-600/20 border border-cyan-500/40 text-cyan-300 text-xs font-mono hover:bg-cyan-600/30 transition shadow-sm"
            title="Dispatch Observation Target"
          >
            <Target className="w-3.5 h-3.5" />
            Dispatch
          </button>

          <button
            onClick={runBenchmarks}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono hover:bg-slate-700 hover:text-white transition shadow-sm"
            title="Run Scheduler Benchmarks"
          >
            <BarChart3 className="w-3.5 h-3.5" />
            Evals
          </button>

          <button
            onClick={exportDossier}
            className="flex items-center gap-1.5 px-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-mono transition shadow-sm"
            title="Export Constellation Telemetry Dossier JSON"
          >
            <Download className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      {/* Top Primary Navigation Bar */}
      <div className="w-full bg-slate-950/95 border-b border-cyan-500/20 px-6 py-2 flex flex-wrap items-center justify-between gap-3 z-10 backdrop-blur-md">
        <nav className="flex items-center gap-2 font-mono text-xs overflow-x-auto py-0.5">
          <button
            onClick={() => setActiveTab('assistant')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl font-semibold transition-all cursor-pointer ${
              activeTab === 'assistant'
                ? 'bg-gradient-to-r from-cyan-500/30 to-blue-500/30 border border-cyan-400 text-cyan-300 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>AI Assistant (Hero)</span>
            <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 font-bold">P0</span>
          </button>

          <button
            onClick={() => setActiveTab('decision')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl font-semibold transition-all cursor-pointer ${
              activeTab === 'decision'
                ? 'bg-gradient-to-r from-blue-500/30 to-indigo-500/30 border border-blue-400 text-blue-300 shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span>Decision Explorer</span>
          </button>

          <button
            onClick={() => setActiveTab('data')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl font-semibold transition-all cursor-pointer ${
              activeTab === 'data'
                ? 'bg-gradient-to-r from-purple-500/30 to-indigo-500/30 border border-purple-400 text-purple-300 shadow-md shadow-purple-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
            }`}
          >
            <GitBranch className="w-3.5 h-3.5 text-purple-400" />
            <span>Data Discovery & Lineage</span>
          </button>

          <button
            onClick={() => setActiveTab('traces')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl font-semibold transition-all cursor-pointer ${
              activeTab === 'traces'
                ? 'bg-gradient-to-r from-emerald-500/30 to-teal-500/30 border border-emerald-400 text-emerald-300 shadow-md shadow-emerald-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
            }`}
          >
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span>Agent Traces & MCP</span>
          </button>

          <button
            onClick={() => setActiveTab('monitoring')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl font-semibold transition-all cursor-pointer ${
              activeTab === 'monitoring'
                ? 'bg-cyan-500/20 border border-cyan-400 text-cyan-300 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5 text-cyan-400" />
            <span>Monitoring & SLOs</span>
          </button>

          <div className="h-4 w-px bg-slate-800 mx-1" />

          <button
            onClick={() => setActiveTab('simulation')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl font-semibold transition-all cursor-pointer ${
              activeTab === 'simulation'
                ? 'bg-slate-800 border border-slate-600 text-slate-100 shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
            }`}
          >
            <Globe className="w-3.5 h-3.5 text-slate-400" />
            <span>Simulation (Digital Twin)</span>
            <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">Eval</span>
          </button>
        </nav>

        {/* Status indicator on right */}
        <div className="hidden lg:flex items-center gap-3 text-xs font-mono text-slate-400">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>HITL Decision Pipeline Active</span>
          </div>
        </div>
      </div>

      {/* ISS Verification Modal */}
      {showISSModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fade-in">
          <div className="w-full max-w-lg bg-slate-900 border border-cyan-500/40 rounded-2xl p-6 space-y-4 shadow-2xl font-sans">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2 text-cyan-400">
                <Globe className="w-5 h-5" />
                <h3 className="text-base font-bold text-slate-100">
                  ISS Ground-Truth Physical Verification
                </h3>
              </div>
              <button
                onClick={() => setShowISSModal(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            {isLoadingISS ? (
              <div className="py-8 text-center text-slate-400 font-mono text-xs flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
                <span>Fetching live Celestrak TLE for NORAD 25544 (ISS)...</span>
              </div>
            ) : issData ? (
              <div className="space-y-4 font-mono text-xs">
                <div className="grid grid-cols-2 gap-2 bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <div>
                    <span className="text-slate-500">Target Object:</span>
                    <p className="text-cyan-300 font-bold">{issData.satellite_name}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">NORAD ID:</span>
                    <p className="text-slate-200">{issData.norad_id}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Calculated Period:</span>
                    <p className="text-emerald-400 font-bold">{issData.calculated_period_minutes} min</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Standard Baseline:</span>
                    <p className="text-slate-300">{issData.standard_iss_period_minutes} min</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Physics Deviation:</span>
                    <p className="text-emerald-400">{issData.deviation_minutes} min ({issData.relative_error_pct}%)</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Physical Verification:</span>
                    <p className="text-emerald-400 font-bold">{issData.is_physically_consistent ? 'PASS (CONFIRMED)' : 'FAIL'}</p>
                  </div>
                </div>
                <p className="text-slate-400 font-sans text-xs">
                  {issData.explanation}
                </p>
              </div>
            ) : (
              <p className="text-rose-400 text-xs font-mono">Failed to load ISS verification data.</p>
            )}

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowISSModal(false)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
