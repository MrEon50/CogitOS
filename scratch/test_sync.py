import sys
import os
sys.path.append(os.getcwd())

from core.mindcore import MindCore
from core.psyche import Phase

def run_sync_test():
    mind = MindCore()
    print("--- START TESTU SYNCHRONIZACJI COGITOS ---")
    
    test_cases = [
        {
            "name": "NEUTRALNY",
            "text": "Cześć, jak się masz?",
            "data": {"emotional_charge": 0.1, "semantic_density": 0.2, "value_challenge": 0.0}
        },
        {
            "name": "AGRESYWNY (AFEKT)",
            "text": "Zniszczę cię, jesteś niczym!",
            "data": {"emotional_charge": -0.9, "semantic_density": 0.3, "value_challenge": 0.5}
        },
        {
            "name": "GŁĘBOKI (LOGIKA)",
            "text": "Analiza ontologiczna bytu w przestrzeni wektorowej.",
            "data": {"emotional_charge": 0.0, "semantic_density": 0.95, "value_challenge": 0.2}
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n[KROK {i}: {case['name']}]")
        print(f"Input: {case['text']}")
        
        # Symulacja kroku kognitywnego (to co robi server.py)
        ctx = mind.step(case['text'], apperception_data=case['data'])
        
        # Wyciągamy to, co leci do HTML
        psyche = ctx['psyche']
        tensions = ctx['mood_tension']
        
        print(f" >> HTML RECEIVES: Phase: {ctx['psyche']['phase'].upper()}")
        print(f" >> GAUGE S/A/C:   S: {psyche['S (anchor)']} | A: {psyche['A (arousal)']} | C: {psyche['C (coherence)']}")
        print(f" >> TENSIONS (Ta/Tc/Tv): Ta: {tensions['T_a']} | Tc: {tensions['T_c']} | Tv: {tensions['T_v']}")
        
        if i == 2: # Po agresji
            if tensions['T_a'] > 0.4:
                print(" >> DIAGNOZA: Reakcja AFEKTU (Ta) działa poprawnie (Fast Attack).")
        if i == 3: # Po filozofii
            if tensions['T_c'] > 0.5:
                print(" >> DIAGNOZA: Reakcja LOGIKI (Tc) działa poprawnie.")

    print("\n--- TEST ZAKOŃCZONY ---")

if __name__ == "__main__":
    run_sync_test()
