"""Production Observability Stack: Prometheus Metrics, OpenTelemetry Tracing & Structured JSON Logging."""

import time
import json
import logging
import sys
from typing import Optional, Dict, Any
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    REGISTRY,
)
from app.core.config import settings

# ----------------------------------------------------
# Prometheus Metric Registry & Instrumentation
# ----------------------------------------------------

# HTTP API Metrics
HTTP_REQUEST_DURATION = Histogram(
    "orbit_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint", "status_code"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
HTTP_REQUESTS_TOTAL = Counter(
    "orbit_http_requests_total",
    "Total HTTP requests handled",
    ["method", "endpoint", "status_code"],
)

# Scheduler Metrics
SCHEDULER_DURATION = Histogram(
    "orbit_scheduler_duration_seconds",
    "CP-SAT optimization run latency in seconds",
    ["solver_type"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)
SCHEDULER_SUCCESS_TOTAL = Counter(
    "orbit_scheduler_success_total",
    "Total successful CP-SAT mission schedule assignments",
)
SCHEDULER_FAILURE_TOTAL = Counter(
    "orbit_scheduler_failure_total",
    "Total scheduling failures or infeasible missions",
    ["reason"],
)

# Machine Learning & Surrogate Metrics
ML_INFERENCE_DURATION = Histogram(
    "orbit_ml_inference_duration_seconds",
    "Neural bid network and PINN inference latency in seconds",
    ["model_name"],
    buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1),
)
ML_INFERENCES_TOTAL = Counter(
    "orbit_ml_inferences_total",
    "Total ML model forward passes executed",
    ["model_name"],
)

# Resilience & Anomaly Metrics
ANOMALY_DETECTED_TOTAL = Counter(
    "orbit_anomaly_detected_total",
    "Total telemetry health anomalies detected",
    ["severity", "subsystem"],
)
EMERGENCY_REPLAN_TOTAL = Counter(
    "orbit_emergency_replan_total",
    "Total dynamic emergency replans triggered",
    ["trigger_reason"],
)

# Cache & Distributed Lock Metrics
REDIS_CACHE_HITS = Counter(
    "orbit_redis_cache_hits_total",
    "Total cache hit count",
    ["cache_type"],
)
REDIS_CACHE_MISSES = Counter(
    "orbit_redis_cache_misses_total",
    "Total cache miss count",
    ["cache_type"],
)
LOCK_ACQUISITIONS_TOTAL = Counter(
    "orbit_lock_acquisitions_total",
    "Total distributed locks successfully acquired",
)
LOCK_TIMEOUTS_TOTAL = Counter(
    "orbit_lock_timeouts_total",
    "Total distributed lock acquisition timeouts/contention failures",
)

# Event Backbone Metrics
KAFKA_MESSAGES_PUBLISHED = Counter(
    "orbit_kafka_messages_published_total",
    "Total messages published across Kafka topics",
    ["topic"],
)
KAFKA_MESSAGES_CONSUMED = Counter(
    "orbit_kafka_messages_consumed_total",
    "Total messages consumed and processed from Kafka topics",
    ["topic"],
)
KAFKA_CONSUMER_LAG = Gauge(
    "orbit_kafka_consumer_lag",
    "Estimated Kafka consumer group partition lag",
    ["topic", "consumer_group"],
)

# Constellation Gauges
ACTIVE_MISSIONS = Gauge(
    "orbit_active_missions",
    "Number of currently executing satellite missions",
)
SATELLITES_NOMINAL = Gauge(
    "orbit_satellites_nominal_count",
    "Count of satellites reporting healthy nominal status",
)


def get_prometheus_metrics_bytes() -> bytes:
    """Renders all registered Prometheus metrics to standard scrape format."""
    return generate_latest(REGISTRY)


# ----------------------------------------------------
# Structured JSON Logger Formatter
# ----------------------------------------------------

class JSONLogFormatter(logging.Formatter):
    """Encodes log records into structured JSON according to production architecture specifications."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "service": getattr(record, "service", "orbitx-backend"),
            "logger": record.name,
            "event": getattr(record, "event", record.getMessage()),
        }

        # Contextual correlation fields
        for field in ("request_id", "trace_id", "mission_id", "satellite_id", "duration_ms", "error"):
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_structured_logging(level: int = logging.INFO):
    """Configures root logger with JSON formatting."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing stream handlers
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONLogFormatter())
    root_logger.addHandler(handler)
    return root_logger


# ----------------------------------------------------
# OpenTelemetry Tracer Stub / Wrapper
# ----------------------------------------------------

class TraceContext:
    """Lightweight tracer wrapper with OpenTelemetry SDK fallback."""

    def __init__(self):
        self.tracer = None
        if settings.OPENTELEMETRY_ENABLED:
            try:
                from opentelemetry import trace
                from opentelemetry.sdk.trace import TracerProvider
                from opentelemetry.sdk.resources import Resource

                resource = Resource.create({"service.name": "orbitx-backend", "service.version": settings.VERSION})
                provider = TracerProvider(resource=resource)
                trace.set_tracer_provider(provider)
                self.tracer = trace.get_tracer("orbitx.tracer")
            except Exception as e:
                logging.getLogger("orbitx.otel").warning("OpenTelemetry init skipped: %s", e)

    def start_span(self, name: str):
        if self.tracer:
            return self.tracer.start_as_current_span(name)
        # Dummy context manager fallback
        from contextlib import nullcontext
        return nullcontext()


tracer = TraceContext()
