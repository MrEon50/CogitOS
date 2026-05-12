import json
import os
from pathlib import Path
from dataclasses import asdict
from core import MindCore, Psyche, EngramStore, Engram, Phase

class StateManager:
    """
    Zarządza zapisem i odczytem stanu kognitywnego CogitOS.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.state_file = self.data_dir / "mind_state.json"

    def save_all(self, mind: MindCore) -> None:
        """Zapisuje cały stan MindCore do JSON."""
        state = {
            "step_n": mind.step_n,
            "psyche": {
                "anchor": mind.psyche.anchor,
                "arousal": mind.psyche.arousal,
                "coherence": mind.psyche.coherence,
                "phase": mind.psyche.phase.name,
                "dopamine": mind.psyche.dopamine,
                "motto": mind.psyche.motto,
                "mood_ta": mind.psyche.mood_ta,
                "mood_tc": mind.psyche.mood_tc,
                "mood_tv": mind.psyche.mood_tv,
                "history": mind.psyche._history
            },
            "engrams": [
                {
                    "text": e.text,
                    "features": e.features,
                    "embedding": e.embedding,
                    "valence": e.valence,
                    "strength": e.strength,
                    "recency": e.recency,
                    "step_formed": e.step_formed,
                    "timestamp": e.timestamp
                } for e in mind.memory._store
            ]
        }
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def load_all(self, memory_capacity: int = 64) -> MindCore:
        """Wczytuje stan MindCore. Zwraca nową instancję jeśli brak zapisu."""
        mind = MindCore(memory_capacity=memory_capacity)
        
        if not self.state_file.exists():
            return mind

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            mind.step_n = state.get("step_n", 0)
            
            # Odtwarzanie Psyche
            p_data = state.get("psyche", {})
            mind.psyche.anchor = p_data.get("anchor", 1.0)
            mind.psyche.arousal = p_data.get("arousal", 0.2)
            mind.psyche.coherence = p_data.get("coherence", 0.9)
            mind.psyche.dopamine = p_data.get("dopamine", 0.5)
            mind.psyche.motto = p_data.get("motto", "Eksploracja bieżąca")
            mind.psyche.mood_ta = p_data.get("mood_ta", 0.0)
            mind.psyche.mood_tc = p_data.get("mood_tc", 0.0)
            mind.psyche.mood_tv = p_data.get("mood_tv", 0.0)
            mind.psyche.phase = Phase[p_data.get("phase", "HARMONY")]
            mind.psyche._history = p_data.get("history", [])

            # Odtwarzanie Engramów
            for e_data in state.get("engrams", []):
                eng = Engram(
                    text=e_data["text"],
                    features=e_data["features"],
                    embedding=e_data.get("embedding", []),
                    valence=e_data["valence"],
                    strength=e_data["strength"],
                    recency=e_data["recency"],
                    step_formed=e_data["step_formed"],
                    timestamp=e_data.get("timestamp", "")
                )
                mind.memory._store.append(eng)

        except Exception as e:
            print(f"Błąd podczas wczytywania stanu: {e}")
            
        return mind
