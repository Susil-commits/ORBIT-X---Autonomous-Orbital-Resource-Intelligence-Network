import React from 'react';
import { useConstellationSocket } from './hooks/useConstellationSocket';
import { useSimulationStore } from './hooks/useSimulationStore';
import { Header } from './components/Header';
import { GlobeView3D } from './components/GlobeView3D';
import { SatelliteList } from './components/SatelliteList';
import { MissionQueue } from './components/MissionQueue';
import { TelemetryHUD } from './components/TelemetryHUD';
import { ScheduleGantt } from './components/ScheduleGantt';
import { ExplainabilityModal } from './components/ExplainabilityModal';
import { BenchmarkModal } from './components/BenchmarkModal';
import { ScenarioDirectorModal } from './components/ScenarioDirectorModal';
import { TargetDispatchModal } from './components/TargetDispatchModal';
import { ISLNetworkHUD } from './components/ISLNetworkHUD';
import { MissionRAGDrawer } from './components/MissionRAGDrawer';

// Decision Intelligence Primary Views
import { AIAssistantHeroView } from './components/AIAssistantHeroView';
import { DecisionExplorerView } from './components/DecisionExplorerView';
import { DataDiscoveryLineageView } from './components/DataDiscoveryLineageView';
import { AgentTracesView } from './components/AgentTracesView';
import { MonitoringEvaluationView } from './components/MonitoringEvaluationView';

export const App: React.FC = () => {
  // Establish real-time WebSocket connection to backend
  useConstellationSocket();

  const activeTab = useSimulationStore((s) => s.activeTab);
  const showRAGDrawer = useSimulationStore((s) => s.showRAGDrawer);
  const setShowRAGDrawer = useSimulationStore((s) => s.setShowRAGDrawer);

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden select-none">
      {/* Top Header, Navigation & Decision Console Controls */}
      <Header />

      {/* Main Dynamic View Area */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Tab 1: Hero AI Assistant ("Ask ORBIT-X" 10-Step Decision Workflow) */}
        {activeTab === 'assistant' && <AIAssistantHeroView />}

        {/* Tab 2: Decision Explorer (Candidates, SHAP, Constraints, Solvers) */}
        {activeTab === 'decision' && <DecisionExplorerView />}

        {/* Tab 3: Data Discovery & Lineage (Semantic Catalog, Quality, Provenance DAG) */}
        {activeTab === 'data' && <DataDiscoveryLineageView />}

        {/* Tab 4: Agent Traces & MCP (Planner, Tool Execution Waterfall, Trust/Refusal) */}
        {activeTab === 'traces' && <AgentTracesView />}

        {/* Tab 5: Monitoring & Evaluation (Live KPIs, Ablation Studies, SLOs) */}
        {activeTab === 'monitoring' && <MonitoringEvaluationView />}

        {/* Tab 6: Simulation Digital Twin (Contained 3D Evaluation Domain) */}
        {activeTab === 'simulation' && (
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
        )}
      </div>

      {/* Decision Explainability Inspector Modal */}
      <ExplainabilityModal />

      {/* Scheduler Benchmark Comparison Modal */}
      <BenchmarkModal />

      {/* Extreme Scenario Director (Evaluation) */}
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
