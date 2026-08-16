import React from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import {
  Play,
  Pause,
  FastForward,
  RotateCcw,
  BarChart3,
  Users,
  Zap,
  ShieldAlert,
  Wifi,
  WifiOff,
  Network,
  Target,
  Download,
  Activity,
} from 'lucide-react';

export const Header: React.FC = () => {
  const {
    tickData,
    isConnected,
    startSim,
    pauseSim,
    stepSim,
    setSpeed,
    resetSim,
    runBenchmarks,
    fetchAuctions,
    setShowScenarioModal,
    setShowDispatchModal,
    setShowISLModal,
    exportDossier,
  } = useSimulationStore();

  const speed = tickData?.speed_multiplier || 5.0;
  const simTime = tickData?.sim_time_s || 0;
  const wallClock = tickData?.wall_clock_iso ? new Date(tickData.wall_clock_iso).toLocaleTimeString() : '--:--:--';
  const collisionAlerts = tickData?.collision_alerts?.length || 0;
  const activeAnomalies = tickData?.metrics_summary?.active_anomalies || 0;
  const isScenarioActive = tickData?.active_scenario?.is_active;

  return (
    <header className="hud-panel w-full px-6 py-3 flex items-center justify-between z-20 border-b border-cyan-500/20">
      {/* Brand Title */}
      <div className="flex items-center gap-3">
        <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-cyan-950/60 border border-cyan-400/40 shadow-inner">
          <Zap className="w-6 h-6 text-cyan-400 animate-pulse" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-orbitron font-bold text-lg tracking-wider bg-gradient-to-r from-cyan-400 via-sky-200 to-indigo-400 bg-clip-text text-transparent">
              ORBIT-X
            </h1>
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
              Autonomous Constellation Network V2.0
            </span>
          </div>
          <p className="text-xs text-slate-400 font-mono">
            OR-Tools CP-SAT • Multi-Agent Auction • ISL Optical Mesh • Health AI
          </p>
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
      <div className="flex items-center gap-2.5">
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
          {isScenarioActive ? 'Scenario Active' : 'Scenario Director'}
        </button>

        <button
          onClick={() => setShowISLModal(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 border border-emerald-500/40 text-emerald-300 text-xs font-mono hover:bg-emerald-600/30 transition shadow-sm"
          title="Intersatellite Optical Laser Mesh"
        >
          <Network className="w-3.5 h-3.5" />
          ISL Mesh
        </button>

        <button
          onClick={() => setShowDispatchModal(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600/20 border border-cyan-500/40 text-cyan-300 text-xs font-mono hover:bg-cyan-600/30 transition shadow-sm"
          title="Dispatch Observation Target"
        >
          <Target className="w-3.5 h-3.5" />
          Dispatch Target
        </button>

        <button
          onClick={fetchAuctions}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 text-xs font-mono hover:bg-indigo-600/30 transition shadow-sm"
          title="Multi-Agent Auction Ledger"
        >
          <Users className="w-3.5 h-3.5" />
          Auctions
        </button>

        <button
          onClick={runBenchmarks}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono hover:bg-slate-700 hover:text-white transition shadow-sm"
          title="Run Scheduler Benchmarks"
        >
          <BarChart3 className="w-3.5 h-3.5" />
          Benchmarks
        </button>

        <button
          onClick={exportDossier}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-mono transition shadow-sm"
          title="Export Constellation Telemetry Dossier JSON"
        >
          <Download className="w-3.5 h-3.5" />
        </button>
      </div>
    </header>
  );
};

