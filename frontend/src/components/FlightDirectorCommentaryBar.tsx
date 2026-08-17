import React, { useState, useEffect } from 'react';
import { Radio, ShieldCheck, Cpu } from 'lucide-react';
import type { FlightDirectorCommentary } from '../types';

interface FlightDirectorCommentaryBarProps {
  activeCommentary?: FlightDirectorCommentary | null;
}

export const FlightDirectorCommentaryBar: React.FC<FlightDirectorCommentaryBarProps> = ({
  activeCommentary,
}) => {
  const [commentary, setCommentary] = useState<FlightDirectorCommentary>({
    commentary_id: 'COMM-INIT',
    timestamp_s: 0.0,
    event_type: 'CONSTELLATION_STATE',
    commentary: 'FLIGHT-DIR: Constellation nominal. 12 spacecraft propagating under J2 gravitation. Neural auction valuation active.',
    verified_factual: true,
    llm_latency_ms: 12.4,
    model_used: 'deterministic-verified-template',
  });

  useEffect(() => {
    if (activeCommentary) {
      setCommentary(activeCommentary);
    }
  }, [activeCommentary]);

  return (
    <div className="bg-slate-900/90 backdrop-blur border-y border-cyan-500/30 px-4 py-2 flex items-center justify-between gap-4 text-xs font-mono select-none">
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <div className="flex items-center gap-1.5 text-cyan-400 font-bold tracking-wider shrink-0">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
          </span>
          <Radio className="w-3.5 h-3.5" />
          <span>FLIGHT DIRECTOR:</span>
        </div>
        <p className="text-slate-200 truncate font-sans text-xs">
          {commentary.commentary}
        </p>
      </div>

      <div className="flex items-center gap-3 shrink-0 text-[10px] text-slate-400 font-mono">
        <div className="flex items-center gap-1 bg-cyan-950/60 text-cyan-300 border border-cyan-800/60 rounded px-2 py-0.5">
          <ShieldCheck className="w-3 h-3 text-cyan-400" />
          <span>FACT-CHECKED</span>
        </div>
        <div className="hidden sm:flex items-center gap-1 bg-slate-800 border border-slate-700 rounded px-2 py-0.5">
          <Cpu className="w-3 h-3 text-indigo-400" />
          <span>{commentary.model_used}</span>
        </div>
      </div>
    </div>
  );
};
