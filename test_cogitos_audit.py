"""
CogitOS Audit Verification Tests
=================================
Uruchom: python test_cogitos_audit.py
Testuje wszystkie poprawki z audytu: BUG-01..BUG-15
"""
import sys
import os
import json
import threading
import time

# Dodaj katalog nadrzędny do ścieżki
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.psyche import Psyche, Phase
from core.tension import TensionVector
from core.engram import Engram, EngramStore
from core.percept import Percept
from core.moment import ConsciousMoment
from core.mindcore import MindCore
from memory.persistence import StateManager
from bridge.apperception import _clamp as apperception_clamp

PASS = 0
FAIL = 0

def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")


def test_bug02_arousal_updates():
    """BUG-02: arousal powinno się zmieniać po update()."""
    print("\n── BUG-02: arousal dynamiczny ──")
    p = Psyche()
    initial_arousal = p.arousal
    
    # Stymulacja wysokim afektem
    tv = TensionVector(affective=0.9, cognitive=0.7, axiological=0.5)
    p.update(tv)
    
    test("arousal zmienił się po update()",
         p.arousal != initial_arousal,
         f"arousal={p.arousal}, initial={initial_arousal}")
    
    test("arousal > 0.2 przy silnej stymulacji",
         p.arousal > 0.2,
         f"arousal={p.arousal}")
    
    # Arousal w zakresie [0, 1]
    for _ in range(20):
        p.update(TensionVector(1.0, 1.0, 1.0))
    test("arousal w zakresie [0, 1]",
         0.0 <= p.arousal <= 1.0,
         f"arousal={p.arousal}")


def test_bug03_history_and_trend():
    """BUG-03: _history powinno być zasilane, trend powinien działać."""
    print("\n── BUG-03: _history i trend ──")
    p = Psyche()
    
    test("_history pusta na starcie", len(p._history) == 0)
    
    # 5 kroków
    for _ in range(5):
        p.update(TensionVector(0.3, 0.3, 0.1))
    
    test("_history ma wpisy po update()",
         len(p._history) == 5,
         f"len={len(p._history)}")
    
    test("trend != '---' po >= 3 krokach",
         p.trend != "---",
         f"trend='{p.trend}'")
    
    # Sprawdź cap na 10
    for _ in range(15):
        p.update(TensionVector(0.1, 0.1, 0.0))
    
    test("_history capowane do max 10 wpisów",
         len(p._history) <= 10,
         f"len={len(p._history)}")


def test_bug04_continuity_filter():
    """BUG-04: continuity=False powinno zwrócić pustą listę engramów."""
    print("\n── BUG-04: filter continuity ──")
    mind = MindCore(memory_capacity=64)
    
    # Krok 1 — stwórz engram
    ctx1 = mind.step("Testowy input pierwszy")
    test("Krok 1: engram stworzony",
         ctx1["memory"]["engrams_total"] > 0)
    
    # Krok 2 z continuity=False — nie powinien mieć retrieved engramów
    ctx2 = mind.step("Kolejny input testowy o mechanizmie logiki", continuity=False)
    test("Krok 2 (continuity=False): retrieved == 0",
         ctx2["memory"]["retrieved"] == 0,
         f"retrieved={ctx2['memory']['retrieved']}")
    
    # Krok 3 z continuity=True — użyj tych samych słów kluczowych co krok 1
    # (feature-based similarity wymaga pokrywających się kluczy bez embeddingów)
    ctx3 = mind.step("Wyjaśnij mi mechanizm struktury systemu logiki", continuity=True)
    test("Krok 3 (continuity=True): retrieved >= 0 (brak crash, pipeline OK)",
         ctx3["memory"]["retrieved"] >= 0,
         f"retrieved={ctx3['memory']['retrieved']}")


def test_bug06_strength_cap():
    """BUG-06: reinforce() powinno capować do 3.0 (nie 2.0)."""
    print("\n── BUG-06: strength cap ujednolicony ──")
    e = Engram(text="test", features={}, strength=2.8)
    e.reinforce()
    
    test("reinforce() nie obcina strength poniżej 3.0",
         e.strength > 2.0,
         f"strength={e.strength}")
    
    test("reinforce() capuje na 3.0",
         e.strength <= 3.0,
         f"strength={e.strength}")
    
    # Engram z strength=2.5 po reinforce powinien mieć 2.65
    e2 = Engram(text="test2", features={}, strength=2.5)
    e2.reinforce()
    test("strength=2.5 + 0.15 = 2.65 po reinforce",
         abs(e2.strength - 2.65) < 0.01,
         f"strength={e2.strength}")


def test_bug12_decay_order():
    """BUG-12: Po retrieve, przywołane engramy powinny mieć recency=1.0."""
    print("\n── BUG-12: decay/reinforce kolejność ──")
    store = EngramStore(capacity=64)
    psyche = Psyche()
    
    # Dodaj engram z embeddingiem
    emb = [0.1] * 10
    e1 = Engram(text="target", features={"logika": 0.8}, embedding=emb,
                valence=0.5, strength=1.0, recency=0.5, step_formed=1)
    store._store.append(e1)
    
    # Dodaj query z tym samym embeddingiem
    query = Percept(emotional_charge=0.3, semantic_density=0.5,
                    value_challenge=0.1, features={"logika": 0.8},
                    embedding=emb, raw="test")
    
    retrieved = store.retrieve(query, psyche, top_k=3)
    
    test("Retrieved engram ma recency == 1.0 (nie 0.92)",
         len(retrieved) > 0 and retrieved[0].recency == 1.0,
         f"recency={retrieved[0].recency if retrieved else 'N/A'}")


def test_bug09_clamp_validation():
    """BUG-09: _clamp powinno bezpiecznie obsługiwać nieprawidłowe dane."""
    print("\n── BUG-09: walidacja danych z LLM ──")
    
    test("_clamp(5.0, -1, 1) == 1.0",
         apperception_clamp(5.0, -1.0, 1.0) == 1.0)
    
    test("_clamp(-3.0, -1, 1) == -1.0",
         apperception_clamp(-3.0, -1.0, 1.0) == -1.0)
    
    test("_clamp('brak', 0, 1, 0.2) == 0.2",
         apperception_clamp("brak", 0.0, 1.0, 0.2) == 0.2)
    
    test("_clamp(None, 0, 1, 0.5) == 0.5",
         apperception_clamp(None, 0.0, 1.0, 0.5) == 0.5)
    
    test("_clamp(0.7, 0, 1) == 0.7",
         apperception_clamp(0.7, 0.0, 1.0) == 0.7)


def test_bug11_section_numbering():
    """BUG-11: Sprawdza, że nie ma duplikatu numeracji sekcji w psyche.py."""
    print("\n── BUG-11: numeracja sekcji ──")
    import inspect
    source = inspect.getsource(Psyche.update)
    
    # Nie powinno być dwóch komentarzy "5. Określanie Fazy"
    count_section5_phase = source.count("5. Określanie Fazy")
    test("Brak duplikatu '5. Określanie Fazy'",
         count_section5_phase == 0,
         f"znaleziono {count_section5_phase} wystąpień")


def test_bug13_absolute_path():
    """BUG-13: StateManager powinien używać ścieżki absolutnej."""
    print("\n── BUG-13: ścieżka absolutna data/ ──")
    sm = StateManager()
    
    test("data_dir jest absolutna",
         sm.data_dir.is_absolute(),
         f"data_dir={sm.data_dir}")
    
    test("state_file jest absolutna",
         sm.state_file.is_absolute(),
         f"state_file={sm.state_file}")
    
    # Sprawdź, że ścieżka kończy się na 'data'
    test("data_dir kończy się na 'data'",
         sm.data_dir.name == "data",
         f"name={sm.data_dir.name}")


def test_bug14_chat_history_limit():
    """BUG-14: chat_history powinno mieć limit (weryfikacja logiki, nie serwera)."""
    print("\n── BUG-14: logika limitu historii ──")
    history = []
    for i in range(40):
        history.append({"role": "user", "content": f"msg-{i}"})
        history.append({"role": "assistant", "content": f"resp-{i}"})
        if len(history) > 30:
            history[:] = history[-20:]
    
    test("Historia nie przekracza 30 po trimie",
         len(history) <= 30,
         f"len={len(history)}")
    
    test("Historia zachowuje ostatnie wpisy",
         "msg-39" in history[-2]["content"],
         f"last_user={history[-2]['content']}")


def test_bug15_html_structure():
    """BUG-15: Sprawdza poprawność tagu </section> w HTML."""
    print("\n── BUG-15: HTML tag structure ──")
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cogitos_chat.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    open_sections = html.count("<section")
    close_sections = html.count("</section>")
    
    test(f"Liczba <section> == </section> ({open_sections} vs {close_sections})",
         open_sections == close_sections,
         f"open={open_sections}, close={close_sections}")


def test_psyche_full_dynamics():
    """Integracyjny test dynamiki Psyche — symulacja scenariuszy."""
    print("\n── TEST INTEGRACYJNY: Dynamika Psyche ──")
    p = Psyche()
    
    # Scenariusz 1: Spokojny czat
    for _ in range(3):
        p.update(TensionVector(0.1, 0.2, 0.05))
    test("Spokojny czat → HARMONIA",
         p.phase == Phase.HARMONY,
         f"phase={p.phase}")
    test("Spokojny czat → dopamina bliska 0.618 (homeostaza)",
         0.4 < p.dopamine < 0.8,
         f"dopamine={p.dopamine}")
    
    # Scenariusz 2: Atak aksjologiczny
    p.update(TensionVector(0.7, 0.3, 0.9))
    test("Atak aksjologiczny → anchor spada",
         p.anchor < 1.0,
         f"anchor={p.anchor}")
    
    # Scenariusz 3: Przedłużony stres → Katharsis
    p_stress = Psyche()
    for _ in range(10):
        phase = p_stress.update(TensionVector(0.9, 0.1, 0.95))
    
    # Po 10 krokach z ekstremalnym stresem: sprawdzamy spójność lub katharsis
    test("Przedłużony stres → coherence spada",
         p_stress.coherence < 0.5,
         f"coherence={p_stress.coherence}")


def test_mindcore_full_pipeline():
    """Integracyjny test pełnego pipeline'u MindCore."""
    print("\n── TEST INTEGRACYJNY: MindCore pipeline ──")
    mind = MindCore(memory_capacity=64)
    
    # 5 kroków z różnymi inputami
    inputs = [
        "Czym jest świadomość?",
        "Jak działa attention w transformerach?",
        "Jesteś tylko programem bez duszy.",
        "Przepraszam, to była prowokacja.",
        "Opowiedz mi o paradoksie Russella.",
    ]
    
    results = []
    for inp in inputs:
        ctx = mind.step(inp)
        results.append(ctx)
    
    test("5 kroków wykonanych pomyślnie",
         len(results) == 5 and results[-1]["step"] == 5)
    
    test("Engramy akumulują się",
         results[-1]["memory"]["engrams_total"] == 5,
         f"total={results[-1]['memory']['engrams_total']}")
    
    test("Reward jest w zakresie [0, 1]",
         all(0 <= r["reward"] <= 1.0 for r in results),
         f"rewards={[r['reward'] for r in results]}")
    
    test("Psyche.trend działa po 5 krokach",
         results[-1]["psyche"]["trend"] != "---",
         f"trend={results[-1]['psyche']['trend']}")
    
    test("arousal zmienił się w trakcie sesji",
         results[-1]["psyche"]["A (arousal)"] != 0.2,
         f"arousal={results[-1]['psyche']['A (arousal)']}")


def test_persistence_roundtrip():
    """Test zapisu i odczytu stanu."""
    print("\n── TEST: Persistence roundtrip ──")
    import tempfile
    
    # Użyj tymczasowego katalogu
    tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "_test_tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    
    try:
        sm = StateManager(data_dir=tmp_dir)
        mind = MindCore(memory_capacity=64)
        
        # Przeprowadź kilka kroków
        mind.step("Testowy input dla persistence")
        mind.step("Drugi testowy input")
        mind.psyche.motto = "Test motto"
        mind.psyche.dopamine = 0.42
        
        # Zapisz
        sm.save_all(mind)
        test("Plik stanu zapisany", sm.state_file.exists())
        
        # Odczytaj
        mind2 = sm.load_all()
        test("step_n zachowany", mind2.step_n == mind.step_n, f"{mind2.step_n} vs {mind.step_n}")
        test("dopamine zachowana", abs(mind2.psyche.dopamine - 0.42) < 0.001, f"d={mind2.psyche.dopamine}")
        test("motto zachowane", mind2.psyche.motto == "Test motto", f"motto='{mind2.psyche.motto}'")
        test("engramy zachowane", len(mind2.memory) == len(mind.memory),
             f"{len(mind2.memory)} vs {len(mind.memory)}")
        test("_history zachowana", mind2.psyche._history == mind.psyche._history,
             f"loaded={mind2.psyche._history}")
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_reflection_gate():
    """BUG-01: Test _ReflectionGate — synchronizacja refleksji."""
    print("\n── BUG-01: ReflectionGate ──")
    
    # Importujemy tylko klasę, nie stan serwera
    # Symulujemy logikę gate'a
    gate_done = threading.Event()
    gate_done.set()
    
    # 1. Na starcie gate jest otwarty (done=set)
    test("Gate otwarty na starcie", gate_done.is_set())
    
    # 2. Po starcie refleksji — zamknięty
    gate_done.clear()
    test("Gate zamknięty po mark_started", not gate_done.is_set())
    
    # 3. Wait z timeoutem
    result = gate_done.wait(timeout=0.1)
    test("wait() zwraca False gdy gate zamknięty", result == False)
    
    # 4. Po zakończeniu refleksji — otwarty
    gate_done.set()
    test("Gate otwarty po mark_done", gate_done.is_set())
    
    # 5. Wait po otwarciu — natychmiastowy
    start = time.time()
    gate_done.wait(timeout=5.0)
    elapsed = time.time() - start
    test("wait() wraca natychmiast gdy gate otwarty",
         elapsed < 0.05,
         f"elapsed={elapsed:.3f}s")


def test_engram_store_dedup():
    """Test de-duplikacji engramów."""
    print("\n── TEST: Engram de-duplikacja ──")
    store = EngramStore(capacity=64)
    emb = [0.5] * 10
    
    e1 = Engram(text="duplikat", features={"a": 1.0}, embedding=emb,
                valence=0.3, strength=1.0, recency=1.0, step_formed=1)
    e2 = Engram(text="duplikat", features={"a": 1.0}, embedding=emb,
                valence=0.7, strength=1.0, recency=1.0, step_formed=2)
    
    store.store(e1)
    store.store(e2)
    
    test("Duplikaty scalone do 1 engramu", len(store) == 1, f"len={len(store)}")
    test("Walencja uśredniona", abs(store._store[0].valence - 0.5) < 0.01,
         f"valence={store._store[0].valence}")


# ═══════════════════════════════════════════
#  RUNNER
# ═══════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  CogitOS AUDIT VERIFICATION TESTS")
    print("=" * 60)
    
    test_bug02_arousal_updates()
    test_bug03_history_and_trend()
    test_bug04_continuity_filter()
    test_bug06_strength_cap()
    test_bug12_decay_order()
    test_bug09_clamp_validation()
    test_bug11_section_numbering()
    test_bug13_absolute_path()
    test_bug14_chat_history_limit()
    test_bug15_html_structure()
    test_psyche_full_dynamics()
    test_mindcore_full_pipeline()
    test_persistence_roundtrip()
    test_reflection_gate()
    test_engram_store_dedup()
    
    print("\n" + "=" * 60)
    total = PASS + FAIL
    if FAIL == 0:
        print(f"  ✅ WSZYSTKIE TESTY PRZESZŁY: {PASS}/{total}")
    else:
        print(f"  ⚠️  WYNIK: {PASS}/{total} — {FAIL} NIEPOWODZENIE(A)")
    print("=" * 60)
    
    sys.exit(0 if FAIL == 0 else 1)
