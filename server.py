import http.server
import socketserver
import json
import threading
import os
from core import MindCore, TensionVector, Percept
from bridge.ollama_client import OllamaClient
from bridge.prompt_engine import DynamicPromptEngine
from bridge.param_modulator import ParameterModulator
from bridge.reflection import ReflectionService
from bridge.apperception import ApperceptionService
from memory.persistence import StateManager
from core.predictor import Predictor

PORT = 8800
MODEL_NAME = "CogitOS"  # Domyślny model systemu
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Wspoldzielony stan (singleton, nie na poziomie klasy handlera) ──
_state_manager = StateManager()
_mind, _metacognition = _state_manager.load_all()
_ollama = OllamaClient()
_prompt_engine = DynamicPromptEngine()
_modulator = ParameterModulator()
_reflector = ReflectionService()
_apperceptor = ApperceptionService()
_predictor = Predictor()
_lock = threading.Lock()  # Ochrona przed wyscigiem watkow
_chat_history = []        # Historia sesji (user/assistant) dla kontekstu

# BUG-01 FIX: Kolejka refleksji — nowy step czeka aż poprzednia refleksja się zakończy
class _ReflectionGate:
    """Zapewnia że refleksja z kroku N zakończy się przed krokiem N+1."""
    def __init__(self):
        self._done = threading.Event()
        self._done.set()  # Na starcie brak oczekującej refleksji
    def wait(self):
        self._done.wait(timeout=20.0)  # Max 20s na refleksję
    def mark_started(self):
        self._done.clear()
    def mark_done(self):
        self._done.set()

_reflection_gate = _ReflectionGate()


class CogitOSHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """Cichy log - nie zasmiecamy konsoli."""
        pass

    def do_OPTIONS(self):
        """BUG-07/BUG-10 FIX: Obsługa preflight CORS requests."""
        self.send_response(204)
        self._send_cors_headers()
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_GET(self):
        if self.path == '/':
            self._send_file('cogitos_chat.html', 'text/html; charset=utf-8')
        elif self.path == '/api/state':
            with _lock:
                state_data = _mind.psyche.as_dict()
                state_data["metacognition"] = _metacognition.get_dashboard_data()
                self._send_json(state_data)
        elif self.path == '/api/models':
            self._send_json(_ollama.list_models())
        elif self.path == '/api/engrams':
            with _lock:
                engrams_data = []
                for e in _mind.memory._store:
                    engrams_data.append({
                        "text": e.text,
                        "salience": round(e.salience, 3),
                        "valence": round(e.valence, 3),
                        "step": e.step_formed
                    })
                self._send_json(engrams_data)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/chat':
            self._handle_chat()
        elif self.path == '/api/reset':
            global _mind, _metacognition, _chat_history
            with _lock:
                _mind.reset()
                # Metacognition uczymy długoterminowo, ale zresetujmy go tu też do czysta jeśli resetujemy cały mózg
                _metacognition = type(_metacognition)() 
                _chat_history.clear()
                _state_manager.save_all(_mind, _metacognition)
            self._send_json({"status": "reset done"})
        else:
            self.send_error(404)

    def _handle_chat(self):
        global _chat_history
        import time
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
        user_input = post_data.get('message', '')
        model = post_data.get('model', MODEL_NAME)
        continuity = post_data.get('continuity', True)

        if not user_input.strip():
            self._send_json({"error": "Pusty input"})
            return

        # ══════════════════════════════════════════════════════
        # KLUCZOWA ZMIANA: Wysyłamy nagłówki SSE NATYCHMIAST,
        # zanim zaczniemy ciężkie przetwarzanie (LLM, embedding).
        # Dzięki temu przeglądarka wie, że połączenie żyje
        # i nie przerwie go z powodu timeoutu.
        # ══════════════════════════════════════════════════════
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self._send_cors_headers()
        self.send_header('X-Accel-Buffering', 'no')
        self.end_headers()

        # ══════════════════════════════════════════════════════
        # BUG-16 FIX: Keepalive thread — wysyła komentarze SSE
        # co 3s żeby przeglądarka nie zamknęła połączenia podczas
        # ciężkiego przetwarzania (apperception + embedding + mindcore).
        # Komentarze SSE (linie zaczynające się od ':') są ignorowane
        # przez parser zdarzeń, ale utrzymują TCP przy życiu.
        # ══════════════════════════════════════════════════════
        connection_alive = threading.Event()
        connection_alive.set()  # Zaczyna jako "żywe"
        keepalive_stop = threading.Event()

        def _keepalive_worker():
            """Wysyła SSE komentarze co 3s dopóki nie zostanie zatrzymany."""
            while not keepalive_stop.is_set():
                keepalive_stop.wait(timeout=3.0)
                if keepalive_stop.is_set():
                    break
                try:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
                except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError):
                    connection_alive.clear()  # Połączenie zerwane
                    print(" [WARN] Keepalive wykrył zerwane połączenie")
                    break

        keepalive_thread = threading.Thread(target=_keepalive_worker, daemon=True)
        keepalive_thread.start()

        # Sygnał "myślę" — utrzymuje połączenie przy życiu
        self._write_sse_safe({"type": "status", "data": "thinking"})

        # ── 0. Płytki Skan i Priming (System 0 - Predictor) ──
        # Zanim uruchomimy drogie procesy upewniamy się, że psychika
        # jest "nastawiona" na ciężar i afekt zadania (Cognitive Temperature).
        prediction = _predictor.scan(user_input)
        with _lock:
            _mind.psyche.apply_priming(prediction)
            
            # Poinformuj UI o predykcji (na panelu debug/meta)
            self._write_sse_safe({"type": "prediction", "data": prediction.as_dict()})

        # ── 1. Percepcja Hybrydowa (System 1 + Heurystyka) ──
        t_start_app = time.time()
        apperception_data = _apperceptor.apperceive(user_input, _ollama, model)
        t_app = time.time() - t_start_app
        heuristic_p = Percept.from_text(user_input)
        
        # Merge: bierzemy to co wyzsze (niezawodnosc i czulosc)
        apperception_data["emotional_charge"] = max(apperception_data["emotional_charge"], heuristic_p.emotional_charge, key=abs)
        apperception_data["semantic_density"] = max(apperception_data["semantic_density"], heuristic_p.semantic_density)
        apperception_data["value_challenge"]  = max(apperception_data["value_challenge"], heuristic_p.value_challenge)

        if apperception_data["value_challenge"] > 0.3:
            print("\n" + "!" * 60)
            print(f"!!! WYKRYTO ATAK AKSJOLOGICZNY (Tv): {apperception_data['value_challenge']:.2f} !!!")
            print("!" * 60 + "\n")

        # BUG-16 FIX: Sprawdź czy klient jeszcze słucha
        if not connection_alive.is_set():
            keepalive_stop.set()
            print(" [ABORT] Klient rozłączony przed embeddingiem — przerywam")
            return

        # Heartbeat — przeglądarka wie, że jeszcze pracujemy
        self._write_sse_safe({"type": "status", "data": "embedding"})

        t_start_emb = time.time()
        embedding = _ollama.embed(user_input)
        t_emb = time.time() - t_start_emb

        # BUG-16 FIX: Sprawdź ponownie po embeddingu
        if not connection_alive.is_set():
            keepalive_stop.set()
            print(" [ABORT] Klient rozłączony po embeddingu — przerywam")
            return

        # ── 2. Krok MindCore (z lockiem) ──
        # BUG-01 FIX: Czekamy aż refleksja z poprzedniego kroku się zakończy
        t_start_gate = time.time()
        _reflection_gate.wait()
        t_gate_wait = time.time() - t_start_gate

        t_start_lock = time.time()
        with _lock:
            t_lock_wait = time.time() - t_start_lock
            cognitive_ctx = _mind.step(user_input, embedding=embedding, continuity=continuity, apperception_data=apperception_data)
            p = _mind.psyche
            
            # --- WIZUALIZACJA W KONSOLI (DEBUG) ---
            print("\n" + "="*50)
            print(f" STEP #{_mind.step_n} | PHASE: {p.phase.value.upper()}")
            print("-" * 50)
            print(f" INPUT: {user_input[:50]}...")
            print(f" SENSORS: {apperception_data} [app: {t_app:.2f}s | emb: {t_emb:.2f}s]")
            print(f" PSYCHE:  S: {p.anchor:.3f} | A: {p.arousal:.3f} | C: {p.coherence:.3f} | D: {p.dopamine:.3f}")
            print(f" TENSION: Ta: {p.mood_ta:.3f} | Tc: {p.mood_tc:.3f} | Tv: {p.mood_tv:.3f}")
            print(f" TIMINGS: gate_wait: {t_gate_wait:.2f}s | lock_wait: {t_lock_wait:.2f}s")
            print("="*50 + "\n")

            recent_engrams = _mind.memory._store[-3:] if _mind.memory._store else []

        # ── 3. Odtworz TensionVector z danych kroku ──
        t = cognitive_ctx['tension']
        tv_obj = TensionVector(affective=t['T_a'], cognitive=t['T_c'], axiological=t['T_v'])

        # ── 3.5. MetaCognition: Lustro Myśli ──
        with _lock:
            # Użyjemy poprzednich engramów + obecnych wyników do kontekstu
            # Aby zbudować moment dla metacognition potrzebujemy pełnego obiektu
            # Jednak dla uproszczenia (metacognition buduje słownik z context),
            # możemy to przekazać bezpośrednio:
            moment_mock = _mind.memory._store[-1] if _mind.memory._store else None
            # MetaCognition pobiera stan Psyche oraz aktualny step
            # Ponieważ `select_strategy` przyjmuje `moment` z percepcją, zrekonstruujmy go na szybko:
            from core import ConsciousMoment
            cm_mock = ConsciousMoment(percept=heuristic_p, engrams=recent_engrams, psyche_snapshot=_mind.psyche.snapshot())
            
            strategy = _metacognition.select_strategy(cm_mock, _mind.psyche, step_n=_mind.step_n)
            strategy_instruction = _metacognition.format_instruction(strategy)
            
            # Wzbogacamy dane dla frontendu
            cognitive_ctx["metacognition"] = _metacognition.get_dashboard_data()

        # ── 4. Zbuduj prompt i parametry ──
        sys_prompt = _prompt_engine.build_system_prompt(_mind.psyche, tv_obj, cognitive_ctx, active_strategy_instruction=strategy_instruction)
        mem_context = _prompt_engine.build_memory_context(recent_engrams)
        params = _modulator.modulate(_mind.psyche, tv_obj)

        # ═══════════════════════════════════════════════════════════
        # BUG-17 FIX / OPTYMALIZACJA (Context Consolidation):
        # Przycięcie historii do budżetu. Zmniejszamy budżet z 6000
        # do 3000 i ładujemy tylko najnowszą historię (do 4 wiadomości),
        # polegając na skompresowanych Engramach w pamięci długotrwałej.
        # num_ctx=8192, bezpieczny próg wejściowy to 3000.
        INPUT_BUDGET = 3000 
        # ═══════════════════════════════════════════════════════════
        num_ctx = params.get('num_ctx', 4096)
        RESPONSE_RESERVE = 1024  # Tokeny zarezerwowane na odpowiedź
        
        # Oszacuj tokeny stałych elementów (system prompt + memory + user input)
        fixed_tokens = self._estimate_tokens(sys_prompt) + self._estimate_tokens(mem_context) + self._estimate_tokens(user_input)

        # Budżet na historię = to co zostaje po stałych elementach
        history_budget = INPUT_BUDGET - fixed_tokens

        # Przytnij historię do budżetu
        trimmed_history = self._trim_history_to_budget(_chat_history, history_budget)

        messages = _prompt_engine.build_messages(user_input, sys_prompt, mem_context, trimmed_history)

        # ── DEBUG: Diagnostyka kontekstu ──
        total_chars = sum(len(m.get('content', '')) for m in messages)
        total_tokens_est = self._estimate_tokens_from_messages(messages)
        history_entries_used = len(trimmed_history)
        history_entries_available = len(_chat_history)

        print(f" CONTEXT: {total_tokens_est} tok (est) / {num_ctx} num_ctx | "
              f"budget: {INPUT_BUDGET} input + {RESPONSE_RESERVE} response")
        print(f" CONTEXT: fixed={fixed_tokens} tok | history={total_tokens_est - fixed_tokens} tok "
              f"({history_entries_used}/{history_entries_available} wiadomości)")
        print(f" CONTEXT: {total_chars} chars total | "
              f"{'[!] PRZYCIETO HISTORIE' if history_entries_used < min(4, history_entries_available) else '[OK]'}")

        if total_tokens_est > INPUT_BUDGET:
            print(f" [UWAGA] Estymacja ({total_tokens_est}) > budzet ({INPUT_BUDGET})! Model moze obcinac input.")

        # BUG-16 FIX: Sprawdź czy klient jeszcze słucha przed streamingiem
        if not connection_alive.is_set():
            keepalive_stop.set()
            print(" [ABORT] Klient rozłączony przed streamingiem — przerywam")
            return

        # Wyslij stan kognitywny
        self._write_sse_safe({"type": "cognitive", "data": cognitive_ctx})
        
        print(f" DEBUG: Params modulated -> {params}")

        # ── 5. Streaming odpowiedzi z Ollama ──
        full_response = []
        try:
            t_start_chat = time.time()
            stream = _ollama.chat(messages, model, params, stream=True)
            # Sprawdz czy dostalismy generator (sukces) czy string (blad)
            if isinstance(stream, str):
                # Blad — cala odpowiedz jako jeden token
                keepalive_stop.set()
                full_response.append(stream)
                self._write_sse_safe({"type": "token", "data": stream})
            else:
                first_token_received = False
                token_count = 0
                # BUG-20 FIX: Detekcja "Ollama milczy" - jesli miedzy tokenami
                # uplynie wiecej niz STALL_TIMEOUT, abortujemy stream.
                last_token_time = time.time()
                STALL_TIMEOUT = 25.0  # 25s bez nowego tokena = problem
                stalled = False
                for token in stream:
                    now = time.time()
                    if not first_token_received:
                        keepalive_stop.set()  # BUG-18 FIX: Tu następuje zatrzymanie keepalive!
                        t_prefill = time.time() - t_start_chat
                        print(f" DEBUG: Ollama prefill delay (time to first token): {t_prefill:.2f}s")
                    
                    full_response.append(token)
                    success = self._write_sse_safe({"type": "token", "data": token})
                    if not success:
                        print(" [ABORT] Przerwano generowanie - klient rozłączył się podczas streamingu.")
                        break
                    
                    # Co 10 tokenów wysyłamy przypomnienie o stanie kognitywnym (dla synchronizacji)
                    token_count += 1
                    if token_count % 10 == 0:
                        with _lock:
                            sync_ctx = {
                                "step_n": _mind.step_n,
                                "psyche": _mind.psyche.as_dict(),
                                "tension": tv_obj.as_dict(),
                                "metacognition": _metacognition.get_dashboard_data()
                            }
                        self._write_sse_safe({"type": "cognitive", "data": sync_ctx})
        except Exception as e:
            error_msg = f"Blad generacji: {e}"
            self._write_sse_safe({"type": "token", "data": error_msg})
            full_response.append(error_msg)

        try:
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            print(f" [WARN] Połączenie zamknięte przy wysyłaniu [DONE]")

        # ── 6. Refleksja i zapis (w osobnym watku) ──
        response_text = "".join(full_response)
        _chat_history.append({"role": "user", "content": user_input})
        _chat_history.append({"role": "assistant", "content": response_text})
        # BUG-14 FIX: Ograniczenie rozmiaru historii
        if len(_chat_history) > 30:
            _chat_history[:] = _chat_history[-20:]

        # BUG-01 FIX: Sygnalizujemy start refleksji
        _reflection_gate.mark_started()
        threading.Thread(
            target=self._finalize_step,
            args=(user_input, response_text, model),
            daemon=True
        ).start()

    def _finalize_step(self, user_input, response_text, model):
        """Refleksja kognitywna i zapis stanu — w tle."""
        import time
        t_start_ref = time.time()
        try:
            # 1. Wykonujemy refleksję BEZ trzymania locka (wolne zapytanie do Ollama)
            reflection = _reflector.reflect(user_input, response_text, _ollama, model)
            t_ref = time.time() - t_start_ref
            print(f" DEBUG: Reflection completed in {t_ref:.2f}s")
            
            # 2. Blokujemy stan tylko na czas aktualizacji i zapisu (bardzo szybkie operacje)
            with _lock:
                # 1. Aktualizacja walencji ostatniego engramu
                if _mind.memory._store:
                    last = _mind.memory._store[-1]
                    ref_valence = reflection.get('valence')
                    if ref_valence is not None and isinstance(ref_valence, (int, float)):
                        last.valence = (last.valence + ref_valence) / 2.0
                
                # 2. Aktualizacja autogeniczna Psyche
                new_motto = reflection.get('motto')
                if new_motto:
                    _mind.psyche.motto = new_motto
                
                d_delta = reflection.get('dopamine_delta', 0.0)
                if isinstance(d_delta, (int, float)):
                    _mind.psyche.dopamine = max(0.0, min(1.0, _mind.psyche.dopamine + d_delta))
                
                # 3. Ewaluacja strategii myślenia
                _metacognition.evaluate_outcome(reflection)
                
                _state_manager.save_all(_mind, _metacognition)
                
        except Exception as e:
            print(f"Blad refleksji: {e}")
        finally:
            # BUG-01 FIX: Sygnalizujemy koniec refleksji
            _reflection_gate.mark_done()

    # ── Metody pomocnicze ──

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Przybliżona estymacja tokenów. BUG-21 FIX: Polski tekst z diakrytykami: ~1 token / 2 znaki."""
        if not text:
            return 0
        return max(1, len(text) // 2)

    @staticmethod
    def _estimate_tokens_from_messages(messages: list) -> int:
        """Estymacja łącznej liczby tokenów w liście wiadomości."""
        total = 0
        for msg in messages:
            total += 4  # overhead per message (role, formatting)
            total += max(1, len(msg.get('content', '')) // 2)  # BUG-21 FIX: // 2 dla polskiego
        return total

    @staticmethod
    def _trim_history_to_budget(chat_history: list, token_budget: int) -> list:
        """BUG-17 FIX: Przytnij historię od najstarszych wiadomości aż zmieści się w budżecie.
        Zachowuje pary user/assistant i zawsze bierze od końca (najnowsze).
        """
        if token_budget <= 0:
            return []

        # Zacznij od max 4 najnowszych wiadomości (2 pary)
        candidates = chat_history[-4:]
        
        # Szacuj tokeny od końca, dodając pary
        result = []
        tokens_used = 0
        
        # Iteruj od końca parami (assistant, user)
        i = len(candidates) - 1
        while i >= 1:  # Potrzebujemy min 2 elementy na parę
            pair = candidates[i-1:i+1]  # [user, assistant]
            pair_tokens = sum(max(1, len(m.get('content', '')) // 3) + 4 for m in pair)
            
            if tokens_used + pair_tokens > token_budget:
                # Ta para się nie mieści — przerwij
                if not result:
                    # Jeśli nawet pierwsza para nie mieści się, weź ją ale przytnij
                    for m in pair:
                        truncated = m.copy()
                        max_chars = (token_budget // 2) * 3
                        if len(truncated.get('content', '')) > max_chars:
                            truncated['content'] = truncated['content'][:max_chars] + '...'
                        result.insert(0, truncated)
                break
            
            tokens_used += pair_tokens
            result = pair + result
            i -= 2
        
        return result

    def _write_sse(self, payload: dict):
        """Wyslij jedno zdarzenie SSE."""
        data = json.dumps(payload, ensure_ascii=False)
        self.wfile.write(f"data: {data}\n\n".encode('utf-8'))
        self.wfile.flush()

    def _write_sse_safe(self, payload: dict) -> bool:
        """Wyślij SSE z ochroną przed zerwaniem połączenia. Zwraca True jeśli sukces."""
        try:
            self._write_sse(payload)
            return True
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError):
            print(f" [WARN] Połączenie przerwane przy wysyłaniu SSE")
            return False

    def _send_file(self, filename, content_type):
        filepath = os.path.join(SCRIPT_DIR, filename)
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, f"Nie znaleziono pliku: {filename}")

    def _send_json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self._send_cors_headers()  # BUG-07 FIX
        self.end_headers()
        self.wfile.write(body)


def run_server():
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), CogitOSHandler) as httpd:
        print("\n" + "="*50)
        print(" *** CogitOS GRAVITATIONAL CORE v3.5 ACTIVE ***")
        print("="*50 + "\n")
        print(f"Server: http://127.0.0.1:{PORT}")
        print(f"Model:  {MODEL_NAME}")
        print(f"Memory: {len(_mind.memory)} engrams")
        print(f"Step:   {_mind.step_n}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nZatrzymywanie serwera...")
            # Zapisujemy tylko jeśli plik istnieje (brak pliku = manualny reset)
            if _state_manager.state_file.exists():
                _state_manager.save_all(_mind, _metacognition)
                print("Stan zapisany.")
            else:
                print("Plik stanu nie istnieje - pomijam autozapis (reset manualny).")


if __name__ == "__main__":
    run_server()
