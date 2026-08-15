import { create } from 'zustand';
import type { ConstellationTick, DecisionExplanation, BenchmarkResult, AuctionResult } from '../types';

interface SimulationStore {
  tickData: ConstellationTick | null;
  selectedSatelliteId: string | null;
  selectedMissionId: string | null;
  showExplainModal: boolean;
  showBenchmarkModal: boolean;
  showAuctionModal: boolean;
  activeExplanation: DecisionExplanation | null;
  benchmarkResults: BenchmarkResult[] | null;
  isBenchmarking: boolean;
  auctionResults: AuctionResult[] | null;
  isLoadingAuctions: boolean;
  isConnected: boolean;
  
  // Actions
  setTickData: (data: ConstellationTick) => void;
  setSelectedSatelliteId: (id: string | null) => void;
  setSelectedMissionId: (id: string | null) => void;
  setShowExplainModal: (show: boolean) => void;
  setShowBenchmarkModal: (show: boolean) => void;
  setShowAuctionModal: (show: boolean) => void;
  setIsConnected: (connected: boolean) => void;
  
  // API Actions
  startSim: () => Promise<void>;
  pauseSim: () => Promise<void>;
  stepSim: () => Promise<void>;
  setSpeed: (speed: number) => Promise<void>;
  resetSim: () => Promise<void>;
  injectFault: (satId: string, faultType: string) => Promise<void>;
  clearFaults: (satId?: string) => Promise<void>;
  addRandomMission: () => Promise<void>;
  fetchExplanation: (missionId: string) => Promise<void>;
  runBenchmarks: () => Promise<void>;
  fetchAuctions: () => Promise<void>;
}

const API_BASE = 'http://localhost:8000';

export const useSimulationStore = create<SimulationStore>((set) => ({
  tickData: null,
  selectedSatelliteId: null,
  selectedMissionId: null,
  showExplainModal: false,
  showBenchmarkModal: false,
  showAuctionModal: false,
  activeExplanation: null,
  benchmarkResults: null,
  isBenchmarking: false,
  auctionResults: null,
  isLoadingAuctions: false,
  isConnected: false,

  setTickData: (data) => set({ tickData: data }),
  setSelectedSatelliteId: (id) => set({ selectedSatelliteId: id }),
  setSelectedMissionId: (id) => set({ selectedMissionId: id }),
  setShowExplainModal: (show) => set({ showExplainModal: show }),
  setShowBenchmarkModal: (show) => set({ showBenchmarkModal: show }),
  setShowAuctionModal: (show) => set({ showAuctionModal: show }),
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
      const res = await fetch(`${API_BASE}/api/simulation/step`, { method: 'POST' });
      const data = await res.json();
      set({ tickData: data });
    } catch (e) {
      console.error('Failed to step simulation', e);
    }
  },

  setSpeed: async (speed) => {
    try {
      await fetch(`${API_BASE}/api/simulation/speed`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ speed }),
      });
    } catch (e) {
      console.error('Failed to set speed', e);
    }
  },

  resetSim: async () => {
    try {
      await fetch(`${API_BASE}/api/simulation/reset`, { method: 'POST' });
      const res = await fetch(`${API_BASE}/api/simulation/state`);
      const data = await res.json();
      set({ tickData: data });
    } catch (e) {
      console.error('Failed to reset simulation', e);
    }
  },

  injectFault: async (satId, faultType) => {
    try {
      await fetch(`${API_BASE}/api/simulation/inject_fault`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ satellite_id: satId, fault_type: faultType }),
      });
    } catch (e) {
      console.error('Failed to inject fault', e);
    }
  },

  clearFaults: async (satId) => {
    try {
      const url = satId 
        ? `${API_BASE}/api/simulation/clear_faults?satellite_id=${satId}`
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
      const res = await fetch(`${API_BASE}/api/missions/${missionId}/explanation`);
      if (res.ok) {
        const exp = await res.json();
        set({ activeExplanation: exp, showExplainModal: true });
      }
    } catch (e) {
      console.error('Failed to fetch explanation', e);
    }
  },

  runBenchmarks: async () => {
    set({ isBenchmarking: true, showBenchmarkModal: true });
    try {
      const res = await fetch(`${API_BASE}/api/benchmarks/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed: 42, num_missions: 24, horizon_s: 5400 }),
      });
      if (res.ok) {
        const results = await res.json();
        set({ benchmarkResults: results });
      }
    } catch (e) {
      console.error('Failed to run benchmarks', e);
    } finally {
      set({ isBenchmarking: false });
    }
  },

  fetchAuctions: async () => {
    set({ isLoadingAuctions: true, showAuctionModal: true });
    try {
      const res = await fetch(`${API_BASE}/api/multi-agent/auction`);
      if (res.ok) {
        const results = await res.json();
        set({ auctionResults: results });
      }
    } catch (e) {
      console.error('Failed to fetch auction ledger', e);
    } finally {
      set({ isLoadingAuctions: false });
    }
  },
}));
