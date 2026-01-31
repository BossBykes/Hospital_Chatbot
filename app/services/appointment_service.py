from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Tuple


_BOOKING_KEYWORDS = {"book", "schedule", "appointment"}
_LOOKUP_PHRASES = {"my appointment", "next appointment", "appointment details"}
_CANCEL_WORDS = {"cancel", "stop", "nevermind", "never mind"}
_YES_WORDS = {"yes", "y", "yeah", "yep", "sure", "confirm", "ok", "okay"}
_NO_WORDS = {"no", "n", "nope"}


def _msg_lower(text: str) -> str:
    return (text or "").lower().strip()


def _parse_date(text: str) -> str | None:
    t = _msg_lower(text)
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", t)
    if m:
        try:
            dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    now = datetime.now()
    if "tomorrow" in t:
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")
    if "next week" in t:
        return (now + timedelta(days=7)).strftime("%Y-%m-%d")
    if "today" in t:
        return now.strftime("%Y-%m-%d")

    return None


def _parse_time(text: str) -> str | None:
    t = _msg_lower(text)
    if "morning" in t:
        return "morning"
    if "afternoon" in t:
        return "afternoon"

    m = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", t)
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"

    return None


def _is_lookup(text: str) -> bool:
    t = _msg_lower(text)
    return any(p in t for p in _LOOKUP_PHRASES)


def _is_booking_intent(text: str) -> bool:
    t = _msg_lower(text)
    return any(k in t for k in _BOOKING_KEYWORDS)


def _is_cancel(text: str) -> bool:
    t = _msg_lower(text)
    return any(w in t for w in _CANCEL_WORDS)


def _is_yes(text: str) -> bool:
    t = _msg_lower(text)
    return any(w == t for w in _YES_WORDS)


def _is_no(text: str) -> bool:
    t = _msg_lower(text)
    return any(w == t for w in _NO_WORDS)


def _summary(booking: dict) -> str:
    dept = booking.get("department", "Unknown department")
    date = booking.get("date", "Unknown date")
    time = booking.get("time", "Unknown time")
    name = booking.get("name")
    if name:
        return f"{dept} on {date} at {time} for {name}"
    return f"{dept} on {date} at {time}"


def handle_appointment_message(user_msg: str, state: dict) -> Tuple[str, dict, bool]:
    t = _msg_lower(user_msg)

    if _is_lookup(t):
        appt = state.get("appointment")
        if appt:
            return (f"Your appointment is {appt['summary']}.", state, True)
        return ("I do not have an appointment on file. Want to book one?", state, False)

    if _is_cancel(t):
        if state.get("booking"):
            state.pop("booking", None)
            return ("Okay, I canceled the booking.", state, True)
        return ("No booking in progress.", state, True)

    booking = state.get("booking")
    if not booking and _is_booking_intent(t):
        state["booking"] = {"step": "department"}
        return ("What department or reason is the appointment for?", state, False)

    if not booking:
        return ("Do you want to book an appointment or check an existing one?", state, False)

    step = booking.get("step", "department")

    if step == "department":
        if not t:
            return ("What department or reason is the appointment for?", state, False)
        booking["department"] = user_msg.strip()
        booking["step"] = "date"
        return ("What date works for you? (YYYY-MM-DD, tomorrow, or next week)", state, False)

    if step == "date":
        date = _parse_date(user_msg)
        if not date:
            return ("Please provide a date like 2026-01-15, tomorrow, or next week.", state, False)
        booking["date"] = date
        booking["step"] = "time"
        return ("What time do you prefer? (morning, afternoon, or HH:MM)", state, False)

    if step == "time":
        time = _parse_time(user_msg)
        if not time:
            return ("Please provide a time like morning, afternoon, or 14:30.", state, False)
        booking["time"] = time
        booking["step"] = "name"
        return ("What name should I put the appointment under? (optional, say skip)", state, False)

    if step == "name":
        if t in {"skip", "none", "no"}:
            booking["name"] = ""
        else:
            booking["name"] = user_msg.strip()
        booking["step"] = "confirm"
        return (f"Please confirm: {_summary(booking)}. (yes/no)", state, False)

    if step == "confirm":
        if _is_yes(t):
            summary = _summary(booking)
            state["appointment"] = {
                "department": booking.get("department"),
                "date": booking.get("date"),
                "time": booking.get("time"),
                "name": booking.get("name", ""),
                "summary": summary,
            }
            state.pop("booking", None)
            return ("Confirmed. Your appointment is booked.", state, True)
        if _is_no(t):
            state.pop("booking", None)
            return ("Okay, I canceled the booking.", state, True)
        return ("Please reply yes to confirm or no to cancel.", state, False)

    state.pop("booking", None)
    return ("I had trouble with that booking. Want to start over?", state, True)
