# ORBIT-X Frontend Dashboard

> **The real-time operational mission control interface for ORBIT-X.** It provides operators and autonomous agents with interactive 3D constellation orbital visualization, live telemetry monitoring, governed decision traces, and FastMCP-powered conversational workflows.

<div align="center">

[![React 19](https://img.shields.io/badge/React-19.0-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![Three.js](https://img.shields.io/badge/Three.js-3D%20Graphics-000000?style=flat-square&logo=threedotjs&logoColor=white)](https://threejs.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3.4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)

</div>

---

## 🛰️ Dashboard Capabilities

1. **3D Interactive Orbit & Globe View (`GlobeView.tsx`)**:
   - Real-time Three.js / Globe.gl 3D Earth visualization rendering active satellite orbits, ground station contact cones, and inter-satellite communication links (ISL).
2. **Autonomous Decision & Lineage Inspector (`DecisionTrace.tsx`)**:
   - Interactive visualization of the 7-stage decision pipeline showing data contract validation, FastMCP tool execution, Cross-Attention utility scores, CP-SAT solver constraint checks, and TreeSHAP feature attributions.
3. **Telemetry & Spacecraft Health Monitor (`TelemetryView.tsx`)**:
   - High-frequency charts displaying battery state-of-charge (SoC), Stefan-Boltzmann thermal curves, solar irradiance, and Isolation Forest anomaly scores.
4. **Governed Agent Chat & Mission Dispatch (`AgentChat.tsx`)**:
   - Natural language interface for querying constellation state, triaging subsystem alerts, and dispatching missions with anti-hallucination and refusal status badges.

---

## 🛠️ Tech Stack

- **Framework:** React 19 with TypeScript 5
- **Build Tool:** Vite 6
- **3D Visualization:** Three.js / Globe.gl
- **Icons & UI:** Lucide React, TailwindCSS
- **State & Data Fetching:** React Hooks, WebSocket real-time streams, Axios / Fetch API

---

## ⚡ Quick Start

```bash
# Navigate to frontend directory
cd frontend

# Install node dependencies
npm install

# Start Vite development server
npm run dev
```

The web dashboard will be accessible at `http://localhost:5173`.
