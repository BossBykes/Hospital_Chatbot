from __future__ import annotations

from typing import Dict
from uuid import uuid4


SESSIONS: Dict[str, dict] = {}


def get_session_id(request) -> str:
    sid = request.cookies.get("sid")
    if not sid:
        sid = str(uuid4())
    return sid


def set_session_cookie(response, sid: str) -> None:
    existing = response.headers.getlist("Set-Cookie")
    if any(c.startswith("sid=") for c in existing):
        return
    response.set_cookie("sid", sid, httponly=True, samesite="Lax")


def get_state(sid: str) -> dict:
    return SESSIONS.setdefault(sid, {})


def save_state(sid: str, state: dict) -> None:
    SESSIONS[sid] = state
