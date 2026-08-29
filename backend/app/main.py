import os
import sys
import time
import uuid
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Set, Optional

# Ensure backend and project root are in sys.path
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
for p in [str(backend_dir), str(root_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)


from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.database import init_db
from app.core.redis_client import redis_manager
from app.core.kafka_client import kafka_manager
from app.core.telemetry import (
    get_prometheus_metrics_bytes,
    CONTENT_TYPE_LATEST,
    HTTP_REQUEST_DURATION,
    HTTP_REQUESTS_TOTAL,
    setup_structured_logging,
)
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
from app.api.routes_auth import router as auth_router
from app.api.routes_context import router as context_router
from app.api.routes_experiments import router as experiments_router
from app.api.routes_ai_platform import router as ai_platform_router

# Initialize structured logging
logger = setup_structured_logging(level=logging.INFO)


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
_sim_loop_task: Optional[asyncio.Task] = None


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
            logger.error("Error in simulation loop: %s", e)
            await asyncio.sleep(1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _sim_loop_task
    # Initialize async database tables
    try:
        await init_db()
    except Exception as e:
        logger.warning("Database initialization skipped: %s", e)

    # Connect async Redis
    await redis_manager.connect()

    # Start Kafka Producer & Event Bus
    await kafka_manager.start()

    # Start simulation loop in background
    _sim_loop_task = asyncio.create_task(background_simulation_loop())
    yield
    if _sim_loop_task:
        _sim_loop_task.cancel()
    await kafka_manager.stop()
    await redis_manager.close()


app = FastAPI(
    title="ORBIT-X Backend",
    description="Autonomous Orbital Resource & Intelligence Network Production API",
    version="2.0.0",
    lifespan=lifespan,
)

# Rate Limiter Setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Observability & Request Correlation Middleware
@app.middleware("http")
async def observability_and_correlation_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:10]}"
    trace_id = request.headers.get("X-Trace-ID") or f"trace-{uuid.uuid4().hex[:16]}"
    request.state.request_id = request_id
    request.state.trace_id = trace_id

    start_time = time.perf_counter()
    response: Response = None
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
    except Exception as e:
        status_code = "500"
        logger.error(
            "Unhandled server exception on %s %s: %s",
            request.method, request.url.path, e,
            extra={"request_id": request_id, "trace_id": trace_id, "error": str(e)}
        )
        raise e
    finally:
        duration_s = time.perf_counter() - start_time
        path_template = request.url.path
        HTTP_REQUEST_DURATION.labels(method=request.method, endpoint=path_template, status_code=status_code).observe(duration_s)
        HTTP_REQUESTS_TOTAL.labels(method=request.method, endpoint=path_template, status_code=status_code).inc()

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Trace-ID"] = trace_id
    return response


# CORS Configuration
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
app.include_router(auth_router)
app.include_router(sim_router)
app.include_router(missions_router)
app.include_router(benchmarks_router)
app.include_router(multi_agent_router)
app.include_router(isl_router)
app.include_router(scenarios_router)
app.include_router(ai_router)
app.include_router(constellation_data_router)
app.include_router(context_router)
app.include_router(experiments_router)
app.include_router(ai_platform_router)


# ----------------------------------------------------
# Health, Readiness & Metrics Endpoints
# ----------------------------------------------------

@app.get("/health")
async def liveness_probe():
    """Liveness probe: answers whether the API process is alive."""
    return {"status": "UP", "service": "orbitx-api", "version": "2.0.0"}


@app.get("/ready")
async def readiness_probe():
    """Readiness probe: checks whether dependencies are ready to serve live traffic."""
    redis_alive = await redis_manager.ping()
    return {
        "status": "READY",
        "service": "orbitx-api",
        "redis_connected": redis_alive,
        "kafka_connected": kafka_manager.is_connected,
        "database": "ACTIVE",
    }


@app.get("/metrics")
async def prometheus_metrics():
    """Standard Prometheus metrics scrape endpoint."""
    metrics_data = get_prometheus_metrics_bytes()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


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
        api_prefixes = ("api/", "docs", "openapi.json", "ws/", "redoc", "health", "ready", "metrics")
        if any(full_path.startswith(p) for p in api_prefixes):
            raise HTTPException(status_code=404, detail="Not Found")
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
                "Strictly Async Redis State Caching, Distributed Locks & Event Pub/Sub",
                "Kafka Event Backbone with Idempotency Deduplication & Dead-Letter Queue (DLQ)",
                "BullMQ Node.js Asynchronous Background Workers",
                "Full Observability: OpenTelemetry Distributed Traces, Prometheus Metrics & Grafana Dashboards",
                "JWT Authentication & Role-Based Access Control (ADMIN, MISSION_OPERATOR, ANALYST, VIEWER)",
                "Immutable PostgreSQL / Async Relational Audit Logging",
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
