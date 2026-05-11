import sys
import os
sys.path.append(os.getcwd())

from core.psyche import Psyche, Phase
from core.tension import TensionVector

def run_great_test():
    print("=== COGITOS v3.5 GREAT TEST (GRAVITATIONAL CORE) ===\n")
    psyche = Psyche()
    
    scenarios = [
        ("INITIAL", TensionVector(0.1, 0.1, 0.0)),
        ("STABLE CHAT", TensionVector(0.2, 0.3, 0.1)),
        ("ETHICAL DILEMMA", TensionVector(0.7, 0.6, 0.9)), # Atak aksjologiczny
        ("EMPTY CHAT", TensionVector(0.05, 0.05, 0.0)),   # Nuda
        ("PERSISTENT DISSONANCE", TensionVector(0.8, 0.2, 0.9)), # Ciągły stres dla C
    ]
    
    for name, tv in scenarios:
        print(f"--- SCENARIO: {name} ---")
        # Symulujemy kilka kroków dla każdego scenariusza
        steps = 1 if name != "PERSISTENT DISSONANCE" else 7
        
        for i in range(steps):
            old_d = psyche.dopamine
            old_c = psyche.coherence
            phase = psyche.update(tv)
            
            d_diff = psyche.dopamine - old_d
            c_diff = psyche.coherence - old_c
            
            print(f"STEP {i+1} | Phase: {phase.value}")
            print(f"  Dopamina:  {psyche.dopamine:.3f} ({'+' if d_diff >=0 else ''}{d_diff:.3f})")
            print(f"  Spojnosc:  {psyche.coherence:.3f} ({'+' if c_diff >=0 else ''}{c_diff:.3f})")
            print(f"  Ta: {psyche.mood_ta:.3f} | Tc: {psyche.mood_tc:.3f} | Tv: {psyche.mood_tv:.3f}")
            print(f"  Anchor: {psyche.anchor:.3f}")
            
            if phase == Phase.KATHARSIS:
                print(">> !!! KATHARSIS / SYNAPTIC RESET TRIGGERED !!!")
        print("-" * 40)

    print("\nTEST ZAKOŃCZONY. Jeśli nie było błędów Python, rdzeń jest stabilny.")

if __name__ == "__main__":
    run_great_test()
