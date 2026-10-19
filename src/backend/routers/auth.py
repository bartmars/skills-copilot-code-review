"""
Authentication endpoints for the High School Management System API
"""

from datetime import datetime, timedelta, timezone
import secrets
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..database import (
    teacher_sessions_collection,
    teachers_collection,
    verify_password,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
bearer_scheme = HTTPBearer(auto_error=False)


def get_authenticated_teacher(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Dict[str, Any]:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    session = teacher_sessions_collection.find_one({"_id": credentials.credentials})
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if not session or session["expires_at"] <= now:
        raise HTTPException(status_code=401, detail="Session expired")

    teacher = teachers_collection.find_one({"_id": session["username"]})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher session")
    return teacher


@router.post("/login")
def login(username: str, password: str) -> Dict[str, Any]:
    """Login a teacher account"""
    # Find the teacher in the database
    teacher = teachers_collection.find_one({"_id": username})

    # Verify password using Argon2 verifier from database.py
    if not teacher or not verify_password(teacher.get("password", ""), password):
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    session_token = secrets.token_urlsafe(32)
    teacher_sessions_collection.insert_one({
        "_id": session_token,
        "username": teacher["username"],
        "expires_at": datetime.now(timezone.utc).replace(tzinfo=None)
        + timedelta(hours=12),
    })

    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"],
        "session_token": session_token,
    }


@router.get("/check-session")
def check_session(
    username: str,
    teacher: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> Dict[str, Any]:
    """Check whether the authenticated teacher session is valid."""
    if teacher["username"] != username:
        raise HTTPException(status_code=401, detail="Invalid teacher session")

    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"],
    }


@router.post("/logout")
def logout(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    teacher: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> Dict[str, str]:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    teacher_sessions_collection.delete_one({"_id": credentials.credentials})
    return {"message": "Logged out"}
