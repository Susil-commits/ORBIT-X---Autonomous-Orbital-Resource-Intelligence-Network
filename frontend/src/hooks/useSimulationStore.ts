import { create } from 'zustand';
import type {
  ConstellationTick,
  DecisionExplanation,
  BenchmarkResult,
  AuctionResult,
  ScenarioType,
  TargetDispatchRequest,
} from '../types';

interface SimulationStore {
  tickData: ConstellationTick | null;
  selectedSatelliteId: string | null;
  selectedMissionId: string | null;
  showExplainModal: boolean;
  showBenchmarkModal: boolean;
  showAuctionModal: boolean;
  showScenarioModal: boolean;
  showDispatchModal: boolean;
  showISLModal: boolean;
  showRAGDrawer: boolean;
  constellationSource: 'synthetic' | 'celestrak_real';
  dispatchCoordinates: { lat: number; lon: number } | null;
  activeExplanation: DecisionExplanation | null;
  benchmarkResults: BenchmarkResult[] | null;
  isBenchmarking: boolean;
  auctionResults: AuctionResult[] | null;
  isLoadingAuctions: boolean;
  isConnected: boolean;
  
  // Modal Setters
  setTickData: (data: ConstellationTick) => void;
  setSelectedSatelliteId: (id: string | null) => void;
  setSelectedMissionId: (id: string | null) => void;
  setShowExplainModal: (show: boolean) => void;
  setShowBenchmarkModal: (show: boolean) => void;
  setShowAuctionModal: (show: boolean) => void;
  setShowScenarioModal: (show: boolean) => void;
  setShowDispatchModal: (show: boolean) => void;
  setShowISLModal: (show: boolean) => void;
  setShowRAGDrawer: (show: boolean) => void;
  setDispatchCoordinates: (coords: { lat: number; lon: number } | null) => void;
  setIsConnected: (connected: boolean) => void;
  
  // API Actions
  startSim: () => Promise<void>;
  pauseSim: () => Promise<void>;
  stepSim: () => Promise<void>;
  setSpeed: (speed: number) => Promise<void>;
  resetSim: () => Promise<void>;
  switchConstellationSource: (source: 'synthetic' | 'celestrak_real') => Promise<void>;
  injectFault: (satId: string, faultType: string) => Promise<void>;
  clearFaults: (satId?: string) => Promise<void>;
  addRandomMission: () => Promise<void>;
  fetchExplanation: (missionId: string) => Promise<void>;
  runBenchmarks: () => Promise<void>;
  fetchAuctions: () => Promise<void>;
  triggerScenario: (type: ScenarioType) => Promise<void>;
  resetScenario: () => Promise<void>;
  dispatchTarget: (req: TargetDispatchRequest) => Promise<void>;
  triggerAgentHealing: () => Promise<any>;
  fetchISSVerification: () => Promise<any>;
  exportDossier: () => void;
}

const API_BASE = 'http://localhost:8000';

export const useSimulationStore = create<SimulationStore>((set, get) => ({
  tickData: null,
  selectedSatelliteId: null,
  selectedMissionId: null,
  showExplainModal: false,
  showBenchmarkModal: false,
  showAuctionModal: false,
  showScenarioModal: false,
  showDispatchModal: false,
  showISLModal: false,
  showRAGDrawer: false,
  constellationSource: 'synthetic',
  dispatchCoordinates: null,
  activeExplanation: null,
  benchmarkResults: null,
  isBenchmarking: false,
  auctionResults: null,
  isLoadingAuctions: false,
  isConnected: false,

  setTickData: (data) => {
    const src = (data.data_source as any) || (data.satellites?.[0]?.data_source as any) || 'synthetic';
    set({ tickData: data, constellationSource: src });
  },
  setSelectedSatelliteId: (id) => set({ selectedSatelliteId: id }),
  setSelectedMissionId: (id) => set({ selectedMissionId: id }),
  setShowExplainModal: (show) => set({ showExplainModal: show }),
  setShowBenchmarkModal: (show) => set({ showBenchmarkModal: show }),
  setShowAuctionModal: (show) => set({ showAuctionModal: show }),
  setShowScenarioModal: (show) => set({ showScenarioModal: show }),
  setShowDispatchModal: (show) => set({ showDispatchModal: show }),
  setShowISLModal: (show) => set({ showISLModal: show }),
  setShowRAGDrawer: (show) => set({ showRAGDrawer: show }),
  setDispatchCoordinates: (coords) => set({ dispatchCoordinates: coords }),
  setIsConnected: (connected) => set({ isConnected: connected }),

  startSim: async () => {
    try {
      await fetch(`${API_BASE}/api/simulation/start`, { method: 'POST' });
    } catch (e) {
      console.error('Failed to start simulation', e);
    }
  },

  pauseSim: async () => {
    try {
      await fetch(`${API_BASE}/api/simulation/pause`, { method: 'POST' });
    } catch (e) {
      console.error('Failed to pause simulation', e);
    }
  },

  stepSim: async () => {
    try {
      const res = await fetch(`${API_BASE}/api/simulation/step?dt=1.0`, { method: 'POST' });
      const data = await res.json();
      set({ tickData: data });
    } catch (e) {
      console.error('Failed to step simulation', e);
    }
  },

  setSpeed: async (speed: number) => {
    try {
      await fetch(`${API_BASE}/api/simulation/speed?speed=${speed}`, { method: 'POST' });
      const currentTick = get().tickData;
      if (currentTick) {
        set({ tickData: { ...currentTick, speed_multiplier: speed } });
      }
    } catch (e) {
      console.error('Failed to set speed', e);
    }
  },

  resetSim: async () => {
    try {
      const res = await fetch(`${API_BASE}/api/simulation/reset`, { method: 'POST' });
      const data = await res.json();
      set({ tickData: data });
    } catch (e) {
      console.error('Failed to reset simulation', e);
    }
  },

  switchConstellationSource: async (source: 'synthetic' | 'celestrak_real') => {
    try {
      const res = await fetch(`${API_BASE}/api/constellation/switch_source?source=${source}`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to switch constellation data source');
      set({ constellationSource: source });
    } catch (e) {
      console.error('Failed to switch constellation source', e);
    }
  },

  injectFault: async (satId: string, faultType: string) => {
    try {
      await fetch(`${API_BASE}/api/simulation/inject_fault?sat_id=${satId}&fault_type=${faultType}`, {
        method: 'POST',
      });
    } catch (e) {
      console.error('Failed to inject fault', e);
    }
  },

  clearFaults: async (satId?: string) => {
    try {
      const url = satId
        ? `${API_BASE}/api/simulation/clear_faults?sat_id=${satId}`
        : `${API_BASE}/api/simulation/clear_faults`;
      await fetch(url, { method: 'POST' });
    } catch (e) {
      console.error('Failed to clear faults', e);
    }
  },

  addRandomMission: async () => {
    try {
      await fetch(`${API_BASE}/api/missions/random`, { method: 'POST' });
    } catch (e) {
      console.error('Failed to add random mission', e);
    }
  },

  fetchExplanation: async (missionId: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/missions/explain/${missionId}`);
      if (res.ok) {
        const data = await res.json();
        set({ activeExplanation: data, showExplainModal: true });
      }
    } catch (e) {
      console.error('Failed to fetch explanation', e);
    }
  },

  runBenchmarks: async () => {
    set({ isBenchmarking: true, showBenchmarkModal: true });
    try {
      const res = await fetch(`${API_BASE}/api/benchmarks/run`);
      const data = await res.json();
      set({ benchmarkResults: data, isBenchmarking: false });
    } catch (e) {
      console.error('Failed to run benchmarks', e);
      set({ isBenchmarking: false });
    }
  },

  fetchAuctions: async () => {
    set({ isLoadingAuctions: true, showAuctionModal: true });
    try {
      const res = await fetch(`${API_BASE}/api/multi-agent/auction`);
      const data = await res.json();
      set({ auctionResults: data, isLoadingAuctions: false });
    } catch (e) {
      console.error('Failed to fetch auctions', e);
      set({ isLoadingAuctions: false });
    }
  },

  triggerScenario: async (type: ScenarioType) => {
    try {
      const res = await fetch(`${API_BASE}/api/scenarios/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_type: type }),
      });
      const data = await res.json();
      const currentTick = get().tickData;
      if (currentTick) {
        set({ tickData: { ...currentTick, active_scenario: data } });
      }
    } catch (e) {
      console.error('Failed to trigger scenario', e);
    }
  },

  resetScenario: async () => {
    try {
      const res = await fetch(`${API_BASE}/api/scenarios/reset`, { method: 'POST' });
      const data = await res.json();
      const currentTick = get().tickData;
      if (currentTick) {
        set({ tickData: { ...currentTick, active_scenario: data } });
      }
    } catch (e) {
      console.error('Failed to reset scenario', e);
    }
  },

  dispatchTarget: async (req: TargetDispatchRequest) => {
    try {
      await fetch(`${API_BASE}/api/missions/dispatch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
      });
      set({ showDispatchModal: false, dispatchCoordinates: null });
    } catch (e) {
      console.error('Failed to dispatch target', e);
    }
  },

  triggerAgentHealing: async () => {
    try {
      const res = await fetch(`${API_BASE}/api/ai/agent/inspect_and_heal`, {
        method: 'POST',
      });
      return await res.json();
    } catch (e) {
      console.error('Failed to trigger self-healing agent', e);
      return null;
    }
  },

  fetchISSVerification: async () => {
    try {
      const res = await fetch(`${API_BASE}/api/constellation/iss_verification`);
      return await res.json();
    } catch (e) {
      console.error('Failed to fetch ISS verification', e);
      return null;
    }
  },

  exportDossier: () => {
    const tick = get().tickData;
    if (!tick) return;
    const dossier = {
      system: 'ORBIT-X Autonomous Constellation Network',
      exported_at: new Date().toISOString(),
      sim_time_s: tick.sim_time_s,
      wall_clock_iso: tick.wall_clock_iso,
      data_source: tick.data_source || 'synthetic',
      metrics: tick.metrics_summary,
      active_scenario: tick.active_scenario,
      active_maneuvers: tick.active_maneuvers,
      isl_mesh: tick.isl_mesh,
      satellites: tick.satellites.map((s) => ({
        id: s.id,
        name: s.name,
        norad_id: s.norad_id,
        data_source: s.data_source,
        health: s.health_status,
        battery_soc_pct: Math.round(s.battery.soc * 100),
        storage_gb: s.onboard_storage_used_gb,
        active_task: s.active_task_type,
        geodetic: s.geodetic,
      })),
      missions: {
        active: tick.active_missions,
        pending: tick.pending_missions,
        completed: tick.completed_missions,
      },
    };

    const blob = new Blob([JSON.stringify(dossier, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ORBIT-X_Constellation_Dossier_Tick_${tick.tick}.json`;
    a.click();
    URL.revokeObjectURL(url);
  },
}));
