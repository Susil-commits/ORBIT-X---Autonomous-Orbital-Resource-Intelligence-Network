import React from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import { Activity, Flame, Cpu, Radio, Zap, ShieldAlert, RefreshCw } from 'lucide-react';

export const TelemetryHUD: React.FC = () => {
  const tickData = useSimulationStore((s) => s.tickData);
  const selectedSatId = useSimulationStore((s) => s.selectedSatelliteId);
  const injectFault = useSimulationStore((s) => s.injectFault);
  const clearFaults = useSimulationStore((s) => s.clearFaults);

  const satellites = tickData?.satellites || [];
  const activeSat = satellites.find((s) => s.id === selectedSatId) || satellites[0];

  if (!activeSat) {
    return (
      <div className="hud-panel p-4 text-xs font-mono text-slate-500 flex items-center justify-center h-full">
        Initializing Constellation Telemetry Stream...
      </div>
    );
  }

  const tel = activeSat.telemetry;
  const isSelected = activeSat.id === selectedSatId;
  const isAnomaly = tel.anomaly_score > 0.52;

  return (
    <div className="hud-panel flex flex-col h-full overflow-hidden border-t border-cyan-500/20">
      {/* HUD Header */}
      <div className="p-3 border-b border-cyan-500/20 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h2 className="font-orbitron font-semibold text-xs tracking-wider text-cyan-300">
            TELEMETRY & HEALTH AI HUD
          </h2>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
            {activeSat.id} ({activeSat.name}) {isSelected ? '• FOCUS' : '• AUTO'}
          </span>
        </div>

        {/* Anomaly Gauge Badge */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-slate-400">Isolation Forest Score:</span>
          <span
            className={`font-mono text-xs font-bold px-2 py-0.5 rounded border ${
              isAnomaly
                ? 'bg-rose-500/20 border-rose-500 text-rose-300 animate-pulse'
                : 'bg-emerald-500/10 border-emerald-500/40 text-emerald-300'
            }`}
          >
            {(tel.anomaly_score * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Sensor Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 p-3 flex-1 overflow-y-auto">
        {/* Bus Voltage */}
        <div className="hud-card p-2.5 rounded-lg border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
            <span>Main Bus Voltage</span>
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="my-1">
            <span className={`font-mono text-base font-bold ${tel.bus_voltage_v < 24 ? 'text-rose-400' : 'text-cyan-300'}`}>
              {tel.bus_voltage_v.toFixed(1)} V
            </span>
            <span className="text-[9px] font-mono text-slate-500 ml-1.5">(28.0V Nom)</span>
          </div>
          <div className="text-[9px] font-mono text-slate-400">
            Solar: {tel.solar_current_a.toFixed(1)} A ({activeSat.battery.solar_generation_w.toFixed(0)} W)
          </div>
        </div>

        {/* Battery & Payload Thermal */}
        <div className="hud-card p-2.5 rounded-lg border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
            <span>Thermal Subsystems</span>
            <Flame className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="my-1">
            <span className={`font-mono text-base font-bold ${tel.battery_temp_c > 45 ? 'text-rose-400' : 'text-amber-300'}`}>
              {tel.battery_temp_c.toFixed(1)}°C
            </span>
            <span className="text-[9px] font-mono text-slate-500 ml-1.5">(Cell Temp)</span>
          </div>
          <div className="text-[9px] font-mono text-slate-400">
            Payload Sensor: {tel.payload_temp_c.toFixed(1)}°C
          </div>
        </div>

        {/* Attitude Jitter (ADCS) */}
        <div className="hud-card p-2.5 rounded-lg border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
            <span>ADCS RMS Jitter</span>
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="my-1">
            <span className={`font-mono text-base font-bold ${tel.reaction_wheel_jitter_dps > 0.2 ? 'text-rose-400' : 'text-indigo-300'}`}>
              {tel.reaction_wheel_jitter_dps.toFixed(3)}°/s
            </span>
            <span className="text-[9px] font-mono text-slate-500 ml-1.5">(Precision)</span>
          </div>
          <div className="text-[9px] font-mono text-slate-400">
            Velocity: {activeSat.velocity_kms.toFixed(2)} km/s
          </div>
        </div>

        {/* Comms & Sub-Satellite Location */}
        <div className="hud-card p-2.5 rounded-lg border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
            <span>X-Band Downlink & Ground</span>
            <Radio className="w-3.5 h-3.5 text-purple-400" />
          </div>
          <div className="my-1">
            <span className="font-mono text-base font-bold text-purple-300">
              {tel.rf_snr_db > 0 ? `${tel.rf_snr_db.toFixed(1)} dB` : 'Carrier Off'}
            </span>
            <span className="text-[9px] font-mono text-slate-500 ml-1.5">SNR</span>
          </div>
          <div className="text-[9px] font-mono text-slate-400">
            Pos: {activeSat.geodetic.lat.toFixed(1)}°, {activeSat.geodetic.lon.toFixed(1)}°
          </div>
        </div>
      </div>

      {/* Anomaly Injection & Autonomous Healing Deck */}
      <div className="px-3 py-2 bg-slate-900/90 border-t border-slate-800 flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
          <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
          <span>Inject Fault on {activeSat.id}:</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => injectFault(activeSat.id, 'BATTERY_THERMAL_RUNAWAY')}
            className="px-2 py-1 rounded bg-rose-950/60 border border-rose-600/40 text-rose-300 hover:bg-rose-900/60 text-[10px] font-mono transition"
          >
            🔥 Thermal Runaway
          </button>
          <button
            onClick={() => injectFault(activeSat.id, 'REACTION_WHEEL_JITTER')}
            className="px-2 py-1 rounded bg-amber-950/60 border border-amber-600/40 text-amber-300 hover:bg-amber-900/60 text-[10px] font-mono transition"
          >
            🔄 Wheel Jitter
          </button>
          <button
            onClick={() => injectFault(activeSat.id, 'TRANSPONDER_FAILURE')}
            className="px-2 py-1 rounded bg-purple-950/60 border border-purple-600/40 text-purple-300 hover:bg-purple-900/60 text-[10px] font-mono transition"
          >
            📡 SNR Drop
          </button>
          <button
            onClick={() => clearFaults(activeSat.id)}
            className="flex items-center gap-1 px-2.5 py-1 rounded bg-emerald-950/60 border border-emerald-500/50 text-emerald-300 hover:bg-emerald-900/60 text-[10px] font-mono transition"
          >
            <RefreshCw className="w-3 h-3" /> Self-Heal
          </button>
        </div>
      </div>
    </div>
  );
};
