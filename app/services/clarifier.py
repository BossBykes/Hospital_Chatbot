from __future__ import annotations


def clarify(user_msg: str) -> str | None:
    text = (user_msg or "").strip().lower()
    if not text:
        return None

    words = text.split()
    is_short = len(words) <= 2

    if ("visit" in text or "visiting" in text) and "icu" not in text:
        if is_short or "hours" in text or "when" in text:
            return "Do you need general visiting hours or ICU visiting hours?"

    if ("bill" in text or "pay" in text) and "insurance" not in text:
        if is_short or "how" in text or "payment" in text:
            return "Do you want help paying your bill or checking accepted insurance?"

    if "parking" in text or "directions" in text:
        if is_short or "where" in text or "how" in text:
            return "Do you want parking info or directions to the hospital?"

    return None
