import React, { useState } from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import { Target, Clock, Award, HelpCircle, CheckCircle, AlertCircle } from 'lucide-react';
import type { MissionRequest } from '../types';

export const MissionQueue: React.FC = () => {
  const [tab, setTab] = useState<'ACTIVE' | 'COMPLETED'>('ACTIVE');
  const tickData = useSimulationStore((s) => s.tickData);
  const fetchExplanation = useSimulationStore((s) => s.fetchExplanation);

  const pending = tickData?.pending_missions || [];
  const active = tickData?.active_missions || [];
  const completed = tickData?.completed_missions || [];
  const currentSimTime = tickData?.sim_time_s || 0;

  const displayedMissions = tab === 'ACTIVE' ? [...active, ...pending] : completed;

  return (
    <div className="hud-panel flex flex-col h-full overflow-hidden border-l border-cyan-500/20">
      {/* Tab Header */}
      <div className="p-2 border-b border-cyan-500/20 flex items-center justify-between">
        <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setTab('ACTIVE')}
            className={`px-3 py-1 text-xs font-mono rounded ${
              tab === 'ACTIVE'
                ? 'bg-cyan-500 text-slate-950 font-bold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Active & Pending ({pending.length + active.length})
          </button>
          <button
            onClick={() => setTab('COMPLETED')}
            className={`px-3 py-1 text-xs font-mono rounded ${
              tab === 'COMPLETED'
                ? 'bg-cyan-500 text-slate-950 font-bold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Completed ({completed.length})
          </button>
        </div>
      </div>

      {/* Mission Cards List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {displayedMissions.length === 0 ? (
          <div className="text-center py-8 text-xs font-mono text-slate-500">
            No missions in this queue.
          </div>
        ) : (
          displayedMissions.map((m: MissionRequest) => {
            const timeRemaining = Math.max(0, m.deadline_s - currentSimTime);
            const isCompleted = m.status === 'COMPLETED';
            const isFailed = m.status === 'FAILED';
            const isInProgress = m.status === 'IN_PROGRESS';

            let prioBadge = 'bg-slate-700 text-slate-300';
            if (m.priority === 5) prioBadge = 'bg-rose-500/20 border border-rose-500/60 text-rose-300';
            else if (m.priority === 4) prioBadge = 'bg-amber-500/20 border border-amber-500/60 text-amber-300';
            else if (m.priority === 3) prioBadge = 'bg-cyan-500/20 border border-cyan-500/60 text-cyan-300';

            return (
              <div
                key={m.id}
                className="hud-card p-3 rounded-lg border border-slate-800/80 hover:border-cyan-500/40 transition flex flex-col gap-2"
              >
                {/* Header row */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${prioBadge}`}>
                      P{m.priority}
                    </span>
                    <span className="font-mono text-xs font-semibold text-slate-200">
                      {m.name}
                    </span>
                  </div>

                  {isCompleted ? (
                    <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400">
                      <CheckCircle className="w-3 h-3" /> Done
                    </span>
                  ) : isFailed ? (
                    <span className="flex items-center gap-1 text-[10px] font-mono text-rose-400">
                      <AlertCircle className="w-3 h-3" /> Failed
                    </span>
                  ) : isInProgress ? (
                    <span className="text-[10px] font-mono font-bold text-cyan-300 animate-pulse">
                      ⚡ Imaging
                    </span>
                  ) : (
                    <span className="text-[10px] font-mono text-slate-400">
                      {m.status}
                    </span>
                  )}
                </div>

                {/* Target location & Deadline */}
                <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400">
                  <div className="flex items-center gap-1">
                    <Target className="w-3 h-3 text-cyan-400" />
                    <span>{m.target_location.lat.toFixed(1)}°, {m.target_location.lon.toFixed(1)}°</span>
                  </div>
                  <div className="flex items-center gap-1 justify-end">
                    <Clock className="w-3 h-3 text-amber-400" />
                    <span>Expires: {timeRemaining.toFixed(0)}s</span>
                  </div>
                </div>

                {/* Assignment & Explain button */}
                <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] font-mono">
                  <div className="flex items-center gap-1 text-cyan-300">
                    <Award className="w-3 h-3 text-indigo-400" />
                    <span>{m.assigned_satellite_id ? `Assigned: ${m.assigned_satellite_id}` : 'Unassigned'}</span>
                  </div>

                  <button
                    onClick={() => fetchExplanation(m.id)}
                    className="flex items-center gap-1 px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-900/60 transition"
                  >
                    <HelpCircle className="w-3 h-3" />
                    Why this?
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
