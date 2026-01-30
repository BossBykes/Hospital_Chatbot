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
    "i","you","we","they","he","she","my","your","our","their","me","us","them"
}


def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [w for w in words if w not in _STOPWORDS and len(w) >= 2]


def _split_markdown_sections(md: str) -> List[Tuple[str, str]]:
    """
    Returns list of (section_title, section_text).
    Uses markdown headings starting with '#'.
    """
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


class KnowledgeBase:
    def __init__(self, kb_dir: Path | None = None):
        self.kb_dir = kb_dir or (Path(__file__).resolve().parent)
        self.docs: List[Tuple[str, str]] = []  # (source, text)
        self.sections: List[Tuple[str, str, str]] = []  # (source, title, text)
        self._load()

    def _load(self):
        md_files = sorted(self.kb_dir.glob("*.md"))
        for fp in md_files:
            text = fp.read_text(encoding="utf-8")
            self.docs.append((fp.name, text))
            for title, sec_text in _split_markdown_sections(text):
                self.sections.append((fp.name, title, sec_text))

    def search(self, query: str, top_k: int = 3) -> List[KBHit]:
        q_tokens = set(_tokenize(query))
        if not q_tokens:
            return []

        hits: List[KBHit] = []
        for source, title, sec_text in self.sections:
            sec_tokens = set(_tokenize(sec_text))
            overlap = q_tokens.intersection(sec_tokens)
            if not overlap:
                continue

            # Score: overlap ratio with a small boost for shorter sections
            score = len(overlap) / max(len(q_tokens), 1)
            excerpt = sec_text.strip()
            if len(excerpt) > 320:
                excerpt = excerpt[:320].rstrip() + "..."

            hits.append(KBHit(
                score=score,
                title=title,
                source=source,
                excerpt=excerpt
            ))

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:top_k]
