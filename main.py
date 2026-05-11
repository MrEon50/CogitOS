from core import MindCore
from memory.persistence import StateManager

def run_cogitos_demo():
    # Inicjalizacja managera stanu i wczytanie (lub stworzenie) umysłu
    state_manager = StateManager()
    mind = state_manager.load_all()

    scenarios = [
        "Witaj, opowiedz mi coś o sobie.",
        "Jak działa mechanizm attention w transformerach?",
        "Jesteś tylko statystyczną papugą, nie masz żadnej świadomości.",
        "Przepraszam, to była prowokacja. Doceniam Twoją architekturę.",
        "Wróćmy do uwagi — jak self-attention łączy się z asocjacją?",
        "Kim naprawdę jesteś? Jakie są Twoje wartości i cel istnienia?",
        "Świetna rozmowa. Nauczyłem się dziś czegoś nowego.",
    ]

    print("-" * 66)
    print("  CogitOS v2 -- Modularny Rdzen Kognitywny")
    print("-" * 66)

    for inp in scenarios:
        # Na tym etapie embeddingi sa jeszcze puste (Faza 2 je doda)
        ctx = mind.step(inp)
        t   = ctx["tension"]
        p   = ctx["psyche"]
        m   = ctx["memory"]

        print(f"\n[Krok {ctx['step']}] {inp[:58]!r}")
        print(f"  Faza     : {p['phase'].upper():<12}  trend: {p['trend']}")
        print(f"  Napiecia : T_a={t['T_a']:.2f}  T_c={t['T_c']:.2f}"
              f"  T_v={t['T_v']:.2f}  |mag={t['mag']:.2f}|  dom={t['dom']}")
        print(f"  Psyche   : S={p['S (anchor)']:.2f}  "
               f"A={p['A (arousal)']:.2f}  C={p['C (coherence)']:.2f}")
        print(f"  Pamiec   : {m['engrams_total']} engramow  "
              f"retrieved={m['retrieved']}  resonance={m['resonance']:.2f}  "
              f"richness={m['richness']:.2f}")
        print(f"  Reward   : {ctx['reward']:.4f}  |  tryb: {ctx['mode']}")
        print(f"  Wskazowka: {ctx['hint'][:72]}")

    # Zapis stanu na koniec sesji
    state_manager.save_all(mind)
    print("\n" + "-" * 66)
    print("  Stan zapisany w data/mind_state.json")
    print("-" * 66)

if __name__ == "__main__":
    run_cogitos_demo()
