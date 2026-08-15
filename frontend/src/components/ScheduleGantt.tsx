import React from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import { Calendar } from 'lucide-react';

export const ScheduleGantt: React.FC = () => {
  const tickData = useSimulationStore((s) => s.tickData);
  const satellites = tickData?.satellites || [];
  const missions = tickData?.pending_missions || [];
  const simTime = tickData?.sim_time_s || 0;

  const horizonS = 3600.0;
  const startWindowS = Math.floor(simTime / 300) * 300; // Snap to 5-min intervals
  const endWindowS = startWindowS + horizonS;

  return (
    <div className="hud-panel p-3 border-t border-cyan-500/20 flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-cyan-400" />
          <h2 className="font-orbitron font-semibold text-xs tracking-wider text-cyan-300">
            OPTIMIZED GANTT SCHEDULE
          </h2>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
            Horizon: T+{startWindowS}s to T+{endWindowS}s
          </span>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-[10px] font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-2 rounded bg-emerald-500" />
            <span>Target Imaging</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-2 rounded bg-purple-500" />
            <span>Ground Downlink</span>
          </div>
        </div>
      </div>

      {/* Gantt Timeline Grid */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden relative border border-slate-800 rounded bg-slate-950/60 p-2 space-y-1.5">
        {satellites.map((sat) => {
          const satMissions = missions.filter((m) => m.assigned_satellite_id === sat.id);

          return (
            <div key={sat.id} className="flex items-center h-5 text-[9px] font-mono">
              <span className="w-14 text-slate-400 font-bold flex-shrink-0">{sat.id}</span>
              <div className="flex-1 h-full bg-slate-900/60 rounded border border-slate-800/80 relative overflow-hidden">
                {satMissions.map((m) => {
                  if (!m.imaging_start_s || !m.imaging_end_s) return null;
                  const leftPct = Math.max(0, ((m.imaging_start_s - startWindowS) / horizonS) * 100);
                  const widthPct = Math.max(1.5, ((m.imaging_end_s - m.imaging_start_s) / horizonS) * 100);

                  return (
                    <div
                      key={`img-${m.id}`}
                      className="absolute top-0 bottom-0 bg-emerald-500/80 border border-emerald-300 rounded text-[7px] text-black font-bold flex items-center justify-center overflow-hidden"
                      style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
                      title={`${m.name} (${m.id})`}
                    >
                      IMG
                    </div>
                  );
                })}

                {satMissions.map((m) => {
                  if (!m.downlink_start_s || !m.downlink_end_s) return null;
                  const leftPct = Math.max(0, ((m.downlink_start_s - startWindowS) / horizonS) * 100);
                  const widthPct = Math.max(1.5, ((m.downlink_end_s - m.downlink_start_s) / horizonS) * 100);

                  return (
                    <div
                      key={`dl-${m.id}`}
                      className="absolute top-0 bottom-0 bg-purple-500/80 border border-purple-300 rounded text-[7px] text-white font-bold flex items-center justify-center overflow-hidden"
                      style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
                      title={`Downlink @ ${m.downlink_ground_station_id}`}
                    >
                      DL
                    </div>
                  );
                })}

                {simTime >= startWindowS && simTime <= endWindowS && (
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-cyan-400 shadow-glow"
                    style={{ left: `${((simTime - startWindowS) / horizonS) * 100}%` }}
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
