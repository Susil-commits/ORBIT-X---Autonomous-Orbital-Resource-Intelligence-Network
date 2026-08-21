"""Comprehensive unit and API test suite for JWT Authentication, RBAC, and Audit Logging."""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    UserRole,
)
from app.core.audit import record_audit_event
from app.core.database import AsyncSessionLocal, AuditLogRecord, init_db
from sqlalchemy import select


def test_password_hashing_and_verification():
    """Validates deterministic password hashing and constant-time verification."""
    raw_pass = "mission-commander-2026"
    h = hash_password(raw_pass)
    assert h != raw_pass
    assert verify_password(raw_pass, h) is True
    assert verify_password("wrong-password", h) is False


def test_jwt_token_generation_and_decoding():
    """Validates token creation, claim preservation, and signature verification."""
    token = create_access_token({"sub": "flight_director_1", "role": UserRole.MISSION_OPERATOR.value})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.sub == "flight_director_1"
    assert payload.role == UserRole.MISSION_OPERATOR


@pytest.mark.asyncio
async def test_api_login_success_and_denied():
    """Verifies POST /api/auth/login with valid and invalid credentials."""
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Valid Admin Login
        res_ok = await client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "orbitx-admin-2026"},
        )
        assert res_ok.status_code == 200
        data = res_ok.json()
        assert "access_token" in data
        assert data["role"] == "ADMIN"
        token = data["access_token"]

        # 2. Invalid Password
        res_bad = await client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "invalid-password"},
        )
        assert res_bad.status_code == 401

        # 3. Authenticated /me endpoint
        res_me = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_me.status_code == 200
        me_data = res_me.json()
        assert me_data["username"] == "admin"
        assert me_data["role"] == "ADMIN"
        assert me_data["permissions"]["can_access_admin"] is True


@pytest.mark.asyncio
async def test_rbac_access_control():
    """Verifies that VIEWER role is blocked (403) from Operator/Admin audit logs."""
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Login as Viewer
        res_v = await client.post(
            "/api/auth/login",
            json={"username": "viewer", "password": "viewer-pass"},
        )
        assert res_v.status_code == 200
        viewer_token = res_v.json()["access_token"]

        # 2. Attempt to access /api/auth/audit with Viewer token -> 403 Forbidden
        res_denied = await client.get(
            "/api/auth/audit",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert res_denied.status_code == 403

        # 3. Login as Operator
        res_op = await client.post(
            "/api/auth/login",
            json={"username": "operator", "password": "operator-pass"},
        )
        assert res_op.status_code == 200
        op_token = res_op.json()["access_token"]

        # 4. Access /api/auth/audit with Operator token -> 200 OK
        res_allowed = await client.get(
            "/api/auth/audit",
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert res_allowed.status_code == 200
        assert isinstance(res_allowed.json(), list)


@pytest.mark.asyncio
async def test_audit_event_persistence():
    """Verifies asynchronous recording and database querying of audit events."""
    await init_db()
    audit_id = await record_audit_event(
        actor="test-runner",
        action="EMERGENCY_REPLAN_TEST",
        target="constellation:WALKER_550",
        result="SUCCESS",
        details={"replan_horizon_s": 600},
    )
    assert audit_id.startswith("aud-")

    async with AsyncSessionLocal() as session:
        stmt = select(AuditLogRecord).where(AuditLogRecord.audit_id == audit_id)
        res = await session.execute(stmt)
        record = res.scalar_one_or_none()
        assert record is not None
        assert record.actor == "test-runner"
        assert record.action == "EMERGENCY_REPLAN_TEST"
        assert record.result == "SUCCESS"
