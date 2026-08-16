import React, { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars, Html, Line } from '@react-three/drei';
import * as THREE from 'three';
import { useSimulationStore } from '../hooks/useSimulationStore';
import type { SatelliteState, GroundStation, MissionRequest, GeodeticLocation, ISLLink } from '../types';


// Scale factor: Earth Radius (6378 km) = 2.0 units in 3D
const EARTH_RADIUS_3D = 2.0;
const EARTH_RADIUS_KM = 6378.137;

function kmTo3D(km: number): number {
  return (km / EARTH_RADIUS_KM) * EARTH_RADIUS_3D;
}

function geodeticTo3D(geo: GeodeticLocation, altKm: number = 0): [number, number, number] {
  const latRad = (geo.lat * Math.PI) / 180.0;
  const lonRad = (geo.lon * Math.PI) / 180.0;
  const r = kmTo3D(EARTH_RADIUS_KM + altKm);
  
  // In Three.js coordinate system: Y is Up (North pole), X and Z in equatorial plane
  const x = r * Math.cos(latRad) * Math.sin(lonRad);
  const y = r * Math.sin(latRad);
  const z = r * Math.cos(latRad) * Math.cos(lonRad);
  return [x, y, z];
}

// 3D Point to Geodetic conversion (for click-to-pin target dispatching)
function point3DToGeodetic(point: THREE.Vector3): { lat: number; lon: number } {
  const norm = point.clone().normalize();
  const lat = Math.asin(norm.y) * (180.0 / Math.PI);
  const lon = Math.atan2(norm.x, norm.z) * (180.0 / Math.PI);
  return {
    lat: Math.round(lat * 100) / 100,
    lon: Math.round(lon * 100) / 100,
  };
}

// Procedural Earth Texture
function createEarthCanvasTexture(): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext('2d')!;
  
  // Deep Ocean Blue Base
  const grad = ctx.createLinearGradient(0, 0, 0, 512);
  grad.addColorStop(0, '#0a192f');
  grad.addColorStop(0.5, '#0d254c');
  grad.addColorStop(1, '#0a192f');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 1024, 512);

  // Continental landmasses sketch / latitude grid lines
  ctx.strokeStyle = 'rgba(56, 189, 248, 0.2)';
  ctx.lineWidth = 1;
  for (let lat = -80; lat <= 80; lat += 20) {
    const y = ((90 - lat) / 180) * 512;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(1024, y);
    ctx.stroke();
  }
  for (let lon = -180; lon <= 180; lon += 30) {
    const x = ((lon + 180) / 360) * 1024;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, 512);
    ctx.stroke();
  }

  // Equator highlight
  ctx.strokeStyle = 'rgba(0, 240, 255, 0.4)';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(0, 256);
  ctx.lineTo(1024, 256);
  ctx.stroke();

  // Continents simplified glow polygons
  ctx.fillStyle = 'rgba(16, 185, 129, 0.18)';
  // North America
  ctx.beginPath();
  ctx.ellipse(280, 160, 90, 60, 0.2, 0, Math.PI * 2);
  ctx.fill();
  // South America
  ctx.beginPath();
  ctx.ellipse(340, 320, 50, 90, 0.1, 0, Math.PI * 2);
  ctx.fill();
  // Eurasia
  ctx.beginPath();
  ctx.ellipse(650, 160, 140, 70, 0, 0, Math.PI * 2);
  ctx.fill();
  // Africa
  ctx.beginPath();
  ctx.ellipse(560, 280, 60, 90, 0, 0, Math.PI * 2);
  ctx.fill();
  // Australia
  ctx.beginPath();
  ctx.ellipse(820, 350, 50, 40, 0, 0, Math.PI * 2);
  ctx.fill();

  const texture = new THREE.CanvasTexture(canvas);
  return texture;
}

// 3D Earth Mesh with Atmosphere Glow & Click-to-Dispatch Listener
const EarthMesh: React.FC = () => {
  const texture = useMemo(() => createEarthCanvasTexture(), []);
  const setDispatchCoords = useSimulationStore((s) => s.setDispatchCoordinates);
  const setShowDispatchModal = useSimulationStore((s) => s.setShowDispatchModal);

  const handleEarthClick = (e: any) => {
    e.stopPropagation();
    if (e.point) {
      const geo = point3DToGeodetic(e.point);
      setDispatchCoords(geo);
      setShowDispatchModal(true);
    }
  };

  return (
    <group>
      {/* Core Earth */}
      <mesh onClick={handleEarthClick}>
        <sphereGeometry args={[EARTH_RADIUS_3D, 64, 64]} />
        <meshStandardMaterial
          map={texture}
          roughness={0.6}
          metalness={0.2}
          emissive="#031024"
          emissiveIntensity={0.4}
        />
      </mesh>

      {/* Atmosphere Glow Halo */}
      <mesh raycast={() => null}>
        <sphereGeometry args={[EARTH_RADIUS_3D * 1.03, 32, 32]} />
        <meshBasicMaterial
          color="#00f0ff"
          transparent
          opacity={0.08}
          side={THREE.BackSide}
        />
      </mesh>

    </group>
  );
};

// Orbital Plane Rings
const OrbitalRings: React.FC = () => {
  const r = kmTo3D(EARTH_RADIUS_KM + 550);
  const planes = [
    { raan: 0, color: 'rgba(0, 240, 255, 0.35)' },
    { raan: 120, color: 'rgba(99, 102, 241, 0.35)' },
    { raan: 240, color: 'rgba(16, 185, 129, 0.35)' },
  ];

  return (
    <group>
      {planes.map((p, idx) => {
        const points: [number, number, number][] = [];
        const numPoints = 72;
        const incRad = (53.0 * Math.PI) / 180.0;
        const raanRad = (p.raan * Math.PI) / 180.0;

        for (let i = 0; i <= numPoints; i++) {
          const u = (i / numPoints) * 2 * Math.PI;
          const xp = r * Math.cos(u);
          const yp = r * Math.sin(u);
          
          const x = xp * Math.cos(raanRad) - yp * Math.sin(raanRad) * Math.cos(incRad);
          const z = xp * Math.sin(raanRad) + yp * Math.cos(raanRad) * Math.cos(incRad);
          const y = yp * Math.sin(incRad);
          points.push([x, y, z]);
        }

        return (
          <Line
            key={idx}
            points={points}
            color={p.color}
            lineWidth={1.2}
            transparent
            opacity={0.6}
          />
        );
      })}
    </group>
  );
};

// 3D Satellite Node with Solar Panels and FOV Sensor Cone
const SatelliteNode: React.FC<{ sat: SatelliteState; isSelected: boolean }> = ({ sat, isSelected }) => {
  const setSelectedSatId = useSimulationStore((s) => s.setSelectedSatelliteId);
  const satPos = useMemo(() => geodeticTo3D(sat.geodetic, sat.geodetic.alt), [sat.geodetic]);
  const groundPos = useMemo(() => geodeticTo3D(sat.geodetic, 0), [sat.geodetic]);

  const isFault = sat.health_status === 'CRITICAL_FAULT';
  const isDegraded = sat.health_status === 'DEGRADED';
  const isImaging = sat.active_task_type === 'IMAGING';
  const isDownlink = sat.active_task_type === 'DOWNLINK';

  let satColor = '#00f0ff';
  if (isFault) satColor = '#f43f5e';
  else if (isDegraded) satColor = '#f59e0b';
  else if (isImaging) satColor = '#10b981';
  else if (isDownlink) satColor = '#a855f7';

  return (
    <group position={satPos}>
      {/* Central Satellite Body */}
      <mesh onClick={(e) => { e.stopPropagation(); setSelectedSatId(sat.id); }}>
        <boxGeometry args={[0.08, 0.08, 0.08]} />
        <meshStandardMaterial
          color={satColor}
          emissive={satColor}
          emissiveIntensity={isSelected ? 1.0 : 0.5}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>

      {/* Solar Wings */}
      <mesh position={[0.1, 0, 0]}>
        <boxGeometry args={[0.12, 0.04, 0.01]} />
        <meshStandardMaterial color="#1e3a8a" metalness={0.9} roughness={0.1} />
      </mesh>
      <mesh position={[-0.1, 0, 0]}>
        <boxGeometry args={[0.12, 0.04, 0.01]} />
        <meshStandardMaterial color="#1e3a8a" metalness={0.9} roughness={0.1} />
      </mesh>

      {/* Sensor FOV Nadir Line */}
      {(isSelected || isImaging) && (
        <Line
          points={[[0, 0, 0], [groundPos[0] - satPos[0], groundPos[1] - satPos[1], groundPos[2] - satPos[2]]]}
          color={isImaging ? '#10b981' : '#00f0ff'}
          lineWidth={1.5}
          transparent
          opacity={0.7}
        />
      )}

      {/* HTML Label Tag */}
      <Html distanceFactor={14} position={[0, 0.12, 0]} center>
        <div
          onClick={(e) => { e.stopPropagation(); setSelectedSatId(sat.id); }}
          className={`cursor-pointer px-1.5 py-0.5 rounded text-[9px] font-mono whitespace-nowrap backdrop-blur-md border transition-all ${
            isSelected
              ? 'bg-cyan-500 text-slate-950 font-bold border-white shadow-lg'
              : 'bg-slate-900/80 text-cyan-300 border-cyan-500/40 hover:border-cyan-400'
          }`}
        >
          {sat.id} • {Math.round(sat.battery.soc * 100)}%
        </div>
      </Html>
    </group>
  );
};

// Ground Stations on Earth Surface
const GroundStationMarker: React.FC<{ station: GroundStation }> = ({ station }) => {
  const pos = useMemo(() => geodeticTo3D(station.location, 0), [station.location]);

  return (
    <group position={pos}>
      <mesh>
        <cylinderGeometry args={[0.02, 0.04, 0.03, 8]} />
        <meshStandardMaterial
          color={station.is_active ? '#38bdf8' : '#64748b'}
          emissive={station.is_active ? '#38bdf8' : '#334155'}
          emissiveIntensity={station.is_active ? 0.6 : 0.1}
        />
      </mesh>
      <Html distanceFactor={16} position={[0, 0.06, 0]} center>
        <div
          className={`px-1 py-0.5 rounded border text-[8px] font-mono whitespace-nowrap ${
            station.is_active
              ? 'bg-slate-900/90 border-sky-400/40 text-sky-200'
              : 'bg-slate-950/90 border-red-500/40 text-red-400 line-through opacity-70'
          }`}
        >
          📡 {station.id} {station.is_active ? '' : '(OFFLINE)'}
        </div>
      </Html>
    </group>
  );
};

// Ground Observation Target Markers
const MissionTargetMarker: React.FC<{ mission: MissionRequest }> = ({ mission }) => {
  const fetchExp = useSimulationStore((s) => s.fetchExplanation);
  const pos = useMemo(() => geodeticTo3D(mission.target_location, 0), [mission.target_location]);

  let targetColor = '#00f0ff';
  if (mission.priority >= 5) targetColor = '#f43f5e';
  else if (mission.priority >= 4) targetColor = '#f59e0b';
  else if (mission.status === 'COMPLETED') targetColor = '#10b981';

  return (
    <group position={pos}>
      <mesh onClick={(e) => { e.stopPropagation(); fetchExp(mission.id); }}>
        <sphereGeometry args={[0.03, 12, 12]} />
        <meshBasicMaterial color={targetColor} />
      </mesh>
      <Html distanceFactor={16} position={[0, 0.06, 0]} center>
        <div
          onClick={(e) => { e.stopPropagation(); fetchExp(mission.id); }}
          className="cursor-pointer px-1 py-0.5 rounded bg-slate-900/90 border border-amber-400/50 text-[8px] font-mono text-amber-300 hover:scale-105 transition shadow-md"
        >
          🎯 P{mission.priority} • {mission.name.slice(0, 16)}...
        </div>
      </Html>
    </group>
  );
};

// Intersatellite Laser Links (ISL Mesh) Beams
const ISLLaserMesh: React.FC<{ satellites: SatelliteState[]; links?: ISLLink[] }> = ({
  satellites,
  links = [],
}) => {
  const satPosMap = useMemo(() => {
    const map: Record<string, [number, number, number]> = {};
    satellites.forEach((s) => {
      map[s.id] = geodeticTo3D(s.geodetic, s.geodetic.alt);
    });
    return map;
  }, [satellites]);

  const activeLinks = useMemo(() => {
    return links.filter((l) => l.status === 'ACTIVE' && satPosMap[l.sat_1_id] && satPosMap[l.sat_2_id]);
  }, [links, satPosMap]);

  return (
    <group>
      {activeLinks.map((lk, idx) => {
        const from = satPosMap[lk.sat_1_id];
        const to = satPosMap[lk.sat_2_id];
        return (
          <Line
            key={idx}
            points={[from, to]}
            color={lk.is_in_use ? '#10b981' : '#00f0ff'}
            lineWidth={lk.is_in_use ? 2.2 : 0.8}
            transparent
            opacity={lk.is_in_use ? 0.85 : 0.25}
          />
        );
      })}
    </group>
  );
};

// Laser Downlink Beams (Active Comms)
const DownlinkLaserBeams: React.FC<{ satellites: SatelliteState[]; stations: GroundStation[] }> = ({
  satellites,
  stations,
}) => {
  const activeDownlinks = useMemo(() => {
    const beams: Array<{ from: [number, number, number]; to: [number, number, number] }> = [];
    satellites.forEach((sat) => {
      if (sat.active_task_type === 'DOWNLINK') {
        const satPos = geodeticTo3D(sat.geodetic, sat.geodetic.alt);
        stations.forEach((gs) => {
          if (gs.is_active) {
            const gsPos = geodeticTo3D(gs.location, 0);
            beams.push({ from: satPos, to: gsPos });
          }
        });
      }
    });
    return beams;
  }, [satellites, stations]);

  return (
    <group>
      {activeDownlinks.map((beam, idx) => (
        <Line
          key={idx}
          points={[beam.from, beam.to]}
          color="#c084fc"
          lineWidth={2.5}
          transparent
          opacity={0.9}
        />
      ))}
    </group>
  );
};

// Orbital Debris Field Marker (when Debris Conjunction scenario is active)
const DebrisCloudMarker: React.FC<{ position?: { x: number; y: number; z: number } | null }> = ({ position }) => {
  if (!position) return null;
  const p3d: [number, number, number] = [kmTo3D(position.x), kmTo3D(position.y), kmTo3D(position.z)];

  return (
    <group position={p3d}>
      <mesh>
        <octahedronGeometry args={[0.06, 0]} />
        <meshStandardMaterial color="#f43f5e" emissive="#f43f5e" emissiveIntensity={1.0} wireframe />
      </mesh>
      <Html distanceFactor={14} position={[0, 0.08, 0]} center>
        <div className="px-1.5 py-0.5 rounded bg-rose-950/90 border border-rose-500 text-[8px] font-mono text-rose-300 animate-pulse whitespace-nowrap">
          ⚠️ DEBRIS FRAG #COSMOS-2251
        </div>
      </Html>
    </group>
  );
};

export const GlobeView3D: React.FC = () => {
  const tickData = useSimulationStore((s) => s.tickData);
  const selectedSatId = useSimulationStore((s) => s.selectedSatelliteId);

  const satellites = tickData?.satellites || [];

  const groundStations = tickData?.ground_stations || [];
  const islLinks = tickData?.isl_mesh?.links || [];
  const debrisPos = tickData?.active_scenario?.debris_position;

  const missions = useMemo(() => {
    const active = tickData?.active_missions || [];
    const pending = tickData?.pending_missions || [];
    return [...active, ...pending];
  }, [tickData]);

  return (
    <div className="relative w-full h-full bg-slate-950 overflow-hidden">
      <Canvas
        camera={{ position: [0, 2.5, 4.5], fov: 45 }}
        style={{ width: '100%', height: '100%' }}
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 3, 5]} intensity={1.5} color="#ffffff" />
        <pointLight position={[-5, -3, -5]} intensity={0.4} color="#00f0ff" />
        <Stars radius={50} depth={50} count={2000} factor={4} saturation={0.5} fade speed={1} />

        <EarthMesh />
        <OrbitalRings />

        {satellites.map((sat) => (
          <SatelliteNode
            key={sat.id}
            sat={sat}
            isSelected={sat.id === selectedSatId}
          />
        ))}

        {groundStations.map((gs) => (
          <GroundStationMarker key={gs.id} station={gs} />
        ))}

        {missions.map((m) => (
          <MissionTargetMarker key={m.id} mission={m} />
        ))}

        <ISLLaserMesh satellites={satellites} links={islLinks} />
        <DownlinkLaserBeams satellites={satellites} stations={groundStations} />
        <DebrisCloudMarker position={debrisPos} />

        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={2.4}
          maxDistance={10}
          rotateSpeed={0.6}
        />
      </Canvas>

      {/* Top Helper Hint */}
      <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-slate-900/80 backdrop-blur-md border border-cyan-500/30 px-3 py-1 rounded-full text-[10px] font-mono text-cyan-300 pointer-events-none flex items-center gap-2 shadow-lg z-10">
        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
        <span>Click anywhere on 3D Earth to drop an observation target</span>
      </div>

      {/* Bottom HUD Legend */}
      <div className="absolute bottom-4 left-4 hud-panel px-3 py-2 rounded-lg text-xs font-mono flex items-center gap-4 pointer-events-none z-10">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-cyan-400" />
          <span>Nominal</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          <span>Imaging / ISL Relay</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-purple-400" />
          <span>X-Band Downlink</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-rose-500" />
          <span>Critical / Debris</span>
        </div>
      </div>
    </div>
  );
};
