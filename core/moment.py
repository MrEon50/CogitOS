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

        # ── REZONANS ASOCJACYJNY (Pamięć jako bodziec) ──
        # Engramy nie tylko "echo" — one pompują napięcie
        memory_affect = sum(e.salience * abs(e.valence) for e in self.engrams)
        memory_values = sum(e.salience for e in self.engrams if abs(e.valence) > 0.6)

        # Afekt (Ta): Bodziec + Pamięć. Jeśli Dopamina (z psyche_snapshot) jest niska, efekt jest 2x silniejszy
        dopamine = self.psyche_snapshot.get("dopamine", 0.5)
        d_factor = 1.5 - dopamine # Niska dopamina = wysoka wrażliwość na strach/afekt
        
        t_a = (abs(p.emotional_charge) + memory_affect) * (2.0 - S) * d_factor
        t_a = min(1.0, t_a)

        # Logika (Tc): Bodziec informacyjny, dość płaski, ale rośnie przy wysokim A
        t_c = p.semantic_density * (1.5 - C) * (1.0 + A * 0.5)
        t_c = min(1.0, t_c)

        # Wartości (Tv): Wyzwanie + Rezonans Aksjologiczny z pamięci
        t_v = (p.value_challenge + memory_values * 0.5) * (2.2 - S)
        t_v = min(1.0, t_v)

        return TensionVector(
            affective=round(t_a, 3),
            cognitive=round(t_c, 3),
            axiological=round(t_v, 3),
        )
