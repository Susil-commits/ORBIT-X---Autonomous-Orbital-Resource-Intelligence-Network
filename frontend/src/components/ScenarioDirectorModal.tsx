import React from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import type { ScenarioType } from '../types';
import { Zap, AlertTriangle, ShieldAlert, Radio, Activity, CheckCircle2, RotateCcw, X } from 'lucide-react';

export const ScenarioDirectorModal: React.FC = () => {
  const show = useSimulationStore((s) => s.showScenarioModal);
  const setShow = useSimulationStore((s) => s.setShowScenarioModal);
  const tickData = useSimulationStore((s) => s.tickData);
  const triggerScenario = useSimulationStore((s) => s.triggerScenario);
  const resetScenario = useSimulationStore((s) => s.resetScenario);

  if (!show) return null;

  const scenario = tickData?.active_scenario;
  const isScenarioActive = scenario && scenario.is_active;

  const scenarios: Array<{
    type: ScenarioType;
    title: string;
    icon: any;
    color: string;
    severity: string;
    description: string;
    aiResponse: string;
  }> = [
    {
      type: 'SOLAR_STORM',
      title: 'Geomagnetic Solar Storm (CME Flare)',
      icon: Zap,
      color: 'amber',
      severity: 'CRITICAL',
      description: 'Severe solar energetic particle flare inducing +14°C thermal surge, reaction wheel gyro noise, and 45% solar array degradation.',
      aiResponse: 'Isolation Forest triggers autonomous constellation safe-mode power-shedding & SoC margin protection.',
    },
    {
      type: 'DEBRIS_CONJUNCTION',
      title: 'Orbital Debris Conjunction & CAM Evasion',
      icon: ShieldAlert,
      color: 'rose',
      severity: 'CRITICAL',
      description: 'High-speed fragmentation debris (COSMOS-2251) crossing Plane 1 at 14.8 km/s relative speed with predicted TCA < 180s on SAT-04.',
      aiResponse: 'Collision AI computes optimal prograde 1.45 m/s ΔV impulse burn, pushing miss distance from 2.1 km to 52.8 km.',
    },
    {
      type: 'GROUND_BLACKOUT',
      title: 'Polar Ground Station Network Blackout',
      icon: Radio,
      color: 'purple',
      severity: 'HIGH',
      description: 'Severe uplink/downlink power outage at Svalbard and McMurdo stations, isolating high-latitude coverage passes.',
      aiResponse: 'Multi-Agent Auction & ISL Optical Mesh reroutes polar telemetry to equatorial antennas (Hawaii & Singapore).',
    },
    {
      type: 'DISASTER_SURGE',
      title: 'Disaster Reconnaissance Surge (5x P5)',
      icon: AlertTriangle,
      color: 'cyan',
      severity: 'CRITICAL',
      description: 'Simultaneous tsunami, megafire, and earthquake events inject 5 urgent Priority-5 observation requests into the intake queue.',
      aiResponse: 'Google OR-Tools CP-SAT executes instant constellation re-optimization, preempting commercial surveys.',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4 animate-fade-in">
      <div className="bg-slate-900 border border-cyan-500/40 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30">
              <Activity className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                Extreme Space Scenario Director
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  AI Self-Healing Engine
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Simulate catastrophic space weather, orbital debris conjunctions, and mission surges to test constellation autonomy.
              </p>
            </div>
          </div>
          <button
            onClick={() => setShow(false)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Active Scenario Live Status Banner */}
          {isScenarioActive ? (
            <div className="p-4 rounded-xl bg-gradient-to-r from-rose-950/40 via-slate-900 to-amber-950/40 border border-rose-500/40 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
                  <span className="text-xs font-bold font-mono uppercase text-rose-400">
                    ACTIVE SCENARIO: {scenario?.title}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-500/20 text-rose-300 border border-rose-500/40">
                    {scenario?.severity} SEVERITY
                  </span>
                </div>
                <button
                  onClick={() => resetScenario()}
                  className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-cyan-300 border border-cyan-500/40 flex items-center gap-1.5 transition"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Restore Nominal
                </button>
              </div>
              <p className="text-xs text-slate-300">{scenario?.description}</p>

              {/* AI Actions Log */}
              {scenario?.ai_actions_taken && scenario.ai_actions_taken.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-800/80">
                  <div className="text-[11px] font-mono font-bold text-cyan-400 mb-1.5 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    Autonomous AI Recovery Mitigations Executed:
                  </div>
                  <ul className="space-y-1">
                    {scenario.ai_actions_taken.map((act, idx) => (
                      <li key={idx} className="text-[11px] font-mono text-emerald-300/90 pl-4 border-l border-emerald-500/40">
                        • {act}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                <div>
                  <div className="text-xs font-bold text-slate-200">Constellation Operating in Nominal Baseline</div>
                  <div className="text-[11px] text-slate-400">All 12 nodes, solar arrays, and ground downlinks healthy.</div>
                </div>
              </div>
              <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/30">
                100% HEALTHY
              </span>
            </div>
          )}

          {/* Scenario Trigger Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {scenarios.map((sc) => {
              const Icon = sc.icon;
              const isCurrent = Boolean(isScenarioActive && scenario?.scenario_type === sc.type);


              return (
                <div
                  key={sc.type}
                  className={`p-4 rounded-xl border transition-all flex flex-col justify-between ${
                    isCurrent
                      ? 'bg-slate-900 border-rose-500 shadow-lg shadow-rose-950/50'
                      : 'bg-slate-950/70 border-slate-800 hover:border-cyan-500/50 hover:bg-slate-900/60'
                  }`}
                >
                  <div className="space-y-2.5">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700 text-cyan-400">
                          <Icon className="w-4 h-4" />
                        </div>
                        <div>
                          <h3 className="text-sm font-bold text-slate-100">{sc.title}</h3>
                          <span className="text-[10px] font-mono text-rose-400 uppercase font-semibold">
                            {sc.severity} Severity
                          </span>
                        </div>
                      </div>
                    </div>

                    <p className="text-xs text-slate-400 leading-relaxed">{sc.description}</p>

                    <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px] font-mono text-cyan-300/90">
                      <span className="text-slate-400 font-sans">AI Reaction: </span>
                      {sc.aiResponse}
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between">
                    <span className="text-[10px] font-mono text-slate-500">Trigger Scenario</span>
                    <button
                      onClick={() => triggerScenario(sc.type)}
                      disabled={isCurrent}
                      className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition flex items-center gap-1.5 ${
                        isCurrent
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40 cursor-default'
                          : 'bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/50 hover:border-cyan-400'
                      }`}
                    >
                      {isCurrent ? (
                        <>
                          <Activity className="w-3.5 h-3.5 animate-spin" /> Active
                        </>
                      ) : (
                        <>
                          <Zap className="w-3.5 h-3.5" /> Inject Scenario
                        </>
                      )}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950 flex items-center justify-between text-xs font-mono text-slate-400">
          <div>ORBIT-X Autonomous Reactive Scheduler • Multi-Agent Resolution</div>
          <button
            onClick={() => setShow(false)}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
