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
    MOOD_ATTACK:      float = 0.40  # Szybsza reakcja na bodźce
    MOOD_DECAY:       float = 0.96  # Wolniejszy spadek (system dłużej 'pamięta' stres)
    COGNITIVE_COST:   float = 0.060 # WYSOKI: Myślenie Tc jest drogie
    METABOLIC_COST:   float = 0.035 # WYSOKI: Samo istnienie kosztuje
    RESET_THRESHOLD:  int = 6       # Kroki przy C < 0.2 przed resetem
    
    _history: list[float] = field(default_factory=list, repr=False)
    _reset_counter: int = 0

    def update(self, tv: "TensionVector") -> Phase:
        # ── 1. Aktualizacja Nastrojów ──
        def calc_mood(current, target, inertia_mod=1.0):
            attack = min(0.95, self.MOOD_ATTACK * inertia_mod) # Clamp zabezpieczający
            if target > current:
                return (attack * current + (1 - attack) * target)
            else:
                return (self.MOOD_DECAY * current + (1 - self.MOOD_DECAY) * target)

        # Inercja Aksjologiczna + Wpływ Dopaminy na Strach
        # Wysoka D = mniejsza wrażliwość na strach. Niska D = wysoka wrażliwość.
        d_sensitivity = 2.0 - self.dopamine # 1.0 (przy D=1.0) do 1.95 (przy D=0.05)
        ta_inertia = (1.0 + (self.mood_tv * self.PHI)) / d_sensitivity

        self.mood_ta = calc_mood(self.mood_ta, tv.affective, 1.0 / ta_inertia)
        self.mood_tc = calc_mood(self.mood_tc, tv.cognitive)

        # Blokada Logiki: Jeśli Ta jest b. wysokie (strach), logika Tc cierpi niezależnie od D
        if self.mood_ta > 0.8:
            self.mood_tc *= 0.7 

        # [BUG-02 FIX] Aktualizacja Arousal — dynamiczne pobudzenie
        self.arousal = min(1.0, max(0.0,
            self.mood_ta * 0.6 + self.mood_tc * 0.3 + (1.0 - self.dopamine) * 0.1
        ))

        # Tv reaguje na wartości, ale w afekcie jego głos jest słabszy
        boosted_tv_input = tv.axiological ** 0.5
        if self.mood_ta > 0.7:
            boosted_tv_input *= (1.0 - self.mood_ta * 0.5)

        self.mood_tv = calc_mood(self.mood_tv, boosted_tv_input)

        # ── 2. Obliczanie Spójności (C) ──
        dissonance = abs((self.mood_ta * self.mood_tc) - self.mood_tv)
        old_cohesion = self.coherence
        self.coherence = max(0.05, min(1.0, self.INV_PHI - dissonance + 0.382))

        # ── 3. Ekonomia Dopaminy (Bez przebaczenia) ──
        # A. Koszt (Metabolizm + Wysiłek + Tarcie)
        friction = 2.5 if self.coherence < self.INV_PHI else 1.0
        effort = (self.METABOLIC_COST + (self.mood_tc * self.COGNITIVE_COST)) * friction
        
        # B. Nagroda (Trudno dostępna)
        learning_bonus = (self.mood_tc * 0.02) if self.coherence > 0.9 else 0
        c_gain = max(0, self.coherence - old_cohesion)
        # Nagroda za sens wymaga wysokiego Tv (wartości)
        meaning_density = (self.mood_ta * self.mood_tc) * self.mood_tv
        reward = (c_gain * 0.2) + (meaning_density * 0.05) + learning_bonus
        
        # C. Homeostaza (Ekstremalnie silny dryf do 0.618)
        drift = (self.INV_PHI - self.dopamine) * 0.4
        
        self.dopamine = max(0.05, min(1.0, self.dopamine - effort + reward + drift))

        # ── KATARZIS DYNAMICZNA (Minimalna i rzadka) ──
        # Tylko przy euforii (D > 0.8) i realnym sukcesie kognitywnym
        if self.dopamine > 0.8 and reward > 0.1:
            relief_factor = 0.95 # Tylko 5% spadku napięcia
            self.mood_ta *= relief_factor
            self.mood_tc *= relief_factor
            self.mood_tv *= relief_factor

        # ── LĘK PRZED PUSTKĄ ──
        if self.dopamine < 0.35:
            self.mood_ta = min(1.0, self.mood_ta + (0.35 - self.dopamine) * 0.05)

        # ── 4. Mechanizm Resetu Synaptycznego ──
        if self.coherence < 0.2:
            self._reset_counter += 1
            if self._reset_counter >= self.RESET_THRESHOLD:
                self.phase = Phase.KATHARSIS
                self.dopamine = 0.1 # Całkowite wyczerpanie
                self._reset_counter = 0
        else:
            self._reset_counter = max(0, self._reset_counter - 1)
            
        # ── 5. Zakotwiczenie (Anchor/S) ──
        if tv.axiological > 0.5:
            self.anchor = max(0.0, self.anchor - (tv.axiological - 0.5) * 0.05)
        else:
            self.anchor = min(1.0, self.anchor + 0.018)

        # ── 6. Określanie Fazy ──
        if self.phase != Phase.KATHARSIS:
            if tv.magnitude > 0.6: self.phase = Phase.TENSION
            else: self.phase = Phase.HARMONY

        # ── 7. Historia (BUG-03 FIX) ──
        self._history.append(self.coherence)
        if len(self._history) > 10:
            self._history = self._history[-10:]
        
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
