import React, { useState, useEffect } from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import type { SensorType, TargetDispatchRequest } from '../types';
import { Target, Sparkles, Navigation, X, Radio, Eye, Flame, Layers } from 'lucide-react';


export const TargetDispatchModal: React.FC = () => {
  const show = useSimulationStore((s) => s.showDispatchModal);
  const setShow = useSimulationStore((s) => s.setShowDispatchModal);
  const dispatchCoords = useSimulationStore((s) => s.dispatchCoordinates);
  const dispatchTarget = useSimulationStore((s) => s.dispatchTarget);

  const [name, setName] = useState('Custom Orbital Observation Request');
  const [lat, setLat] = useState<number>(30.60);
  const [lon, setLon] = useState<number>(32.34);
  const [priority, setPriority] = useState<number>(4);
  const [sensorType, setSensorType] = useState<SensorType>('OPTICAL_RGB');
  const [dataSizeGb, setDataSizeGb] = useState<number>(14);
  const [deadlineMin, setDeadlineMin] = useState<number>(45);

  useEffect(() => {
    if (dispatchCoords) {
      setLat(dispatchCoords.lat);
      setLon(dispatchCoords.lon);
      setName(`Pointed Target @ ${dispatchCoords.lat.toFixed(2)}°, ${dispatchCoords.lon.toFixed(2)}°`);
    }
  }, [dispatchCoords]);

  if (!show) return null;

  const presets = [
    { name: 'Suez Canal Maritime Bottleneck', lat: 30.6043, lon: 32.3418, sensor: 'OPTICAL_RGB' as SensorType, prio: 4 },
    { name: 'Amazon Rainforest Active Front', lat: -3.4653, lon: -62.2159, sensor: 'THERMAL_IR' as SensorType, prio: 5 },
    { name: 'Mount Fuji Seismic Deformation', lat: 35.3606, lon: 138.7274, sensor: 'SAR_RADAR' as SensorType, prio: 4 },
    { name: 'Ukraine Grain Belt Multi-Crop', lat: 48.3794, lon: 31.1656, sensor: 'HYPERSPECTRAL' as SensorType, prio: 3 },
    { name: 'Strait of Gibraltar Surveillance', lat: 35.9622, lon: -5.6028, sensor: 'SAR_RADAR' as SensorType, prio: 5 },
    { name: 'South China Sea Maritime Corridor', lat: 12.0000, lon: 114.0000, sensor: 'OPTICAL_RGB' as SensorType, prio: 4 },
  ];

  const sensors: Array<{ type: SensorType; label: string; icon: any; desc: string }> = [
    { type: 'OPTICAL_RGB', label: 'Optical RGB (0.3m)', icon: Eye, desc: 'High-resolution panchromatic & multispectral visible imagery' },
    { type: 'SAR_RADAR', label: 'SAR Radar (X-Band)', icon: Radio, desc: 'All-weather, day/night cloud-penetrating synthetic aperture radar' },
    { type: 'THERMAL_IR', label: 'Thermal IR (MWIR/LWIR)', icon: Flame, desc: 'Thermal radiometric flux for wildfire, volcano, and energy auditing' },
    { type: 'HYPERSPECTRAL', label: 'Hyperspectral (240-Band)', icon: Layers, desc: 'Mineralogy, crop nitrogen, and chemical plume spectroscopy' },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const req: TargetDispatchRequest = {
      name,
      lat: Number(lat),
      lon: Number(lon),
      priority,
      sensor_type: sensorType,
      data_size_gb: Number(dataSizeGb),
      deadline_offset_s: Number(deadlineMin) * 60,
    };
    dispatchTarget(req);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4 animate-fade-in">
      <div className="bg-slate-900 border border-cyan-500/40 rounded-2xl w-full max-w-2xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              <Target className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                Point-and-Click Target Dispatcher
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  CP-SAT Live Intake
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Dispatch an observation request. The constellation optimizer will compute orbital access cones and assign the optimal satellite.
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

        {/* Content Form */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-5 flex-1">
          {/* Quick Presets */}
          <div>
            <label className="text-xs font-mono text-cyan-400 mb-2 flex items-center gap-1.5">
              <Navigation className="w-3.5 h-3.5" />
              Global Hotspot Presets
            </label>
            <div className="flex flex-wrap gap-2">
              {presets.map((p, idx) => (
                <button
                  type="button"
                  key={idx}
                  onClick={() => {
                    setName(p.name);
                    setLat(p.lat);
                    setLon(p.lon);
                    setSensorType(p.sensor);
                    setPriority(p.prio);
                  }}
                  className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-[11px] font-mono text-slate-300 hover:text-cyan-300 hover:border-cyan-500/50 transition"
                >
                  📍 {p.name.slice(0, 24)}...
                </button>
              ))}
            </div>
          </div>

          {/* Mission Name & Target Location */}
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">Target Mission Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-cyan-400 font-mono"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1">Latitude (°N/S)</label>
                <input
                  type="number"
                  step="0.0001"
                  min="-90"
                  max="90"
                  value={lat}
                  onChange={(e) => setLat(parseFloat(e.target.value))}
                  required
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-cyan-400 font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1">Longitude (°E/W)</label>
                <input
                  type="number"
                  step="0.0001"
                  min="-180"
                  max="180"
                  value={lon}
                  onChange={(e) => setLon(parseFloat(e.target.value))}
                  required
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-cyan-400 font-mono"
                />
              </div>
            </div>
          </div>

          {/* Sensor Payload Selection */}
          <div>
            <label className="block text-xs font-mono text-slate-400 mb-2">Payload Sensor Type</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {sensors.map((s) => {
                const Icon = s.icon;
                const selected = sensorType === s.type;
                return (
                  <div
                    key={s.type}
                    onClick={() => setSensorType(s.type)}
                    className={`p-3 rounded-xl border cursor-pointer transition ${
                      selected
                        ? 'bg-cyan-950/40 border-cyan-400 shadow-md'
                        : 'bg-slate-950 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Icon className={`w-4 h-4 ${selected ? 'text-cyan-400' : 'text-slate-400'}`} />
                      <span className={`text-xs font-bold ${selected ? 'text-cyan-200' : 'text-slate-200'}`}>
                        {s.label}
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-400 leading-tight">{s.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Priority & Deadline */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">
                Priority: <span className="text-cyan-400 font-bold">P{priority}</span>
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(parseInt(e.target.value))}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-cyan-400 font-mono"
              >
                <option value={1}>P1 — Routine Baseline</option>
                <option value={2}>P2 — Standard Survey</option>
                <option value={3}>P3 — Priority Client</option>
                <option value={4}>P4 — Urgent Target</option>
                <option value={5}>P5 — Critical Emergency</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">
                Data Size: <span className="text-cyan-400 font-bold">{dataSizeGb} GB</span>
              </label>
              <input
                type="range"
                min="6"
                max="32"
                step="2"
                value={dataSizeGb}
                onChange={(e) => setDataSizeGb(parseInt(e.target.value))}
                className="w-full accent-cyan-400 mt-2"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">
                Deadline: <span className="text-cyan-400 font-bold">+{deadlineMin} min</span>
              </label>
              <input
                type="range"
                min="15"
                max="120"
                step="15"
                value={deadlineMin}
                onChange={(e) => setDeadlineMin(parseInt(e.target.value))}
                className="w-full accent-cyan-400 mt-2"
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-2">
            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-600 hover:from-cyan-400 hover:to-sky-500 text-slate-950 font-bold font-mono text-sm flex items-center justify-center gap-2 shadow-lg shadow-cyan-950 transition"
            >
              <Sparkles className="w-4 h-4" />
              Dispatch Target & Re-Optimize Constellation
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
