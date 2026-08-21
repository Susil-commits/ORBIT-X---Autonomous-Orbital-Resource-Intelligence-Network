"""FastAPI Router for JWT Authentication, RBAC Profiles & Audit Log Queries."""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
from sqlalchemy import select, desc
from app.core.security import (
    UserAuth,
    UserTokenPayload,
    UserRole,
    DEMO_USERS,
    verify_password,
    create_access_token,
    get_current_user,
    require_roles,
)
from app.core.audit import record_audit_event
from app.core.database import get_db, AuditLogRecord, AsyncSession

router = APIRouter(prefix="/api/auth", tags=["Security & Authentication"])


@router.post("/login")
async def login(credentials: UserAuth):
    """Authenticates user credentials and returns signed JWT access token."""
    user = DEMO_USERS.get(credentials.username.lower())
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        await record_audit_event(
            actor=credentials.username,
            action="USER_LOGIN_ATTEMPT",
            target="auth/login",
            result="DENIED",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = user["role"]
    token = create_access_token({"sub": credentials.username, "role": role.value})

    await record_audit_event(
        actor=credentials.username,
        action="USER_LOGIN_SUCCESS",
        target="auth/login",
        result="SUCCESS",
        details={"role": role.value},
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": credentials.username,
        "role": role.value,
    }


@router.get("/me")
async def get_my_profile(current_user: UserTokenPayload = Depends(get_current_user)):
    """Returns currently authenticated user profile and permissions."""
    return {
        "username": current_user.sub,
        "role": current_user.role.value,
        "permissions": {
            "can_create_mission": current_user.role in [UserRole.ADMIN, UserRole.MISSION_OPERATOR],
            "can_replan": current_user.role in [UserRole.ADMIN, UserRole.MISSION_OPERATOR],
            "can_view_telemetry": True,
            "can_access_admin": current_user.role == UserRole.ADMIN,
        },
    }


@router.get("/audit", dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.MISSION_OPERATOR]))])
async def list_audit_logs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Lists recent immutable security and operational audit records (Admin/Operator only)."""
    stmt = select(AuditLogRecord).order_by(desc(AuditLogRecord.id)).limit(limit)
    res = await db.execute(stmt)
    records = res.scalars().all()
    return [
        {
            "audit_id": r.audit_id,
            "actor": r.actor,
            "action": r.action,
            "target": r.target,
            "result": r.result,
            "timestamp_utc": r.timestamp_utc,
            "details": r.details_json,
        }
        for r in records
    ]
