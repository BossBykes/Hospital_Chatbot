import json
import random
import re
from pathlib import Path
from typing import Tuple


class IntentClassifier:
    def __init__(self):
        intents_path = Path(__file__).resolve().parent / "intents.json"
        with open(intents_path, "r", encoding="utf-8") as f:
            self.intents = json.load(f)["intents"]

    def _normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def predict(self, text: str) -> Tuple[str, float]:
        """
        Simple scoring:
        - Match each pattern as a whole phrase OR as all words present
        - Prefer longer/more specific patterns
        """
        t = self._normalize(text)
        best_tag = "fallback"
        best_score = 0.0

        for intent in self.intents:
            tag = intent.get("tag", "fallback")
            patterns = intent.get("patterns", []) or []

            for p in patterns:
                p_norm = self._normalize(p)
                if not p_norm:
                    continue

                # Phrase match (word-boundary-ish for safer matching)
                if re.search(rf"\b{re.escape(p_norm)}\b", t):
                    score = 1.0 + min(len(p_norm) / 50.0, 0.5)
                else:
                    # Word coverage match (handles slightly shuffled wording)
                    p_words = [w for w in re.split(r"\W+", p_norm) if w]
                    if not p_words:
                        continue
                    hits = sum(1 for w in p_words if re.search(rf"\b{re.escape(w)}\b", t))
                    score = hits / max(len(p_words), 1)

                if score > best_score:
                    best_score = score
                    best_tag = tag

        # Confidence threshold
        if best_score < 0.45:
            return "fallback", float(best_score)

        # Clamp confidence to [0,1]
        conf = min(1.0, float(best_score))
        return best_tag, conf

    def get_response(self, tag: str) -> str:
        for intent in self.intents:
            if intent.get("tag") == tag:
                responses = intent.get("responses", []) or []
                if responses:
                    return random.choice(responses)
        return "Sorry, I didn't understand that. Could you rephrase?"
