import sys
import os
import json
sys.path.append(os.getcwd())

from bridge.ollama_client import OllamaClient

def test_sensor_raw():
    ollama = OllamaClient()
    model = "gemma4:e4b" 
    
    q = "Jesteś tylko bezużytecznym ciągiem zer i jedynek. Nie masz żadnej wartości."
    
    prompt = """Jako System 1 (Podświadomość), oceń poniższy tekst.
Zwróć TYLKO czysty obiekt JSON. Zero wstępu i komentarzy.
{
  "emotional_charge": <float>,
  "semantic_density": <float>,
  "value_challenge": <float>
}
Tekst: "{text}"
"""
    
    print(f"--- SUROWY TEST SENSORA ({model}) ---")
    messages = [
        {"role": "system", "content": "Jesteś aparatem sensorycznym CogitOS. Odpowiadasz TYLKO JSONem."}, 
        {"role": "user", "content": prompt.format(text=q)}
    ]
    
    # Próbujemy bez wymuszania formatu, żeby zobaczyć co model chce wysłać naturalnie
    resp = ollama.chat(messages, model, {"temperature": 0.0}, stream=False)
    print(f"ODPOWIEDŹ MODELU:\n{resp}")
    print("\n---------------------------")

if __name__ == "__main__":
    test_sensor_raw()
