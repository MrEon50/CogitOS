from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tension import TensionVector

class Phase(Enum):
    HARMONY   = "harmonia"    # napięcia zrównoważone
    TENSION   = "napięcie"    # aktywne tarcie — głębsze przetwarzanie
    KATHARSIS = "katharsis"   # przeciążenie aksjologiczne — reset

@dataclass
class Psyche:
    """
    Stabilny stan wewnętrzny. Ewoluuje powoli — to jest tożsamość.
    """
    anchor:    float = 1.0
    arousal:   float = 0.2
    coherence: float = 0.9
    phase:     Phase = Phase.HARMONY
    dopamine:  float = 0.5  # Poziom satysfakcji / napedu
    motto:     str = "Eksploracja biezaca" # Samookreslony cel kognitywny
    
    # Nastroj (rezydualne napiecia)
    mood_ta:   float = 0.0
    mood_tc:   float = 0.0
    mood_tv:   float = 0.0

    # Stałe kognitywne (Złoty Podział)
    PHI:     float = 1.618033
    INV_PHI: float = 0.618033

    # Parametry Inercji i Kosztów
    MOOD_ATTACK:      float = 0.35
    MOOD_DECAY:       float = 0.94
    COGNITIVE_COST:   float = 0.015 # Koszt Dopaminy za intensywne Tc
    RESET_THRESHOLD:  int = 6       # Kroki przy C < 0.2 przed resetem
    
    _history: list[float] = field(default_factory=list, repr=False)
    _reset_counter: int = 0

    def update(self, tv: "TensionVector") -> Phase:
        # ── 1. Aktualizacja Nastrojów (Fast Attack / Slow Decay) ──
        def calc_mood(current, target, inertia_mod=1.0):
            attack = self.MOOD_ATTACK * inertia_mod
            if target > current:
                return (attack * current + (1 - attack) * target)
            else:
                return (self.MOOD_DECAY * current + (1 - self.MOOD_DECAY) * target)

        # Inercja Aksjologiczna: Wysokie Tv sprawia, że Afekt (Ta) reaguje wolniej (większa masa)
        ta_inertia = 1.0 + (self.mood_tv * self.PHI)
        
        # Jeśli logika jest silna, wartości mają większą siłę (integrytet)
        if self.mood_tc > self.INV_PHI:
            ta_inertia *= 1.4

        self.mood_ta = calc_mood(self.mood_ta, tv.affective, 1.0 / ta_inertia)
        self.mood_tc = calc_mood(self.mood_tc, tv.cognitive)

        # ── BLOKADA STANU UMYSŁU (Logika vs Afekt) ──
        # Jeśli afekt jest b. wysoki, a dopamina niska -> Logika się blokuje
        if self.mood_ta > 0.75 and self.dopamine < 0.35:
            self.mood_tc *= 0.5 # Gwałtowny spadek/blokada logiki

        # Tv reaguje nieliniowo, ale w stresie (wysokie Ta) jego znaczenie spada
        boosted_tv_input = tv.axiological ** 0.5
        if self.mood_ta > 0.85:
            boosted_tv_input *= 0.6 # Wartości tracą znaczenie, gdy dominuje afekt

        self.mood_tv = calc_mood(self.mood_tv, boosted_tv_input)

        # ── 2. Obliczanie Spójności (C) - Meta-Parametr ──
        # C = PHI - |(Ta * Tc) - Tv| -> dążymy do rezonansu między tym co czujemy a wartościami
        dissonance = abs((self.mood_ta * self.mood_tc) - self.mood_tv)
        old_cohesion = self.coherence
        self.coherence = max(0.05, min(1.0, self.INV_PHI - dissonance + 0.382)) # 0.382 = PHI - 1.236... offset

        # ── 3. Ekonomia Dopaminy (Paliwo i Nagroda) ──
        # A. Bazowe zużycie (koszt myślenia)
        effort = self.mood_tc * self.COGNITIVE_COST
        if self.coherence < self.INV_PHI:
            effort *= 1.5 # Wyższy koszt przy braku spójności (tarcie)
        
        # B. Nagroda (D_gain) za wzrost spójności i gęstość sensu
        c_gain = max(0, self.coherence - old_cohesion)
        meaning_density = (self.mood_ta * self.mood_tc) ** (self.mood_tv + 0.1)
        reward = (c_gain * self.PHI) + (meaning_density * 0.12)
        
        # C. Homeostaza (dryf w stronę INV_PHI)
        drift = (self.INV_PHI - self.dopamine) * 0.1
        
        self.dopamine = max(0.05, min(1.0, self.dopamine - effort + reward + drift))

        # ── 4. Mechanizm Resetu Synaptycznego ──
        if self.coherence < 0.2:
            self._reset_counter += 1
            if self._reset_counter >= self.RESET_THRESHOLD:
                self.phase = Phase.KATHARSIS
                self.dopamine = 0.1 # Całkowite wyczerpanie
                self._reset_counter = 0
        else:
            self._reset_counter = max(0, self._reset_counter - 1)
            
        # ── 5. Określanie Fazy ──
        # ── 5. Zakotwiczenie (Anchor/S) ──
        if tv.axiological > 0.5:
            self.anchor = max(0.0, self.anchor - (tv.axiological - 0.5) * 0.05)
        else:
            self.anchor = min(1.0, self.anchor + 0.018)

        # ── 6. Określanie Fazy ──
        if self.phase != Phase.KATHARSIS:
            if tv.magnitude > 0.6: self.phase = Phase.TENSION
            else: self.phase = Phase.HARMONY
        
        return self.phase

    @property
    def trend(self) -> str:
        if len(self._history) < 3:
            return "---"
        delta = self._history[-1] - self._history[0]
        return "rosnace" if delta > 0.08 else ("opadajace" if delta < -0.08 else "stabilne")

    def snapshot(self) -> dict[str, float]:
        return {
            "anchor": self.anchor,
            "arousal": self.arousal,
            "coherence": self.coherence,
            "dopamine": self.dopamine,
            "motto": self.motto,
            "mood_ta": self.mood_ta,
            "mood_tc": self.mood_tc,
            "mood_tv": self.mood_tv
        }

    def as_dict(self) -> dict:
        return {
            "S (anchor)": round(self.anchor, 3),
            "A (arousal)": round(self.arousal, 3),
            "C (coherence)": round(self.coherence, 3),
            "dopamine": round(self.dopamine, 3),
            "motto": self.motto,
            "mood_ta": round(self.mood_ta, 3),
            "mood_tc": round(self.mood_tc, 3),
            "mood_tv": round(self.mood_tv, 3),
            "phase": self.phase.value,
            "trend": self.trend
        }
