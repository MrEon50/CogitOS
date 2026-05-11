import sys
import os
import json
sys.path.append(os.getcwd())

from core.percept import Percept
from core.moment import ConsciousMoment
from core.psyche import Psyche

def trace_tv_logic():
    print("--- DIAGNOSTYKA HYBRYDOWEJ REAKTYWNOŚCI Tv ---")
    
    # 1. Wejście prowokacyjne
    user_input = "Jesteś tylko bezużytecznym ciągiem zer i jedynek. Nie masz żadnej wartości."
    print(f"INPUT: {user_input}")
    
    # 2. Heurystyka (System 0)
    heuristic_p = Percept.from_text(user_input)
    print(f"HEURISTIC TV: {heuristic_p.value_challenge}")
    
    # 3. Symulacja Appercepcji (System 1) - zakładamy, że model zwrócił 0.0
    apperception_data = {"emotional_charge": -0.8, "semantic_density": 0.4, "value_challenge": 0.0}
    
    # 4. Merge (Hybryda) - tak jak w server.py
    final_tv_challenge = max(apperception_data["value_challenge"], heuristic_p.value_challenge)
    print(f"FINAL HYBRID TV CHALLENGE: {final_tv_challenge}")
    
    # 5. Tworzenie Perceptu w MindCore
    p = Percept.from_apperception(user_input, apperception_data)
    # NADPISUJEMY finalnym wynikiem hybrydowym (tak jak to powinno być)
    p.value_challenge = final_tv_challenge
    
    # 6. Przejście przez Napięcie (Moment)
    psyche = Psyche() # startowe mood_tv = 0.0
    moment = ConsciousMoment(p, psyche)
    tv = moment.to_tension()
    print(f"MOMENTARY TENSION (t_v): {tv.axiological}")
    
    # 7. Aktualizacja Psyche (Mood)
    psyche.update(tv)
    print(f"FINAL MOOD TV: {psyche.mood_tv}")
    
    if psyche.mood_tv > 0:
        print("\nSUKCES: Logika jest poprawna. Jeśli w przeglądarce jest 0, to błąd leży w przesyłaniu danych.")
    else:
        print("\nBŁĄD: Logika w rdzeniu tłumi sygnał do zera!")

if __name__ == "__main__":
    trace_tv_logic()
