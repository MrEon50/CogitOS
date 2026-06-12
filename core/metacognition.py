"""
MetaCognitionEngine — Lustro Myśli.

Warstwa metapoznawcza, która wybiera STRATEGIĘ myślenia (jak myśleć),
a nie tylko treść (co myśleć). Uczy się skuteczności strategii
przez pętlę zwrotną z ReflectionService.

Realizuje wizję z Ulepszenie.txt:
- Od "Pamiętania odpowiedzi" do "Budowania strategii"
- Architektura "Lustra Myśli" (Feedback Loop)
- Inteligencja Dynamiczna (adaptacja do zmiany reguł)
"""
from typing import Optional, Dict
from .thinking_strategy import ThinkingStrategy, StrategyRegistry
from .psyche import Psyche
from .moment import ConsciousMoment


class MetaCognitionEngine:
    """
    Silnik metapoznawczy — wybiera i ewaluuje strategie myślenia.
    
    Pipeline:
    1. select_strategy() — przed generacją odpowiedzi
    2. format_instruction() — konwertuje strategię na instrukcję dla LLM
    3. evaluate_outcome() — po refleksji, aktualizuje wagi
    """

    def __init__(self):
        self.registry = StrategyRegistry()
        self._current_strategy: Optional[ThinkingStrategy] = None
        self._strategy_history: list[str] = []  # Ostatnie N użytych strategii

    def select_strategy(self, moment: ConsciousMoment, psyche: Psyche, 
                        step_n: int = 0) -> ThinkingStrategy:
        """
        Wybiera strategię myślenia na podstawie aktualnego kontekstu kognitywnego.
        
        Buduje kontekst z:
        - Psyche (nastroje, dopamina, spójność, faza)
        - ConsciousMoment (percepcja, rezonans, bogactwo kontekstu)
        - Stan konwersacji (numer kroku)
        """
        # Buduj kontekst decyzyjny
        context = {
            # Z Psyche (nastroje)
            "mood_ta": psyche.mood_ta,
            "mood_tc": psyche.mood_tc,
            "mood_tv": psyche.mood_tv,
            "coherence": psyche.coherence,
            "dopamine": psyche.dopamine,
            "anchor": psyche.anchor,
            "arousal": psyche.arousal,
            
            # Z Percept (bodziec)
            "emotional_charge": abs(moment.percept.emotional_charge),
            "semantic_density": moment.percept.semantic_density,
            "value_challenge": moment.percept.value_challenge,
            
            # Z Moment (pamięć)
            "resonance": moment.resonance,
            "context_richness": moment.context_richness,
            
            # Stan konwersacji
            "step_n": step_n,
        }

        strategy = self.registry.select_best(context)
        self._current_strategy = strategy
        
        # Historia (max 10)
        self._strategy_history.append(strategy.name)
        if len(self._strategy_history) > 10:
            self._strategy_history = self._strategy_history[-10:]

        return strategy

    def format_instruction(self, strategy: ThinkingStrategy) -> str:
        """Formatuje strategię jako instrukcję do wstrzyknięcia w prompt systemowy."""
        confidence = f"{strategy.weight:.0%}"
        usage_info = (
            f"(użyta {strategy.usage_count}x, skuteczność: {strategy.success_rate:.0%})"
            if strategy.usage_count > 0
            else "(nowa strategia — oceń jej przydatność)"
        )
        
        return (
            f"\n[AKTYWNA STRATEGIA MYŚLENIA — LUSTRO MYŚLI]\n"
            f"Metodologia: {strategy.label}\n"
            f"Pewność wyboru: {confidence} {usage_info}\n"
            f"Instrukcja: {strategy.description}\n"
            f"Zastosuj tę strategię do swojej odpowiedzi. "
            f"Jeśli uważasz, że jest nieodpowiednia dla tego pytania, "
            f"powiedz DLACZEGO i zaproponuj lepsze podejście.\n"
        )

    def evaluate_outcome(self, reflection: dict) -> None:
        """
        Pętla zwrotna — aktualizuje wagę aktywnej strategii.
        
        Wywoływana po ReflectionService z danymi:
        - strategy_fit: float (0.0-1.0) — jak dobrze strategia pasowała
        - strategy_note: str — opcjonalny komentarz
        """
        if self._current_strategy is None:
            return

        strategy_fit = reflection.get("strategy_fit", 0.5)
        
        # Dodatkowe sygnały sukcesu/porażki z samej refleksji
        coherence_delta = reflection.get("coherence_delta", 0.0)
        dopamine_delta = reflection.get("dopamine_delta", 0.0)
        
        # Bonus/kara za korelację z pozytywnymi wynikami
        adjusted_fit = strategy_fit
        if coherence_delta > 0:
            adjusted_fit = min(1.0, adjusted_fit + 0.1)
        elif coherence_delta < -0.05:
            adjusted_fit = max(0.0, adjusted_fit - 0.1)
            
        if dopamine_delta > 0.05:
            adjusted_fit = min(1.0, adjusted_fit + 0.05)

        self.registry.update_strategy(self._current_strategy.name, adjusted_fit)

    @property
    def current_strategy_name(self) -> Optional[str]:
        return self._current_strategy.name if self._current_strategy else None

    @property
    def current_strategy_label(self) -> Optional[str]:
        return self._current_strategy.label if self._current_strategy else None

    def get_dashboard_data(self) -> dict:
        """Dane do wyświetlenia w dashboardzie frontend."""
        return {
            "active_strategy": {
                "name": self._current_strategy.name if self._current_strategy else None,
                "label": self._current_strategy.label if self._current_strategy else "Brak",
                "weight": round(self._current_strategy.weight, 2) if self._current_strategy else 0,
                "usage_count": self._current_strategy.usage_count if self._current_strategy else 0,
            },
            "all_strategies": [
                {
                    "name": s.name,
                    "label": s.label,
                    "weight": round(s.weight, 2),
                    "usage_count": s.usage_count,
                    "success_rate": round(s.success_rate, 2),
                }
                for s in self.registry.strategies
            ],
            "history": self._strategy_history[-5:],  # Ostatnie 5
        }
