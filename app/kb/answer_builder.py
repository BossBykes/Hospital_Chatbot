from __future__ import annotations

from typing import List

from .retriever import KBHit


def _one_line(text: str) -> str:
    return " ".join((text or "").strip().split())


def _split_sentences(text: str) -> List[str]:
    parts = [p.strip() for p in (text or "").split(".") if p.strip()]
    return [p + "." for p in parts]


def _shorten(text: str, max_len: int = 200) -> str:
    line = _one_line(text)
    if len(line) <= max_len:
        return line
    return line[: max_len - 3].rstrip() + "..."


def build_kb_answer(query: str, hits: list[KBHit]) -> dict:
    if not hits:
        return {"text": ""}

    q = (query or "").lower()
    wants_icu = "icu" in q

    # Prefer non-ICU visiting hours if query doesn't mention ICU
    if not wants_icu:
        for h in hits:
            if "visiting hours" in h.title.lower() and "icu" not in h.title.lower():
                hits = [h] + [x for x in hits if x is not h]
                break

    best = hits[0]
    response = _shorten(best.excerpt, max_len=220)

    sources = [f"{best.source} — {best.title}"]
    suggestions = []

    # If second hit is close and different, add a related line or clarify
    if len(hits) > 1:
        second = hits[1]
        if abs(best.score - second.score) <= 0.12 and best.title != second.title:
            best_title = best.title.lower()
            second_title = second.title.lower()

            if ("icu" in second_title or "icu" in best_title) and not wants_icu:
                response = "General visiting hours are available. Do you need general visiting hours or ICU visiting hours?"
                suggestions = ["Visiting hours", "ICU visiting hours"]
            elif ("visiting hours" in best_title and "icu" in second_title and wants_icu):
                response = _shorten(second.excerpt, max_len=220)
                sources = [f"{second.source} — {second.title}"]
            else:
                related_line = _split_sentences(second.excerpt)
                if related_line:
                    response = f"{response}\nRelated: {related_line[0]}"
                    sources.append(f"{second.source} — {second.title}")

    # Keep responses short (max ~3 lines)
    response = "\n".join(response.splitlines()[:3])

    result = {"text": response}
    if suggestions:
        result["suggestions"] = suggestions
    if sources:
        result["sources"] = sources
    return result
