import os
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Set

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.database import init_db
from app.core.redis_client import redis_manager
from app.core.limiter import limiter
from app.simulation.simulator import get_simulator
from app.api.routes_simulation import router as sim_router
from app.api.routes_missions import router as missions_router
from app.api.routes_benchmarks import router as benchmarks_router
from app.api.routes_multi_agent import router as multi_agent_router
from app.api.routes_isl import router as isl_router
from app.api.routes_scenarios import router as scenarios_router
from app.api.routes_ai import router as ai_router
from app.api.routes_constellation_data import router as constellation_data_router


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
    """Continuous simulation loop broadcasting ticks to WebSocket clients and Redis."""
    sim = get_simulator()
    while True:
        try:
            if sim.is_running:
                # Step simulation asynchronously with non-blocking CP-SAT thread offload
                tick_data = await sim.step_async(dt_seconds=0.5)
                dumped = tick_data.model_dump()
                
                # Broadcast to connected WebSocket clients
                if ws_manager.active_connections:
                    await ws_manager.broadcast_json(dumped)
                    
                # Publish to Redis channel asynchronously (non-blocking, fails safe)
                await redis_manager.publish_event("constellation:ticks", dumped)
                await redis_manager.set_json("constellation:latest_tick", dumped, expire_seconds=30)
                
            await asyncio.sleep(0.1)  # 10 Hz ticker
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in simulation loop: {e}")
            await asyncio.sleep(1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _sim_loop_task
    # Initialize async database tables
    try:
        await init_db()
    except Exception as e:
        print(f"Warning: Database initialization skipped: {e}")
        
    # Connect async Redis
    await redis_manager.connect()
    
    # Start simulation loop in background
    _sim_loop_task = asyncio.create_task(background_simulation_loop())
    yield
    if _sim_loop_task:
        _sim_loop_task.cancel()
    await redis_manager.close()


app = FastAPI(
    title="ORBIT-X Backend",
    description="Autonomous Orbital Resource & Intelligence Network API",
    version="2.0.0",
    lifespan=lifespan,
)

# Rate Limiter Setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration with environment variable override and safe localhost defaults
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(sim_router)
app.include_router(missions_router)
app.include_router(benchmarks_router)
app.include_router(multi_agent_router)
app.include_router(isl_router)
app.include_router(scenarios_router)
app.include_router(ai_router)
app.include_router(constellation_data_router)


from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Check for compiled frontend distribution
frontend_dist_path = Path(__file__).resolve().parent.parent / "frontend_dist"
if not frontend_dist_path.exists():
    frontend_dist_path = Path("/app/frontend_dist")

if frontend_dist_path.exists() and (frontend_dist_path / "index.html").exists():
    assets_path = frontend_dist_path / "assets"
    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_path)), name="static_assets")

    @app.get("/")
    async def serve_root():
        return FileResponse(frontend_dist_path / "index.html")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json") or full_path.startswith("ws/"):
            return None
        file_target = frontend_dist_path / full_path
        if file_target.is_file():
            return FileResponse(file_target)
        return FileResponse(frontend_dist_path / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "system": "ORBIT-X",
            "status": "ONLINE",
            "version": "2.0.0",
            "capabilities": [
                "Real Celestrak TLE Orbital Propagation (Starlink, Planet, ISS) with Physical Ground-Truth Verification",
                "PyTorch Neural Bid-Valuation Network (BidValueMLP) Imitating CP-SAT in Sub-Millisecond Preview",
                "Distilled TreeSHAP Local Feature Explainability & SHA-256 Checkpoint Drift Detection",
                "Grounded Decision History RAG (sentence-transformers) with Verified Record Citations & Honest Refusal",
                "Local LLM Flight Director Tactical Commentary (Ollama) with Fact-Consistency Verifier",
                "Official Model Context Protocol (MCP) Server with 5 Constellation Decision & Query Tools",
                "Automated CI-Integrated Evaluation & Regression Scoring Harness",
                "Self-Healing Continuous Verification Agent Loop",
                "Strictly Async Redis State Caching & Event Pub/Sub",
                "Async SQLAlchemy Database (PostgreSQL / SQLite switch)",
                "Google OR-Tools CP-SAT Constellation Mission Optimizer",
                "Intersatellite Optical Laser Link (ISL) Mesh Network & Multi-Hop Relay Routing",
                "Extreme Space Scenario Director (Solar Storm, Debris Conjunction, Ground Blackout, Disaster Surge)",
                "Real-time WebSocket Constellation Stream",
            ],
        }


@app.websocket("/ws/constellation")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    sim = get_simulator()
    try:
        init_tick = sim.step(dt_seconds=0.0)
        await websocket.send_text(json.dumps(init_tick.model_dump()))
        while True:
            msg = await websocket.receive_text()
            try:
                cmd = json.loads(msg)
                if cmd.get("action") == "step":
                    tick = await sim.step_async(dt_seconds=cmd.get("dt", 1.0))
                    await websocket.send_text(json.dumps(tick.model_dump()))
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
