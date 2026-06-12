import json
import socket
import urllib.request
import urllib.error
from typing import List, Dict, Generator, Optional

# BUG-20 FIX: Per-read socket timeout (sekundy). Chroni przed zawieszeniem
# streamu, gdy Ollama przestaje wysyłać tokeny (np. przepełnienie kontekstu,
# OOM, lub model utknął w inference). 15s bez tokena = realny problem.
STREAM_READ_TIMEOUT = 120.0  # BUG-21 FIX: z 30s na 120s — baaardzo długi czas na prefill przy dużych promptach

class OllamaClient:
    """
    Klient HTTP dla Ollama API (bez zewnętrznych zależności).
    """
    def __init__(self, base_url: str = "http://127.0.0.1:11434"):
        self.base_url = base_url

    def embed(self, text: str, model: str = "mxbai-embed-large") -> List[float]:
        """Tworzy embedding dla podanego tekstu."""
        url = f"{self.base_url}/api/embed"
        data = json.dumps({"model": model, "input": text}).encode("utf-8")
        
        try:
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=5.0) as response:
                resp_data = json.loads(response.read().decode("utf-8"))
                # mxbai-embed-large zwraca listę list w 'embeddings'
                return resp_data.get("embeddings", [[]])[0]
        except Exception as e:
            print(f"Błąd Ollama embed: {e}")
            return []

    def chat(self, messages: List[Dict], model: str, params: Dict, stream: bool = True) -> Generator[str, None, None] | str:
        """Wysyła zapytanie czatowe do Ollama."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "options": params,
            "stream": stream
        }
        data = json.dumps(payload).encode("utf-8")

        try:
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("Content-Type", "application/json")
            
            if stream:
                return self._handle_stream(req)
            else:
                with urllib.request.urlopen(req, timeout=25.0) as response:
                    resp_data = json.loads(response.read().decode("utf-8"))
                    return resp_data.get("message", {}).get("content", "")
        except Exception as e:
            print(f"Błąd Ollama chat: {e}")
            return "Błąd komunikacji z modelem kognitywnym."

    def _handle_stream(self, req: urllib.request.Request) -> Generator[str, None, None]:
        """Obsługuje streaming odpowiedzi z Ollama z ochroną przed zawieszeniem.

        BUG-20 FIX: Ustawia per-read socket timeout (STREAM_READ_TIMEOUT)
        zamiast timeout na całe połączenie. Zapobiega sytuacji, w której
        Ollama przestaje wysyłać tokeny (prefill, OOM, context overflow)
        i handler wisi bez końca.
        """
        response = None
        try:
            response = urllib.request.urlopen(req, timeout=120)
            # Wymuszamy timeout na KAŻDY read() z osobna
            sock = response.fp.raw._sock if hasattr(response.fp, 'raw') else None
            if sock is not None:
                sock.settimeout(STREAM_READ_TIMEOUT)
            for line in response:
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break
        except socket.timeout:
            yield f"\n[Timeout: Ollama milczy od {STREAM_READ_TIMEOUT}s. Możliwe przepełnienie kontekstu lub przeciążenie modelu.]"
        except Exception as e:
            yield f"\n[Błąd streamingu: {e}]"
        finally:
            if response is not None:
                try:
                    response.close()
                except Exception:
                    pass

    def list_models(self) -> List[str]:
        """Zwraca listę dostępnych modeli."""
        url = f"{self.base_url}/api/tags"
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                return [m["name"] for m in data.get("models", [])]
        except:
            return []
