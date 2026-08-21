"""JWT Authentication & Role-Based Access Control (RBAC) Module for ORBIT-X."""

import time
import hmac
import hashlib
from typing import Optional, List
from enum import Enum
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel
from app.core.config import settings

# RBAC Roles
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MISSION_OPERATOR = "MISSION_OPERATOR"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"


class UserTokenPayload(BaseModel):
    sub: str  # username / user_id
    role: UserRole = UserRole.VIEWER
    exp: Optional[int] = None
    iat: Optional[int] = None


class UserAuth(BaseModel):
    username: str
    password: str
    role: Optional[UserRole] = UserRole.VIEWER


security_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Computes deterministic SHA-256 password hash with salt."""
    salt = settings.JWT_SECRET_KEY[:8].encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000).hex()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against stored hash."""
    return hmac.compare_digest(hash_password(plain_password), hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(datetime.now(timezone.utc).timestamp())})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[UserTokenPayload]:
    """Decodes and verifies signed JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return UserTokenPayload(**payload)
    except Exception:
        return None


# Default Mock/In-Memory User Store (supplemented by Database)
DEMO_USERS = {
    "admin": {"hashed_password": hash_password("orbitx-admin-2026"), "role": UserRole.ADMIN},
    "operator": {"hashed_password": hash_password("operator-pass"), "role": UserRole.MISSION_OPERATOR},
    "analyst": {"hashed_password": hash_password("analyst-pass"), "role": UserRole.ANALYST},
    "viewer": {"hashed_password": hash_password("viewer-pass"), "role": UserRole.VIEWER},
}


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> UserTokenPayload:
    """FastAPI dependency to extract and validate current authenticated user."""
    # Allow unauthenticated local development if header missing (defaults to VIEWER)
    if not credentials:
        return UserTokenPayload(sub="anonymous", role=UserRole.VIEWER)

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired JWT credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def require_roles(allowed_roles: List[UserRole]):
    """Role-Based Access Control dependency factory."""
    async def role_checker(current_user: UserTokenPayload = Depends(get_current_user)):
        # Admin can access everything
        if current_user.role == UserRole.ADMIN:
            return current_user

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role '{current_user.role.value}'. Requires: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker
