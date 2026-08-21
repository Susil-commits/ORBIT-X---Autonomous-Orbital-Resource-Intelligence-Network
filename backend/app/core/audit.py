"""Asynchronous Audit Logging Engine for ORBIT-X."""

import time
import json
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.core.database import AsyncSessionLocal, AuditLogRecord
from app.core.redis_client import redis_manager

logger = logging.getLogger("orbitx.audit")


async def record_audit_event(
    actor: str,
    action: str,
    target: Optional[str] = None,
    result: str = "SUCCESS",
    details: Optional[Dict[str, Any]] = None,
) -> str:
    """Records an immutable audit event in the database and broadcasts to Redis."""
    audit_id = f"aud-{uuid.uuid4().hex[:12]}"
    timestamp_utc = datetime.now(timezone.utc).isoformat()
    details_json = json.dumps(details or {})

    # 1. Persist to Relational Database
    try:
        async with AsyncSessionLocal() as session:
            record = AuditLogRecord(
                audit_id=audit_id,
                actor=actor,
                action=action,
                target=target,
                result=result,
                timestamp_utc=timestamp_utc,
                details_json=details_json,
            )
            session.add(record)
            await session.commit()
    except Exception as e:
        logger.error("Failed to persist audit log record: %s", e)

    # 2. Broadcast event to Redis audit channel
    audit_payload = {
        "audit_id": audit_id,
        "actor": actor,
        "action": action,
        "target": target,
        "result": result,
        "timestamp_utc": timestamp_utc,
        "details": details or {},
    }
    await redis_manager.publish_event("orbit:audit", audit_payload)
    
    logger.info("AUDIT [%s] %s by %s on %s -> %s", audit_id, action, actor, target or 'N/A', result)
    return audit_id
