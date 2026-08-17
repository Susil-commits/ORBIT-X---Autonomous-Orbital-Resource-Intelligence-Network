import React from 'react';
import { useConstellationSocket } from './hooks/useConstellationSocket';
import { useSimulationStore } from './hooks/useSimulationStore';
import { Header } from './components/Header';
import { FlightDirectorCommentaryBar } from './components/FlightDirectorCommentaryBar';
import { GlobeView3D } from './components/GlobeView3D';
import { SatelliteList } from './components/SatelliteList';
import { MissionQueue } from './components/MissionQueue';
import { TelemetryHUD } from './components/TelemetryHUD';
import { ScheduleGantt } from './components/ScheduleGantt';
import { ExplainabilityModal } from './components/ExplainabilityModal';
import { BenchmarkModal } from './components/BenchmarkModal';
import { MultiAgentModal } from './components/MultiAgentModal';
import { ScenarioDirectorModal } from './components/ScenarioDirectorModal';
import { TargetDispatchModal } from './components/TargetDispatchModal';
import { ISLNetworkHUD } from './components/ISLNetworkHUD';
import { MissionRAGDrawer } from './components/MissionRAGDrawer';

export const App: React.FC = () => {
  // Establish real-time WebSocket connection to backend
  useConstellationSocket();

  const showRAGDrawer = useSimulationStore((s) => s.showRAGDrawer);
  const setShowRAGDrawer = useSimulationStore((s) => s.setShowRAGDrawer);

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden select-none">
      {/* Top Header & Simulation Controls */}
      <Header />

      {/* Flight Director Live Tactical Commentary Bar */}
      <FlightDirectorCommentaryBar />

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Constellation Satellite Node Cards */}
        <aside className="w-72 flex-shrink-0 h-full">
          <SatelliteList />
        </aside>

        {/* Center: 3D Interactive Globe & Bottom Telemetry / Gantt HUD */}
        <main className="flex-1 flex flex-col h-full overflow-hidden relative">
          {/* Top: 3D Earth Globe Canvas */}
          <div className="flex-1 relative">
            <GlobeView3D />
          </div>

          {/* Bottom HUD: Telemetry Sensor Deck + Schedule Gantt */}
          <div className="h-56 flex-shrink-0 grid grid-cols-1 lg:grid-cols-2">
            <TelemetryHUD />
            <ScheduleGantt />
          </div>
        </main>

        {/* Right: Mission Intake & Scheduled Queue */}
        <aside className="w-80 flex-shrink-0 h-full">
          <MissionQueue />
        </aside>
      </div>

      {/* Decision Explainability Reasoning Inspector */}
      <ExplainabilityModal />

      {/* Scheduler Benchmark Comparison Modal */}
      <BenchmarkModal />

      {/* Multi-Agent Cooperative Auction Ledger */}
      <MultiAgentModal />

      {/* Extreme Space Mission Scenario Director */}
      <ScenarioDirectorModal />

      {/* Point-and-Click Target Dispatch Deck */}
      <TargetDispatchModal />

      {/* Intersatellite Optical Laser Mesh Topology HUD */}
      <ISLNetworkHUD />

      {/* Grounded Decision History RAG Drawer */}
      <MissionRAGDrawer isOpen={showRAGDrawer} onClose={() => setShowRAGDrawer(false)} />
    </div>
  );
};

export default App;
