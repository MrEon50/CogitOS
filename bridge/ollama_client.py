import json
import urllib.request
import urllib.error
from typing import List, Dict, Generator, Optional

class OllamaClient:
    """
    Klient HTTP dla Ollama API (bez zewnętrznych zależności).
    """
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def embed(self, text: str, model: str = "mxbai-embed-large") -> List[float]:
        """Tworzy embedding dla podanego tekstu."""
        url = f"{self.base_url}/api/embed"
        data = json.dumps({"model": model, "input": text}).encode("utf-8")
        
        try:
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=10) as response:
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
                with urllib.request.urlopen(req, timeout=60) as response:
                    resp_data = json.loads(response.read().decode("utf-8"))
                    return resp_data.get("message", {}).get("content", "")
        except Exception as e:
            print(f"Błąd Ollama chat: {e}")
            return "Błąd komunikacji z modelem kognitywnym."

    def _handle_stream(self, req: urllib.request.Request) -> Generator[str, None, None]:
        """Obsługuje streaming odpowiedzi z Ollama."""
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                for line in response:
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
        except Exception as e:
            yield f"\n[Błąd streamingu: {e}]"

    def list_models(self) -> List[str]:
        """Zwraca listę dostępnych modeli."""
        url = f"{self.base_url}/api/tags"
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                return [m["name"] for m in data.get("models", [])]
        except:
            return []
