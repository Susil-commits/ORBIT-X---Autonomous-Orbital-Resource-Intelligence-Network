"""Async SQLAlchemy Database Engine for ORBIT-X.

Supports seamless switching between PostgreSQL (asyncpg) and SQLite (aiosqlite)
via DATABASE_URL environment variable. Includes models for Decision Logs, Evaluation Runs,
Users, and Immutable Audit Logs.
"""

import json
import datetime
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    DateTime,
    Boolean,
)

from app.core.config import settings

# Format URL for async drivers
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("sqlite:///") and not db_url.startswith("sqlite+aiosqlite:///"):
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


class DecisionLogRecord(Base):
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_id = Column(String(64), unique=True, index=True)
    tick = Column(Integer, index=True)
    sim_time_s = Column(Float, index=True)
    event_type = Column(String(64), index=True)  # "MISSION_ASSIGNED", "ANOMALY_DETECTED", "MANEUVER_EXECUTED", etc.
    mission_id = Column(String(64), nullable=True, index=True)
    satellite_id = Column(String(64), nullable=True, index=True)
    target_name = Column(String(128), nullable=True)
    summary = Column(Text, nullable=False)
    details_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))


class EvalRunRecord(Base):
    __tablename__ = "eval_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    run_id = Column(String(64), unique=True, index=True)
    overall_status = Column(String(32), index=True)  # "PASS", "REGRESSION_DETECTED"
    timestamp_iso = Column(String(64))
    metrics_json = Column(Text, default="[]")
    regressions_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))


class AuditLogRecord(Base):
    """Immutable audit trail of all security and mission-critical actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    audit_id = Column(String(64), unique=True, index=True)
    actor = Column(String(64), nullable=False, index=True)      # WHO (e.g. operator-42, system)
    action = Column(String(64), nullable=False, index=True)     # WHAT (e.g. EMERGENCY_REPLAN, MISSION_DISPATCH)
    target = Column(String(128), nullable=True, index=True)     # TARGET (e.g. mission=M-101, sat=SAT-004)
    result = Column(String(32), nullable=False)                 # RESULT (SUCCESS, FAILED, DENIED)
    timestamp_utc = Column(String(64), nullable=False)          # WHEN
    details_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))


async def init_db():
    """Initializes database tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining async DB sessions."""
    async with AsyncSessionLocal() as session:
        yield session
