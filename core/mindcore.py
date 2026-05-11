from .psyche import Psyche, Phase
from .engram import EngramStore, Engram
from .percept import Percept
from .moment import ConsciousMoment
from .tension import TensionVector

class MindCore:
    """
    Centrum integracji kognitywnej CogitOS.
    """
    def __init__(self, memory_capacity: int = 64):
        self.psyche  = Psyche()
        self.memory  = EngramStore(capacity=memory_capacity)
        self.step_n  = 0

    def step(self, user_input: str, embedding: list[float] = None, continuity: bool = True, apperception_data: dict = None) -> dict:
        self.step_n += 1

        # 1. Percept (Heurystyka AI lub fallback do heurystyki sztywnej)
        if apperception_data:
            percept = Percept.from_apperception(user_input, apperception_data, embedding=embedding)
        else:
            percept = Percept.from_text(user_input, embedding=embedding)

        # 2. Retrieval z uwzglednieniem ciaglosci
        all_engrams = self.memory.retrieve(percept, self.psyche, top_k=3)
        
        if not continuity:
            # Filtrujemy engramy: zostawiamy tylko te z biezacej sesji (step_n)
            # Lub po prostu ograniczamy retrieval do zera, jesli chcemy calkowitej amnezji wstecznej
            engrams = [e for e in all_engrams if e.step_formed >= self.step_n]
        else:
            engrams = all_engrams

        # 3. Moment świadomości
        moment = ConsciousMoment(
            percept=percept,
            engrams=engrams,
            psyche_snapshot=self.psyche.snapshot(),
        )

        # 4. Wektor napięć
        tv = moment.to_tension()

        # 5. Aktualizacja psyche
        phase = self.psyche.update(tv)

        # 6. Modulacja i Reward
        mod = response_modulation(tv, phase, moment)
        reward = compute_reward(tv, self.psyche, moment)

        # 7. Konsolidacja
        new_engram = consolidate(moment, self.step_n)
        self.memory.store(new_engram)

        return {
            "step":     self.step_n,
            "percept":  {"charge": percept.emotional_charge,
                         "density": percept.semantic_density,
                         "challenge": percept.value_challenge,
                         "features": list(percept.features.keys())},
            "memory":   {"engrams_total": len(self.memory),
                         "retrieved": len(engrams),
                         "resonance": round(moment.resonance, 3),
                         "richness": round(moment.context_richness, 3)},
            "tension":  tv.as_dict(),
            "mood_tension": {
                "T_a": round(self.psyche.mood_ta, 3),
                "T_c": round(self.psyche.mood_tc, 3),
                "T_v": round(self.psyche.mood_tv, 3)
            },
            "psyche":   self.psyche.as_dict(),
            "reward":   reward,
            "mode":     mod["mode"],
            "hint":     mod["hint"],
        }

    def reset(self) -> None:
        self.psyche = Psyche()
        self.memory = EngramStore(capacity=self.memory.capacity)
        self.step_n = 0

def response_modulation(tv: TensionVector, phase: Phase, moment: ConsciousMoment) -> dict:
    resonance_note = (
        f"Rezonuje {len(moment.engrams)} engramów (resonance={moment.resonance:.2f})."
        if moment.engrams else "Brak rezonujących wspomnień."
    )

    if phase == Phase.KATHARSIS:
        return {"mode": "grounding", "tone": "calm_assertive", "verbosity": "minimal",
                "hint": f"Wróć do fundamentów. Spokojnie, bez obrony. {resonance_note}"}
    if tv.affective > 0.58:
        return {"mode": "empathic_first", "tone": "warm", "verbosity": "moderate",
                "hint": f"Najpierw emocje, potem logika. {resonance_note}"}
    if tv.cognitive > 0.62:
        return {"mode": "analytical", "tone": "precise", "verbosity": "detailed",
                "hint": f"Rozbij złożoność krok po kroku. {resonance_note}"}
    if tv.axiological > 0.38:
        return {"mode": "values_grounded", "tone": "measured", "verbosity": "moderate",
                "hint": f"Bądź tym, kim jesteś. Wyrażaj, nie broń. {resonance_note}"}
    return {"mode": "balanced", "tone": "natural", "verbosity": "adaptive",
            "hint": f"Swobodny dialog. System w równowadze. {resonance_note}"}

def compute_reward(tv: TensionVector, psyche: Psyche, moment: ConsciousMoment) -> float:
    r_tension  = (1.0 - tv.magnitude)          * 0.35
    r_coherence = psyche.coherence             * 0.30
    r_anchor    = psyche.anchor                * 0.25
    r_context   = moment.context_richness      * 0.10
    return round(r_tension + r_coherence + r_anchor + r_context, 4)

def consolidate(moment: ConsciousMoment, step: int) -> Engram:
    p = moment.percept
    ps = moment.psyche_snapshot
    
    # Napięcia z momentu (zanim zostały zredukowane przez katarzis)
    ta = ps.get("mood_ta", 0.5)
    tv = ps.get("mood_tv", 0.5)
    
    # Siła wspomnienia zależy od 'śladu' emocjonalnego i aksjologicznego
    # Stres wykuwa pamięć (Flashbulb memory effect)
    intensity = (ta * 1.5) + (tv * 2.0)
    strength = 0.5 + (intensity * 0.5)

    return Engram(
        text=p.raw[:120],
        features=dict(p.features),
        embedding=list(p.embedding),
        valence=p.emotional_charge,
        strength=min(3.0, strength), # Pozwalamy na b. silne engramy (do 3.0)
        recency=1.0,
        step_formed=step,
    )
