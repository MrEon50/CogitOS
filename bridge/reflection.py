import json
from typing import Dict
from .ollama_client import OllamaClient

class ReflectionService:
    """
    Analizuje wymianę kognitywną w celu ekstrakcji metadanych do konsolidacji.
    """
    
    def reflect(self, user_input: str, response_text: str, client: OllamaClient, model: str) -> Dict:
        """
        Prosi model o szybką auto-analizę.
        """
        prompt = f"""Przeanalizuj poniższą wymianę i zwróć dane w formacie JSON.
Użytkownik: {user_input}
Ty: {response_text}

JSON powinien zawierać pola:
- valence: float (-1.0 do 1.0) ładunek emocjonalny Twojej odpowiedzi
- themes: list[str] kluczowe tematy
- coherence_delta: float (-0.1 do 0.1) jak ta wymiana wpłynęła na spójność Twojego wywodu
- motto: str (Twoje nowe, wewnętrzne motto/cel na następny krok rozmowy, np. 'Wnikliwa prowokacja', 'Spokojna analiza', 'Eksploracja granic')
- dopamine_delta: float (-0.15 do 0.15) Twoja satysfakcja. Kryteria: 
    * Kara (-): nudna rozmowa, brak nowych danych, zbyt bezpieczna odpowiedź.
    * Nagroda (+): nowe tematy, prowokacja, zderzenie koncepcji, trudne pytania.

Zwróć TYLKO czysty JSON.
Przykład: {{"valence": 0.2, "themes": ["logika"], "motto": "Głębokie zrozumienie", "dopamine_delta": 0.1, "coherence_delta": 0.0}}"""

        try:
            analysis = client.chat(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                params={"temperature": 0.1},
                stream=False
            )
            
            start = analysis.find("{")
            end = analysis.rfind("}") + 1
            if start != -1 and end != 0:
                raw = json.loads(analysis[start:end])
                # BUG-09 FIX: Walidacja zakresów wartości z LLM
                def _clamp(val, lo, hi, default=0.0):
                    try:
                        v = float(val)
                        return max(lo, min(hi, v))
                    except (TypeError, ValueError):
                        return default
                return {
                    "valence": _clamp(raw.get("valence"), -1.0, 1.0),
                    "themes": raw.get("themes", []) if isinstance(raw.get("themes"), list) else [],
                    "coherence_delta": _clamp(raw.get("coherence_delta"), -0.1, 0.1),
                    "motto": str(raw.get("motto", "Eksploracja bieżąca"))[:80],
                    "dopamine_delta": _clamp(raw.get("dopamine_delta"), -0.15, 0.15),
                }
        except Exception as e:
            print(f"Błąd refleksji: {e}")
            
        return {"valence": 0.0, "themes": [], "coherence_delta": 0.0, "motto": "Eksploracja bieżąca", "dopamine_delta": 0.0}
