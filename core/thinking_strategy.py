"""
ThinkingStrategy — Strategie Metodologii Myślenia.

Każda strategia to zestaw instrukcji JAK myśleć (nie CO myśleć).
Wagi ewoluują przez pętlę zwrotną z ReflectionService.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ThinkingStrategy:
    """Jedna strategia myślenia z trackowaną skutecznością."""
    name: str                     # Identyfikator (np. "eliminacja")
    label: str                    # Czytelna nazwa (np. "Metoda Eliminacji")
    description: str              # Instrukcja dla LLM — JAK myśleć
    conditions: Dict[str, float]  # Progi aktywacji (klucz → min. wartość)
    weight: float = 0.5           # Skuteczność (0.0 – 1.0), uczy się
    usage_count: int = 0
    success_sum: float = 0.0      # Suma ocen strategy_fit z refleksji

    @property
    def success_rate(self) -> float:
        if self.usage_count == 0:
            return 0.5  # Domyślna (neutralna) ocena
        return self.success_sum / self.usage_count

    def record_usage(self, strategy_fit: float) -> None:
        """Rejestruje użycie strategii i aktualizuje wagę."""
        self.usage_count += 1
        self.success_sum += max(0.0, min(1.0, strategy_fit))

        # Adaptacyjna aktualizacja wagi: EMA (Exponential Moving Average)
        alpha = 0.3  # Szybkość uczenia
        self.weight = (1.0 - alpha) * self.weight + alpha * strategy_fit
        self.weight = max(0.1, min(1.0, self.weight))  # Clamp


def _build_default_strategies() -> List[ThinkingStrategy]:
    """Zwraca 7 wbudowanych strategii myślenia."""
    return [
        ThinkingStrategy(
            name="eliminacja",
            label="Metoda Eliminacji",
            description=(
                "Wymień wszystkie możliwe odpowiedzi lub hipotezy. "
                "Systematycznie wyklucz każdą, podając konkretny powód eliminacji. "
                "Zostaw jedną — najsilniejszą — i uzasadnij, dlaczego przetrwała."
            ),
            conditions={"mood_tc": 0.3, "semantic_density": 0.4},
        ),
        ThinkingStrategy(
            name="analogia",
            label="Myślenie przez Analogię",
            description=(
                "Znajdź 2-3 znane dziedziny lub zjawiska, które mają analogiczną "
                "strukturę do omawianego problemu. Użyj tych analogii jako rusztowania "
                "do zbudowania odpowiedzi. Wyraźnie zaznacz, gdzie analogia się łamie."
            ),
            conditions={"resonance": -0.1},  # Niska resonance = nowy temat
        ),
        ThinkingStrategy(
            name="dekompozycja",
            label="Dekompozycja Problemu",
            description=(
                "Rozłóż problem na 3-5 niezależnych pod-problemów. "
                "Rozwiąż każdy osobno, a następnie zsyntetyzuj odpowiedzi "
                "w spójną całość. Zaznacz zależności między pod-problemami."
            ),
            conditions={"semantic_density": 0.5},
        ),
        ThinkingStrategy(
            name="dialektyka",
            label="Dialektyka (Teza-Antyteza-Synteza)",
            description=(
                "Sformułuj wyraźną TEZĘ dotyczącą problemu. "
                "Następnie sformułuj równie silną ANTYTEZĘ. "
                "Pokaż punkt, gdzie obie pozycje się łamią. "
                "Zbuduj SYNTEZĘ, która przekracza obie perspektywy."
            ),
            conditions={"mood_tv": 0.3, "value_challenge": 0.3},
        ),
        ThinkingStrategy(
            name="symulacja",
            label="Symulacja Scenariuszy",
            description=(
                "Wyobraź sobie 3 scenariusze rozwoju sytuacji: "
                "optymistyczny, pesymistyczny, i nieoczekiwany (wildcard). "
                "Dla każdego opisz kluczowe konsekwencje i punkty zwrotne. "
                "Wskaż, który scenariusz jest najbardziej prawdopodobny i dlaczego."
            ),
            conditions={"mood_ta": 0.3, "emotional_charge": 0.3},
        ),
        ThinkingStrategy(
            name="samokrytyka",
            label="Autoweryfikacja (Samokrytyka)",
            description=(
                "Zanim odpowiesz, sformułuj swoje kluczowe ZAŁOŻENIE. "
                "Sprawdź: Czy to założenie jest logiczne? Co je podważa? "
                "Jeśli znajdziesz słabość, skoryguj swoje rozumowanie ZANIM podasz wynik. "
                "Pokaż użytkownikowi tę korektę jawnie."
            ),
            conditions={"coherence": -0.6},  # Niska coherence = potrzeba weryfikacji
        ),
        ThinkingStrategy(
            name="krystalizacja",
            label="Krystalizacja Wiedzy",
            description=(
                "Skondensuj dotychczasowe ustalenia w 3 kluczowe zdania. "
                "Wyraźnie rozdziel: co jest PEWNE (potwierdzone), "
                "co jest WĄTPLIWE (wymaga dalszej weryfikacji), "
                "i co jest NOWE (pojawiło się w tej wymianie)."
            ),
            conditions={"dopamine": 0.5, "step_min": 5},  # Długa rozmowa
        ),
    ]


class StrategyRegistry:
    """Rejestr strategii z mechanizmem selekcji i uczenia."""

    def __init__(self):
        self.strategies: List[ThinkingStrategy] = _build_default_strategies()
        self._last_selected: Optional[str] = None

    def score_strategy(self, strategy: ThinkingStrategy, context: dict) -> float:
        """Oblicza trafność strategii dla danego kontekstu kognitywnego.
        
        context keys: mood_ta, mood_tc, mood_tv, coherence, dopamine,
                      semantic_density, emotional_charge, value_challenge,
                      resonance, step_n
        """
        relevance = 0.0
        matches = 0
        total_conditions = len(strategy.conditions)

        for key, threshold in strategy.conditions.items():
            ctx_val = context.get(key, 0.0)
            
            # Specjalne warunki
            if key == "step_min":
                if context.get("step_n", 0) >= threshold:
                    relevance += 1.0
                    matches += 1
                continue
            
            if key == "resonance" and threshold < 0:
                # Odwrócony warunek: aktywuj gdy resonance jest NISKA
                if ctx_val < abs(threshold):
                    relevance += 1.0 - ctx_val  # Im niższa, tym lepsza
                    matches += 1
                continue

            if key == "coherence" and threshold < 0:
                # Odwrócony warunek: aktywuj gdy coherence jest NISKA
                if ctx_val < abs(threshold):
                    relevance += 1.0 - ctx_val
                    matches += 1
                continue

            # Standardowy warunek: wartość powyżej progu
            if ctx_val >= threshold:
                relevance += min(1.0, ctx_val / max(0.01, threshold))
                matches += 1

        if total_conditions == 0:
            return strategy.weight * 0.5

        # Score = trafność kontekstowa × waga (skuteczność historyczna)
        match_ratio = matches / total_conditions
        return (relevance / total_conditions) * match_ratio * strategy.weight

    def select_best(self, context: dict) -> ThinkingStrategy:
        """Wybiera najlepszą strategię dla kontekstu. Unika powtórzeń."""
        scored = []
        for s in self.strategies:
            score = self.score_strategy(s, context)
            # Kara za powtórzenie tej samej strategii (zachęca do eksploracji)
            if s.name == self._last_selected:
                score *= 0.6
            scored.append((score, s))

        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][1] if scored else self.strategies[0]
        self._last_selected = best.name
        return best

    def update_strategy(self, strategy_name: str, strategy_fit: float) -> None:
        """Aktualizuje wagę strategii na podstawie feedbacku z refleksji."""
        for s in self.strategies:
            if s.name == strategy_name:
                s.record_usage(strategy_fit)
                return

    def as_dict(self) -> dict:
        """Serializacja do zapisu."""
        return {
            "strategies": [
                {
                    "name": s.name,
                    "weight": round(s.weight, 4),
                    "usage_count": s.usage_count,
                    "success_sum": round(s.success_sum, 4),
                }
                for s in self.strategies
            ],
            "last_selected": self._last_selected
        }

    def load_weights(self, data: dict) -> None:
        """Odtwarzanie wag z zapisu."""
        strategy_map = {s.name: s for s in self.strategies}
        for s_data in data.get("strategies", []):
            name = s_data.get("name")
            if name in strategy_map:
                strategy_map[name].weight = s_data.get("weight", 0.5)
                strategy_map[name].usage_count = s_data.get("usage_count", 0)
                strategy_map[name].success_sum = s_data.get("success_sum", 0.0)
        self._last_selected = data.get("last_selected")
