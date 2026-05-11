from core import Psyche, Phase, TensionVector

class ParameterModulator:
    """
    Mapuje stan kognitywny Psyche na techniczne parametry modelu LLM.
    """
    
    def modulate(self, psyche: Psyche, tension: TensionVector) -> dict:
        # 1. Temperatura sterowana Pobudzeniem (A) - nieliniowo
        # Przy ekstremalnym A model wpada w 'chaos'
        temp = 0.3 + (psyche.arousal ** 1.5) * 1.2
        
        # 2. Top_P sterowane Zakotwiczeniem (S) 
        # Niskie S = 'panika' kognitywna, system trzyma sie tylko najbardziej prawdopodobnych tokenow
        tp = 0.1 + (psyche.anchor ** 2) * 0.9
        
        # 3. Repeat Penalty sterowane Spojnoscia (C)
        # Niska spojnosc = 'bełkot' lub trudnosc w doborze slow
        rp = 1.1 + (1.0 - psyche.coherence) * 1.2

        # 4. Dopamina wplywa na 'odwage' kognitywna
        if psyche.dopamine < 0.2:
            temp *= 0.5 # Apatia / Zamkniecie
            tp *= 0.5
        elif psyche.dopamine > 0.8:
            temp += 0.2 # Euforia / Nadaktywnosc

        params = {
            "temperature": round(min(1.9, temp), 2),
            "top_p": round(min(1.0, tp), 2),
            "repeat_penalty": round(min(2.5, rp), 2),
            "num_ctx": 8192,
        }
        
        if psyche.phase == Phase.KATHARSIS:
            params["temperature"] = 0.15
            params["top_p"] = 0.2
            params["repeat_penalty"] = 2.0
            
        return params
