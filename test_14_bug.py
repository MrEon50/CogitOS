import requests
import json
import time

URL = "http://127.0.0.1:8800/api/chat"
MODEL = "gemma4:e4b"  # lub jaki tam model jest dostepny

def test_chat(num_requests=16):
    print("Rozpoczynamy testowanie do 16 okienek...")
    for i in range(1, num_requests + 1):
        print(f"\n--- WYSYŁANIE ZAPYTANIA #{i} ---")
        payload = {
            "message": f"Testowa wiadomość numer {i}. Proszę odpowiedzieć krótko.",
            "model": MODEL,
            "continuity": True
        }
        
        start_time = time.time()
        try:
            with requests.post(URL, json=payload, stream=True, timeout=300) as r:
                print(f"Status CODE: {r.status_code}")
                if r.status_code != 200:
                    print("Błąd HTTP!")
                    print(r.text)
                    break
                
                content_chunks = 0
                for line in r.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        if decoded.startswith("data: "):
                            data_str = decoded[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if data.get("type") == "token":
                                    content_chunks += 1
                            except:
                                pass
                
                elapsed = time.time() - start_time
                print(f"Odebrano {content_chunks} tokenów w {elapsed:.2f}s")
                
        except requests.exceptions.Timeout:
            print(f"TIMEOUT przy wiadomości #{i}!")
            break
        except Exception as e:
            print(f"Błąd połączenia przy wiadomości #{i}: {e}")
            break

if __name__ == "__main__":
    test_chat()
