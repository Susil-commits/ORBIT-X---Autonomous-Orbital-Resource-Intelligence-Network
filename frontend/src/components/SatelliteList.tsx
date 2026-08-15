import React from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import { Battery, Sun, Moon, HardDrive, AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';
import type { SatelliteState } from '../types';

export const SatelliteList: React.FC = () => {
  const tickData = useSimulationStore((s) => s.tickData);
  const selectedSatId = useSimulationStore((s) => s.selectedSatelliteId);
  const setSelectedSatId = useSimulationStore((s) => s.setSelectedSatelliteId);

  const satellites = tickData?.satellites || [];

  return (
    <div className="hud-panel flex flex-col h-full overflow-hidden border-r border-cyan-500/20">
      {/* Panel Header */}
      <div className="p-3 border-b border-cyan-500/20 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="font-orbitron font-semibold text-xs tracking-wider text-cyan-300">
            CONSTELLATION NODES
          </h2>
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300">
            {satellites.length} Active
          </span>
        </div>
        <span className="text-[10px] font-mono text-slate-400">Walker 53°/12/3</span>
      </div>

      {/* Satellite Scrollable Cards */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {satellites.map((sat: SatelliteState) => {
          const isSelected = sat.id === selectedSatId;
          const socPct = Math.round(sat.battery.soc * 100);
          const isFault = sat.health_status === 'CRITICAL_FAULT';
          const isDegraded = sat.health_status === 'DEGRADED';
          const isImaging = sat.active_task_type === 'IMAGING';
          const isDownlink = sat.active_task_type === 'DOWNLINK';

          let statusBg = 'border-slate-800 bg-slate-900/60';
          if (isSelected) statusBg = 'border-cyan-400 bg-cyan-950/40 shadow-lg glow-cyan';
          else if (isFault) statusBg = 'border-rose-500/50 bg-rose-950/30';
          else if (isDegraded) statusBg = 'border-amber-500/40 bg-amber-950/20';

          return (
            <div
              key={sat.id}
              onClick={() => setSelectedSatId(isSelected ? null : sat.id)}
              className={`hud-card p-2.5 rounded-lg cursor-pointer transition-all border ${statusBg}`}
            >
              {/* Header row */}
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-1.5">
                  <span className="font-orbitron font-bold text-xs text-white">
                    {sat.id}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    P{sat.orbit_plane}
                  </span>
                </div>

                {/* Health Badge */}
                <div className="flex items-center gap-1">
                  {isFault ? (
                    <span className="flex items-center gap-1 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-rose-500/20 border border-rose-500/60 text-rose-400">
                      <ShieldAlert className="w-3 h-3" /> FAULT
                    </span>
                  ) : isDegraded ? (
                    <span className="flex items-center gap-1 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-500/20 border border-amber-500/60 text-amber-400">
                      <AlertTriangle className="w-3 h-3" /> DEGRADED
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                      <CheckCircle2 className="w-3 h-3" /> NOMINAL
                    </span>
                  )}
                </div>
              </div>

              {/* Battery & Sunlit row */}
              <div className="grid grid-cols-2 gap-2 mb-2 text-[10px] font-mono text-slate-300">
                <div className="flex items-center gap-1.5">
                  <Battery className={`w-3.5 h-3.5 ${socPct < 25 ? 'text-rose-400 animate-pulse' : 'text-cyan-400'}`} />
                  <span>{socPct}% SoC</span>
                </div>
                <div className="flex items-center gap-1 justify-end">
                  {sat.battery.is_sunlit ? (
                    <span className="flex items-center gap-1 text-amber-300">
                      <Sun className="w-3 h-3" /> Sunlit
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-indigo-300">
                      <Moon className="w-3 h-3" /> Eclipse
                    </span>
                  )}
                </div>
              </div>

              {/* Battery Progress Bar */}
              <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden mb-2">
                <div
                  className={`h-full rounded-full transition-all duration-300 ${
                    socPct < 25 ? 'bg-rose-500' : socPct < 50 ? 'bg-amber-400' : 'bg-cyan-400'
                  }`}
                  style={{ width: `${socPct}%` }}
                />
              </div>

              {/* Task Activity & Buffer row */}
              <div className="flex items-center justify-between text-[10px] font-mono">
                <div className="flex items-center gap-1">
                  {isImaging ? (
                    <span className="text-emerald-400 font-semibold animate-pulse">
                      📷 {sat.active_target_name ? sat.active_target_name.slice(0, 14) : 'Imaging'}
                    </span>
                  ) : isDownlink ? (
                    <span className="text-purple-400 font-semibold animate-pulse">
                      📡 {sat.active_target_name ? sat.active_target_name.slice(0, 14) : 'Downlinking'}
                    </span>
                  ) : (
                    <span className="text-slate-500">Idle / Orbiting</span>
                  )}
                </div>

                <div className="flex items-center gap-1 text-slate-400">
                  <HardDrive className="w-3 h-3" />
                  <span>{sat.onboard_storage_used_gb.toFixed(1)} GB</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
