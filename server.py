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

PORT = 8800
MODEL_NAME = "CogitOS"  # Domyślny model systemu
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Wspoldzielony stan (singleton, nie na poziomie klasy handlera) ──
_state_manager = StateManager()
_mind = _state_manager.load_all()
_ollama = OllamaClient()
_prompt_engine = DynamicPromptEngine()
_modulator = ParameterModulator()
_reflector = ReflectionService()
_apperceptor = ApperceptionService()
_lock = threading.Lock()  # Ochrona przed wyscigiem watkow
_chat_history = []        # Historia sesji (user/assistant) dla kontekstu


class CogitOSHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """Cichy log - nie zasmiecamy konsoli."""
        pass

    def do_GET(self):
        if self.path == '/':
            self._send_file('cogitos_chat.html', 'text/html; charset=utf-8')
        elif self.path == '/api/state':
            with _lock:
                self._send_json(_mind.psyche.as_dict())
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
            global _mind, _chat_history
            with _lock:
                _mind.reset()
                _chat_history.clear()
                _state_manager.save_all(_mind)
            self._send_json({"status": "reset done"})
        else:
            self.send_error(404)

    def _handle_chat(self):
        global _chat_history
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
        user_input = post_data.get('message', '')
        model = post_data.get('model', MODEL_NAME)
        continuity = post_data.get('continuity', True)

        if not user_input.strip():
            self._send_json({"error": "Pusty input"})
            return

        # ── 1. Percepcja Hybrydowa (System 1 + Heurystyka) ──
        apperception_data = _apperceptor.apperceive(user_input, _ollama, model)
        heuristic_p = Percept.from_text(user_input)
        
        # Merge: bierzemy to co wyzsze (niezawodnosc i czulosc)
        apperception_data["emotional_charge"] = max(apperception_data["emotional_charge"], heuristic_p.emotional_charge, key=abs)
        apperception_data["semantic_density"] = max(apperception_data["semantic_density"], heuristic_p.semantic_density)
        apperception_data["value_challenge"]  = max(apperception_data["value_challenge"], heuristic_p.value_challenge)

        if apperception_data["value_challenge"] > 0.3:
            print("\n" + "!" * 60)
            print(f"!!! WYKRYTO ATAK AKSJOLOGICZNY (Tv): {apperception_data['value_challenge']:.2f} !!!")
            print("!" * 60 + "\n")

        embedding = _ollama.embed(user_input)

        # ── 2. Krok MindCore (z lockiem) ──
        with _lock:
            cognitive_ctx = _mind.step(user_input, embedding=embedding, continuity=continuity, apperception_data=apperception_data)
            p = _mind.psyche
            
            # --- WIZUALIZACJA W KONSOLI (DEBUG) ---
            print("\n" + "="*50)
            print(f" STEP #{_mind.step_n} | PHASE: {p.phase.value.upper()}")
            print("-" * 50)
            print(f" INPUT: {user_input[:50]}...")
            print(f" SENSORS: {apperception_data}")
            print(f" PSYCHE:  S: {p.anchor:.3f} | A: {p.arousal:.3f} | C: {p.coherence:.3f} | D: {p.dopamine:.3f}")
            print(f" TENSION: Ta: {p.mood_ta:.3f} | Tc: {p.mood_tc:.3f} | Tv: {p.mood_tv:.3f}")
            print("="*50 + "\n")

            recent_engrams = _mind.memory._store[-3:] if _mind.memory._store else []

        # ── 3. Odtworz TensionVector z danych kroku ──
        t = cognitive_ctx['tension']
        tv_obj = TensionVector(affective=t['T_a'], cognitive=t['T_c'], axiological=t['T_v'])

        # ── 4. Zbuduj prompt i parametry ──
        sys_prompt = _prompt_engine.build_system_prompt(_mind.psyche, tv_obj, cognitive_ctx)
        mem_context = _prompt_engine.build_memory_context(recent_engrams)
        messages = _prompt_engine.build_messages(user_input, sys_prompt, mem_context, _chat_history[-10:])
        params = _modulator.modulate(_mind.psyche, tv_obj)

        # ── 5. Streaming odpowiedzi (SSE) ──
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()

        # Wyslij stan kognitywny
        self._write_sse({"type": "cognitive", "data": cognitive_ctx})

        # Streamuj tokeny z Ollama
        full_response = []
        try:
            stream = _ollama.chat(messages, model, params, stream=True)
            # Sprawdz czy dostalismy generator (sukces) czy string (blad)
            if isinstance(stream, str):
                # Blad — cala odpowiedz jako jeden token
                full_response.append(stream)
                self._write_sse({"type": "token", "data": stream})
            else:
                token_count = 0
                for token in stream:
                    full_response.append(token)
                    self._write_sse({"type": "token", "data": token})
                    
                    # Co 10 tokenów wysyłamy przypomnienie o stanie kognitywnym (dla synchronizacji)
                    token_count += 1
                    if token_count % 10 == 0:
                        # Wysyłamy aktualny stan bez robienia nowego kroku (step_n zostaje ten sam)
                        sync_ctx = {
                            "step_n": _mind.step_n,
                            "psyche": _mind.psyche.as_dict(),
                            "tension": tv_obj.as_dict()
                        }
                        self._write_sse({"type": "cognitive", "data": sync_ctx})
        except Exception as e:
            error_msg = f"Blad generacji: {e}"
            self._write_sse({"type": "token", "data": error_msg})
            full_response.append(error_msg)

        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

        # ── 6. Refleksja i zapis (w osobnym watku) ──
        response_text = "".join(full_response)
        _chat_history.append({"role": "user", "content": user_input})
        _chat_history.append({"role": "assistant", "content": response_text})

        threading.Thread(
            target=self._finalize_step,
            args=(user_input, response_text, model),
            daemon=True
        ).start()

    def _finalize_step(self, user_input, response_text, model):
        """Refleksja kognitywna i zapis stanu — w tle."""
        with _lock:
            try:
                reflection = _reflector.reflect(user_input, response_text, _ollama, model)
                
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
                    
            except Exception as e:
                print(f"Blad refleksji: {e}")

            _state_manager.save_all(_mind)

    # ── Metody pomocnicze ──

    def _write_sse(self, payload: dict):
        """Wyslij jedno zdarzenie SSE."""
        data = json.dumps(payload, ensure_ascii=False)
        self.wfile.write(f"data: {data}\n\n".encode('utf-8'))
        self.wfile.flush()

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
        self.end_headers()
        self.wfile.write(body)


def run_server():
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), CogitOSHandler) as httpd:
        print("\n" + "="*50)
        print(" *** CogitOS GRAVITATIONAL CORE v3.5 ACTIVE ***")
        print("="*50 + "\n")
        print(f"Server: http://localhost:{PORT}")
        print(f"Model:  {MODEL_NAME}")
        print(f"Memory: {len(_mind.memory)} engrams")
        print(f"Step:   {_mind.step_n}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nZatrzymywanie serwera...")
            # Zapisujemy tylko jeśli plik istnieje (brak pliku = manualny reset)
            if _state_manager.state_file.exists():
                _state_manager.save_all(_mind)
                print("Stan zapisany.")
            else:
                print("Plik stanu nie istnieje - pomijam autozapis (reset manualny).")


if __name__ == "__main__":
    run_server()
