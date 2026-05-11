import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .percept import Percept
from .psyche import Psyche

@dataclass
class Engram:
    """
    Jednostka pamięci asocjacyjnej wzbogacona o embedding.
    """
    text: str
    features: Dict[str, float]
    embedding: List[float] = field(default_factory=list)  # NOWE
    valence: float = 0.0
    strength: float = 1.0
    recency: float = 1.0
    step_formed: int = 0

    DECAY_RATE: float = 0.92
    REINFORCE_GAIN: float = 0.15

    def decay(self) -> None:
        self.recency *= self.DECAY_RATE

    def reinforce(self) -> None:
        self.strength = min(2.0, self.strength + self.REINFORCE_GAIN)
        self.recency = 1.0

    @property
    def salience(self) -> float:
        return self.strength * self.recency

class EngramStore:
    """
    Magazyn pamięci z obsługą hybrydowego retrievalu (embeddingi + psyche bias).
    """
    def __init__(self, capacity: int = 64):
        self._store: List[Engram] = []
        self.capacity = capacity

    def store(self, engram: Engram) -> None:
        # Sprawdzenie podobieństwa dla zapobiegania duplikatom
        for existing in self._store:
            sim = self._similarity_hybrid(existing, engram)
            if sim > 0.85:
                existing.reinforce()
                existing.valence = (existing.valence + engram.valence) / 2.0
                return
        
        if len(self._store) >= self.capacity:
            self._store.sort(key=lambda e: e.salience)
            self._store.pop(0)
        self._store.append(engram)

    def retrieve(self, query: Percept, psyche: Psyche, top_k: int = 3) -> List[Engram]:
        if not self._store:
            return []

        scored: List[tuple[float, Engram]] = []
        for eng in self._store:
            # Hybrydowe podobieństwo: embeddingi jeśli dostępne, inaczej cechy
            sim = self._similarity_hybrid_query(eng, query)

            # Modulacja przez stan Psyche (zachowana logika)
            affective_bonus = abs(eng.valence) * psyche.arousal * 0.3
            axiological_bonus = eng.features.get("tożsamość", 0.0) * (1.0 - psyche.anchor) * 0.4

            score = sim * eng.salience + affective_bonus + axiological_bonus
            if score > 0.01:
                scored.append((score, eng))

        scored.sort(key=lambda x: x[0], reverse=True)
        retrieved = [eng for _, eng in scored[:top_k]]

        for eng in retrieved:
            eng.reinforce()
        for eng in self._store:
            eng.decay()

        return retrieved

    def _similarity_hybrid(self, e1: Engram, e2: Engram) -> float:
        if e1.embedding and e2.embedding:
            return self._cosine_similarity(e1.embedding, e2.embedding)
        return self._dict_similarity(e1.features, e2.features)

    def _similarity_hybrid_query(self, eng: Engram, query: Percept) -> float:
        if eng.embedding and query.embedding:
            return self._cosine_similarity(eng.embedding, query.embedding)
        return self._dict_similarity(eng.features, query.features)

    @staticmethod
    def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(a * a for a in v2))
        return dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0

    @staticmethod
    def _dict_similarity(a: Dict[str, float], b: Dict[str, float]) -> float:
        if not a or not b: return 0.0
        keys = set(a) & set(b)
        if not keys: return 0.0
        dot = sum(a[k] * b[k] for k in keys)
        norm_a = math.sqrt(sum(v ** 2 for v in a.values()))
        norm_b = math.sqrt(sum(v ** 2 for v in b.values()))
        return dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0

    def __len__(self) -> int:
        return len(self._store)
