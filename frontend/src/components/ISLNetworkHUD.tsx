import React, { useState } from 'react';
import { useSimulationStore } from '../hooks/useSimulationStore';
import { Network, Radio, ArrowRight, X, Activity } from 'lucide-react';


export const ISLNetworkHUD: React.FC = () => {
  const show = useSimulationStore((s) => s.showISLModal);
  const setShow = useSimulationStore((s) => s.setShowISLModal);
  const tickData = useSimulationStore((s) => s.tickData);

  const [filter, setFilter] = useState<'ALL' | 'ACTIVE' | 'IN_USE'>('ACTIVE');

  if (!show) return null;

  const islMesh = tickData?.isl_mesh;
  const links = islMesh?.links || [];
  const routes = islMesh?.routes || [];

  const filteredLinks = links.filter((l) => {
    if (filter === 'ACTIVE') return l.status === 'ACTIVE';
    if (filter === 'IN_USE') return l.is_in_use;
    return true;
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4 animate-fade-in">
      <div className="bg-slate-900 border border-cyan-500/40 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              <Network className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                Intersatellite Optical Laser Mesh (ISL)
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  10 Gbps Cross-Link
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Line-of-sight laser cross-links and Dijkstra min-delay multi-hop data packet relay routing.
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
          {/* Top Metrics Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <div className="text-[10px] font-mono text-slate-400">Active ISL Cross-Links</div>
              <div className="text-xl font-bold font-mono text-cyan-400 mt-1">
                {islMesh?.active_links_count || 0}{' '}
                <span className="text-xs text-slate-500 font-normal">/ {islMesh?.max_links_possible || 66}</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <div className="text-[10px] font-mono text-slate-400">Average Mesh Latency</div>
              <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
                {islMesh?.average_latency_ms || 0}{' '}
                <span className="text-xs text-slate-500 font-normal">ms</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <div className="text-[10px] font-mono text-slate-400">Transceiver Range Limit</div>
              <div className="text-xl font-bold font-mono text-sky-400 mt-1">
                6,200 <span className="text-xs text-slate-500 font-normal">km</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <div className="text-[10px] font-mono text-slate-400">Earth Limb Occlusion</div>
              <div className="text-xl font-bold font-mono text-purple-400 mt-1">
                Active <span className="text-xs text-slate-500 font-normal">(100km buffer)</span>
              </div>
            </div>
          </div>

          {/* Multi-Hop Relay Routes to Ground Stations */}
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold font-mono uppercase text-slate-300 flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5 text-cyan-400" />
                Active Multi-Hop Constellation Downlink Relays ({routes.length})
              </h3>
              <span className="text-[10px] font-mono text-slate-500">Solved via Dijkstra Min-Delay</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 max-h-48 overflow-y-auto pr-1">
              {routes.map((r, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-1 text-xs font-mono font-bold text-slate-200">
                      {r.hops.map((h, hIdx) => (
                        <React.Fragment key={hIdx}>
                          <span
                            className={
                              h.startsWith('GS-')
                                ? 'text-sky-400'
                                : h === r.source_sat_id
                                ? 'text-cyan-300'
                                : 'text-emerald-400'
                            }
                          >
                            {h}
                          </span>
                          {hIdx < r.hops.length - 1 && <ArrowRight className="w-3 h-3 text-slate-600" />}
                        </React.Fragment>
                      ))}
                    </div>
                    <div className="text-[10px] font-mono text-slate-400">
                      Hops: {r.hops.length - 1} • Distance: {r.total_distance_km} km
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-xs font-mono font-bold text-emerald-400">{r.total_latency_ms} ms</div>
                    <div className="text-[9px] font-mono text-slate-500">{r.bottleneck_throughput_gbps} Gbps</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Pairwise Link Topology Table */}
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold font-mono uppercase text-slate-300 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-emerald-400" />
                Optical Cross-Link Topology ({filteredLinks.length})
              </h3>
              <div className="flex gap-1.5">
                {(['ACTIVE', 'IN_USE', 'ALL'] as const).map((f) => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    className={`px-2.5 py-0.5 rounded text-[10px] font-mono transition ${
                      filter === f
                        ? 'bg-cyan-500 text-slate-950 font-bold'
                        : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>

            <div className="border border-slate-800 rounded-xl overflow-hidden max-h-56 overflow-y-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 sticky top-0">
                  <tr>
                    <th className="p-2.5">Link Pair</th>
                    <th className="p-2.5">Distance</th>
                    <th className="p-2.5">Prop. Latency</th>
                    <th className="p-2.5">Bandwidth</th>
                    <th className="p-2.5">Status</th>
                    <th className="p-2.5">State</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                  {filteredLinks.map((l, idx) => (
                    <tr key={idx} className="hover:bg-slate-900/60 transition">
                      <td className="p-2.5 font-bold text-slate-200">
                        {l.sat_1_id} ↔ {l.sat_2_id}
                      </td>
                      <td className="p-2.5 text-slate-300">{l.distance_km} km</td>
                      <td className="p-2.5 text-emerald-400">{l.latency_ms} ms</td>
                      <td className="p-2.5 text-slate-400">{l.throughput_gbps} Gbps</td>
                      <td className="p-2.5">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                            l.status === 'ACTIVE'
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                              : l.status === 'OCCLUDED'
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                              : 'bg-slate-800 text-slate-500'
                          }`}
                        >
                          {l.status}
                        </span>
                      </td>
                      <td className="p-2.5">
                        {l.is_in_use ? (
                          <span className="text-[10px] text-cyan-400 font-bold flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                            ROUTING
                          </span>
                        ) : (
                          <span className="text-[10px] text-slate-600">STANDBY</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950 flex items-center justify-between text-xs font-mono text-slate-400">
          <div>Laser Inter-Satellite Links • Earth-Limb Geometric Occlusion Check</div>
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
