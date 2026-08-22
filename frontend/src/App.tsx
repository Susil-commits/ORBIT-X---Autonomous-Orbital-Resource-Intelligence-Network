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
import { AILabModal } from './components/AILabModal';

// AI-Native Primary Hero Views
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
  const setShowAILabModal = useSimulationStore((s) => s.setShowAILabModal);

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden select-none">
      {/* Top Header, Navigation & Simulation Controls */}
      <Header />

      {/* Flight Director Tactical Commentary Bar (Grounded Decision Summary) */}
      <FlightDirectorCommentaryBar />

      {/* Main Dynamic View Area */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Tab 1: Hero AI Assistant ("Ask ORBIT-X" 10-Step Workflow) */}
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

        {/* Tab 7: AI Lab & Model Cards */}
        {activeTab === 'ailab' && (
          <div className="flex-1 flex flex-col items-center justify-center p-8 bg-slate-950 text-center space-y-4">
            <div className="p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
              <span className="font-orbitron text-2xl font-bold">AI Lab & Training Studio</span>
            </div>
            <p className="text-sm text-slate-400 max-w-lg">
              Launch reproducible cross-attention training runs, inspect model cards, and evaluate neural vs CP-SAT scheduling.
            </p>
            <button
              onClick={() => setShowAILabModal(true)}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-slate-950 font-semibold text-xs shadow-lg shadow-cyan-500/20 transition cursor-pointer font-mono"
            >
              Open Interactive AI Lab Studio
            </button>
          </div>
        )}
      </div>

      {/* Decision Explainability Inspector Modal */}
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

      {/* Neural AI Lab & Fine-Tuning Studio Modal */}
      <AILabModal />
    </div>
  );
};

export default App;
