"""FastAPI Application Entrypoint with WebSocket Streaming for ORBIT-X."""

import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Set

from app.simulation.simulator import get_simulator
from app.api.routes_simulation import router as sim_router
from app.api.routes_missions import router as missions_router
from app.api.routes_benchmarks import router as benchmarks_router
from app.api.routes_multi_agent import router as multi_agent_router


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast_json(self, data: dict):
        dead_connections = []
        for connection in list(self.active_connections):
            try:
                await connection.send_text(json.dumps(data))
            except Exception:
                dead_connections.append(connection)
        for dead in dead_connections:
            self.active_connections.discard(dead)


ws_manager = ConnectionManager()
_sim_loop_task: asyncio.Task = None


async def background_simulation_loop():
    """Continuous simulation loop broadcasting ticks to WebSocket clients."""
    sim = get_simulator()
    while True:
        try:
            if sim.is_running:
                # Step simulation by 1 real second * speed_multiplier
                tick_data = sim.step(dt_seconds=0.5)
                # Broadcast to connected clients
                if ws_manager.active_connections:
                    await ws_manager.broadcast_json(tick_data.model_dump())
            await asyncio.sleep(0.1)  # 10 Hz ticker
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in simulation loop: {e}")
            await asyncio.sleep(1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _sim_loop_task
    # Start simulation loop in background
    _sim_loop_task = asyncio.create_task(background_simulation_loop())
    yield
    if _sim_loop_task:
        _sim_loop_task.cancel()


app = FastAPI(
    title="ORBIT-X Backend",
    description="Autonomous Orbital Resource & Intelligence Network API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(sim_router)
app.include_router(missions_router)
app.include_router(benchmarks_router)
app.include_router(multi_agent_router)


@app.get("/")
async def root():
    return {
        "system": "ORBIT-X",
        "status": "ONLINE",
        "version": "1.0.0",
        "capabilities": [
            "Keplerian Orbital Propagator with J2 Precession & Eclipse Geometry",
            "Line-of-Sight Access & Ground-Station Elevation Model",
            "Battery Energy Intelligence & Lookahead SoC Forecasting",
            "Spacecraft Health AI (Isolation Forest Telemetry Anomaly Detection)",
            "Google OR-Tools CP-SAT Constellation Mission Optimizer",
            "Multi-Agent Cooperative Auction / Bidding Engine",
            "Pairwise Conjunction & Collision-Risk (TCA) Assessment",
            "Structured Decision Explainability Trails",
            "Real-time WebSocket Constellation Stream",
            "Comparative Benchmarks (CP-SAT vs Greedy EDF vs Random)",
        ],
    }


@app.websocket("/ws/constellation")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    sim = get_simulator()
    try:
        # Send initial snapshot immediately upon connection
        init_tick = sim.step(dt_seconds=0.0)
        await websocket.send_text(json.dumps(init_tick.model_dump()))
        while True:
            # Keep connection alive and listen for client messages
            msg = await websocket.receive_text()
            try:
                cmd = json.loads(msg)
                if cmd.get("action") == "step":
                    tick = sim.step(dt_seconds=cmd.get("dt", 1.0))
                    await websocket.send_text(json.dumps(tick.model_dump()))
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
