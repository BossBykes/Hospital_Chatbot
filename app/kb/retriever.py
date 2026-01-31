from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class KBHit:
    score: float
    title: str
    source: str
    excerpt: str


_STOPWORDS = {
    "a","an","the","and","or","but","if","then","to","of","in","on","at","for","with",
    "is","are","was","were","be","been","being","it","this","that","these","those",
    "i","you","we","they","he","she","my","your","our","their","me","us","them",
    "can","could","please","tell"
}

# Domain hints to help scoring (simple but effective)
_HINTS = {
    "visit": {"visiting", "hours", "icu"},
    "visiting": {"visit", "hours", "icu"},
    "hours": {"visiting", "icu"},
    "icu": {"hours", "visiting"},
    "pay": {"billing", "bill"},
    "bill": {"billing", "pay"},
    "billing": {"bill", "pay"},
    "insurance": {"insurances"},
    "cafeteria": {"food"},
    "parking": {"directions", "park"},
    "directions": {"parking", "address"},
}


def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [w for w in words if w not in _STOPWORDS and len(w) >= 2]


def _split_markdown_sections(md: str) -> List[Tuple[str, str]]:
    lines = md.splitlines()
    sections: List[Tuple[str, List[str]]] = []
    current_title = "General"
    current_buf: List[str] = []

    def flush():
        nonlocal current_title, current_buf, sections
        text = "\n".join(current_buf).strip()
        if text:
            sections.append((current_title, text))
        current_buf = []

    for line in lines:
        if line.strip().startswith("#"):
            flush()
            current_title = line.strip().lstrip("#").strip() or "General"
        else:
            current_buf.append(line)

    flush()
    return [(t, s) for (t, s) in sections if s.strip()]


def _expand_query_tokens(q_tokens: set[str]) -> set[str]:
    expanded = set(q_tokens)
    for t in list(q_tokens):
        for extra in _HINTS.get(t, set()):
            expanded.add(extra)
    return expanded


class KnowledgeBase:
    def __init__(self, kb_dir: Path | None = None):
        self.kb_dir = kb_dir or (Path(__file__).resolve().parent)
        self.sections: List[Tuple[str, str, str]] = []  # (source, title, text)
        self._load()

    def _load(self):
        md_files = sorted(self.kb_dir.glob("*.md"))
        for fp in md_files:
            text = fp.read_text(encoding="utf-8")
            for title, sec_text in _split_markdown_sections(text):
                self.sections.append((fp.name, title, sec_text))

    def search(self, query: str, top_k: int = 3) -> List[KBHit]:
        base_tokens = set(_tokenize(query))
        if not base_tokens:
            return []

        q_tokens = _expand_query_tokens(base_tokens)

        hits: List[KBHit] = []
        for source, title, sec_text in self.sections:
            title_tokens = set(_tokenize(title))
            sec_tokens = set(_tokenize(sec_text))

            overlap = q_tokens.intersection(sec_tokens.union(title_tokens))
            if not overlap:
                continue

            # Require at least 2 meaningful overlaps for short queries like "how do i pay"
            if len(base_tokens) >= 3 and len(overlap) < 2:
                continue

            # Base score: overlap ratio
            score = len(overlap) / max(len(q_tokens), 1)

            # Boost if overlap hits title words (titles are strong signals)
            title_overlap = q_tokens.intersection(title_tokens)
            score += 0.25 * (len(title_overlap) / max(len(q_tokens), 1))

            # Strong boost for exact key terms matching title (visit/billing/icu/etc.)
            score += 0.35 * min(1.0, len(title_overlap))

            title_lower = title.lower()
            has_icu_query = "icu" in base_tokens
            looks_like_visit_query = any(t in base_tokens for t in {"visit", "visiting", "hours"})

            # Penalize ICU sections unless the query explicitly mentions ICU
            if "icu" in title_lower and not has_icu_query:
                score -= 0.6
            elif "icu" in title_lower and has_icu_query:
                score += 0.2

            # Prefer general visiting hours for short/ambiguous visit queries
            if looks_like_visit_query and not has_icu_query:
                if "visiting hours" in title_lower and "icu" not in title_lower:
                    score += 0.4
                if "icu" in title_lower:
                    score -= 0.4

            # Clamp to zero minimum
            score = max(0.0, score)

            excerpt = sec_text.strip()
            if len(excerpt) > 320:
                excerpt = excerpt[:320].rstrip() + "..."

            hits.append(KBHit(
                score=float(score),
                title=title,
                source=source,
                excerpt=excerpt
            ))

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:top_k]
