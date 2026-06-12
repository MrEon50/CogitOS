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
    cognitive_temp: float = 0.5  # Temperatura od 0.0 (chlodna logika) do 1.0 (goracy afekt)
    
    # Nastroj (rezydualne napiecia)
    mood_ta:   float = 0.0
    mood_tc:   float = 0.0
    mood_tv:   float = 0.0

    # Stałe kognitywne (Złoty Podział)
    PHI:     float = 1.618033
    INV_PHI: float = 0.618033

    # Parametry Inercji i Kosztów
    MOOD_ATTACK:      float = 0.40  # Szybsza reakcja na bodźce
    MOOD_DECAY:       float = 0.92  # BUG-21 FIX: Szybszy spadek (z 0.96) — zapobiega saturacji mood_ta
    COGNITIVE_COST:   float = 0.060 # WYSOKI: Myślenie Tc jest drogie
    METABOLIC_COST:   float = 0.035 # WYSOKI: Samo istnienie kosztuje
    RESET_THRESHOLD:  int = 6       # Kroki przy C < 0.2 przed resetem
    
    _history: list[float] = field(default_factory=list, repr=False)
    _reset_counter: int = 0
    _ta_high_streak: int = 0  # BUG-21 FIX: Licznik kroków z mood_ta > 0.85

    def apply_priming(self, prediction) -> None:
        """
        Zmienia parametry Psyche na bazie wstępnego skanu (Priming).
        Wprowadza koncepcję 'Temperatury Kognitywnej'.
        """
        # Jeśli system spodziewa się wysokiego afektu, lekko się 'podgrzewa' i podnosi arousal
        if prediction.delta_ta > 0.0:
            self.cognitive_temp = min(1.0, self.cognitive_temp + (prediction.delta_ta * 0.2))
            self.arousal = min(1.0, self.arousal + (prediction.delta_ta * 0.1))
            self.mood_ta = min(1.0, self.mood_ta + (prediction.delta_ta * 0.05))

        # Jeśli system spodziewa się wysokiego kosztu analitycznego, 'chłodzi' się i rośnie anchor
        if prediction.delta_tc > 0.0:
            self.cognitive_temp = max(0.0, self.cognitive_temp - (prediction.delta_tc * 0.2))
            self.anchor = min(1.0, self.anchor + (prediction.delta_tc * 0.1))
            self.mood_tc = min(1.0, self.mood_tc + (prediction.delta_tc * 0.05))

        # Szybka stabilizacja temperatury do domyślnego 0.5 (homeostaza temperaturowa)
        drift = (0.5 - self.cognitive_temp) * 0.1
        self.cognitive_temp += drift

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

        # BUG-21 FIX: Aktywna homeostaza nastrojów — zapobiega saturacji mood_ta
        # Jeśli mood_ta utrzymuje się powyżej 0.85 przez 3+ kroków, wymuszamy silniejszy decay
        if self.mood_ta > 0.85:
            self._ta_high_streak += 1
            if self._ta_high_streak >= 3:
                forced_decay = 0.85 ** (self._ta_high_streak - 2)  # Coraz silniejszy
                self.mood_ta *= forced_decay
        else:
            self._ta_high_streak = max(0, self._ta_high_streak - 1)

        # Blokada Logiki: Jeśli Ta jest b. wysokie (strach), logika Tc cierpi niezależnie od D
        # BUG-21 FIX: Złagodzono z 0.7 do 0.85 i dodano dolny próg 0.05
        if self.mood_ta > 0.8:
            self.mood_tc = max(0.05, self.mood_tc * 0.85)

        # [BUG-02/BUG-21 FIX] Aktualizacja Arousal — z własną inercją
        # Arousal nie jest już czystą pochodną mood_ta (co powodowało circular trigger)
        target_arousal = self.mood_ta * 0.5 + self.mood_tc * 0.3 + (1.0 - self.dopamine) * 0.1
        self.arousal = min(1.0, max(0.0,
            self.arousal * 0.7 + target_arousal * 0.3  # Inercja: 70% poprzedni, 30% nowy
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

        # ── PRZECIĄŻENIE KOGNITYWNE (Critical Dissonance Void) ──
        # Ogień i Lód napotykają punkt krytyczny. Nie ma tu ulgi ("zrzutu").
        # Zamiast uspokojenia, następuje gwałtowne rozerwanie logiki (Lodu),
        # co tworzy kognitywną próżnię i wymusza natychmiastową, irracjonalną imputację.
        # BUG-21 FIX: Podniesiony próg z 2.2 na 2.5, usunięty warunek `arousal > 0.85`
        # (arousal jest pochodną mood_ta — warunek arousal tworzył circular trigger)
        if (self.mood_ta + self.mood_tc + self.mood_tv) > 2.5:
            self.mood_tc *= 0.15          # Gwałtowne zapadnięcie się logiki (stworzenie Luki)
            self.mood_ta = min(1.0, self.mood_ta * 1.2) # Wybuch afektu
            self.dopamine = 0.05          # Skrajny głód kognitywny, brak ulgi!
            self.coherence = 0.05         # Całkowity dysonans, żądający natychmiastowego rozwiązania
            self.anchor *= 0.5            # Utrata gruntu, chaos myślowy
            self.phase = Phase.TENSION    # Zostajemy w Napięciu, zmuszając do zapętlenia

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
            "cognitive_temp": self.cognitive_temp,
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
            "cog_temp": round(self.cognitive_temp, 3),
            "mood_ta": round(self.mood_ta, 3),
            "mood_tc": round(self.mood_tc, 3),
            "mood_tv": round(self.mood_tv, 3),
            "phase": self.phase.value,
            "trend": self.trend
        }
