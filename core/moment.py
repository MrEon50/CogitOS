from dataclasses import dataclass
from typing import List, Dict
from .percept import Percept
from .engram import Engram
from .tension import TensionVector

@dataclass
class ConsciousMoment:
    """
    Chwila świadomości = integracja perceptu z pamięcią i stanem wewnętrznym.
    """
    percept: Percept
    engrams: List[Engram]
    psyche_snapshot: Dict[str, float]

    @property
    def resonance(self) -> float:
        if not self.engrams:
            return 0.0
        return sum(e.salience for e in self.engrams) / len(self.engrams)

    @property
    def context_richness(self) -> float:
        n = len(self.engrams)
        if n == 0:
            return 0.0
        return min(1.0, n * 0.33 * self.resonance)

    def to_tension(self) -> TensionVector:
        S = self.psyche_snapshot.get("anchor", 1.0)
        C = self.psyche_snapshot.get("coherence", 1.0)
        A = self.psyche_snapshot.get("arousal", 0.2)

        p = self.percept

        # Wzmocnienie echa emocjonalnego
        emotional_echo = (
            sum(abs(e.valence) for e in self.engrams) / max(1, len(self.engrams))
        ) * (0.3 + A * 0.7)

        # Afekt: reakcja na bodziec pomnozona przez wage 'ciezaru'
        t_a = abs(p.emotional_charge) * (2.0 - S) + emotional_echo
        t_a = min(1.0, t_a)

        # Cognitive: gęstość informacyjna vs spójność
        t_c = p.semantic_density * (1.8 - C)
        t_c = min(1.0, t_c)

        # Wartosci: uderzenie w fundamenty
        t_v = p.value_challenge * (2.2 - S)
        t_v = min(1.0, t_v)

        return TensionVector(
            affective=round(t_a, 3),
            cognitive=round(t_c, 3),
            axiological=round(t_v, 3),
        )
