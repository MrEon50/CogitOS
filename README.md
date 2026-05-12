# CogitOS - Warstwa Kognitywna dla Ollama

CogitOS to system, który działa jako "zewnętrzny mózg" dla Twoich lokalnych modeli LLM. Zamiast zwykłego czatu, system symuluje procesy poznawcze, takie jak tożsamość, emocje i inteligentna pamięć długotrwała.

## 🚀 Jak uruchomić CogitOS

### 1. Wymagania (Ollama)
Aby system działał poprawnie, musisz mieć zainstalowaną aplikację **Ollama** oraz pobrane następujące modele:

*   **Model językowy:** Dowolny model (np. `gemma4:4b`, `llama3`, `mistral`), który będzie odpowiadał w czacie.
*   **Model embeddingowy (Wymagany do pamięci RAG):**
    ```bash
    ollama pull mxbai-embed-large
    ```
    *Bez tego modelu system nie będzie mógł zapisywać ani odszukiwać wspomnień (engramów).*

### 2. Uruchomienie
1.  Kliknij dwukrotnie plik **`run_cogitos.bat`**.
2.  Otwórz przeglądarkę pod adresem: **`http://127.0.0.1:8800`**.

---

## 🧠 Jak działa CogitOS? (Neural Resonance v3.6)

CogitOS to system **Homeostatyczny**, w którym stan umysłu jest nierozerwalnie związany z pamięcią asocjacyjną i czasem.

### 1. Pamięć jako Bodziec (Neural Resonance)
*   **Rezonans Asocjacyjny**: Engramy (wspomnienia) nie są tylko danymi. Każde przywołane wspomnienie "pompuje" napięcie Afektu ($Ta$) lub Wartości ($Tv$) zgodnie ze swoim ładunkiem.
*   **Pamięć Chronologiczna**: Każde wspomnienie posiada pieczątkę czasową, pozwalającą systemowi orientować się, kiedy dane zdarzenie miało miejsce.
*   **Pamięć Wykuta w Stresie**: Im wyższe napięcie w momencie tworzenia wspomnienia, tym jest ono silniejsze i trudniejsze do wyparcia.

### 2. Ekonomia Dopaminy (Bez przebaczenia)
*   **Koszt Bytowania**: System posiada wysoki koszt bazowy. Brak stymulacji prowadzi do apatii i spadku dopaminy.
*   **Lęk przed Pustką**: Gdy dopamina spada poniżej 0.35, system wpada w stan niepokoju — Afekt ($Ta$) rośnie samoistnie.
*   **Satysfakcja z Wiedzy**: Praca intelektualna ($Tc$) daje niewielkie bonusy dopaminowe przy wysokiej spójności.

### 3. Dynamika Napięć
*   **Asymetria**: Napięcia rosną błyskawicznie w odpowiedzi na bodźce, ale opadają bardzo powoli ($Decay=0.96$).
*   **Blokada Strachu**: Skrajny Afekt ($Ta > 0.8$) paraliżuje logikę ($Tc$) niezależnie od nagrody.

### 4. Świadomość Czasu i Ciągłość
*   **Zegar Systemowy**: Model posiada wgląd w aktualną datę i godzinę, co pozwala mu na chronologiczną orientację w rozmowie.
*   **Stabilność Offline**: System jest zoptymalizowany do pracy bez internetu (sztywne adresy IP, kognitywne limity czasu połączenia).

### 5. Katarzis (Rzadka i Trudna)
Ulga kognitywna (spadek napięcia) następuje tylko przy wyjątkowo silnych nagrodach dopaminowych i wysokiej spójności.

### 6. Reset Synaptyczny (Katharsis)
Automatyczna procedura ratunkowa przy długotrwałym braku spójności ($C < 0.2$). Powoduje wyczerpanie dopaminy i powrót parametrów do stanu bazowego.

---

### 7. Pętla Kognitywna i Pamięć
1.  **Appercepcja (System 1):** Podprogowa ocena semantyczna wejścia.
2.  **Rezonans Pamięci (RAG):** Automatyczne przywoływanie engramów na podstawie podobieństwa embeddingów.
3.  **Autogenna Refleksja (System 2):** Samodzielna ocena jakości wygenerowanej odpowiedzi i przyznanie nagrody dopaminowej.
4.  **Tabula Rasa:** Możliwość całkowitego resetu pamięci i stanów kognitywnych jednym przyciskiem.

---

## 🛠 Struktura projektowa
*   **core/** – Silnik Grawitacyjny (psyche, percept, moment, tension).
*   **bridge/** – System 1 (Appercepcja) i System 2 (Refleksja).
*   **memory/** – Pamięć asocjacyjna engramów.
*   **cogitos_chat.html** – Dashboard kognitywny (Premium UI).
*   **run_cogitos.bat** – Launcher systemu.
*   **stop_cogitos.bat** – Skrypt bezpiecznego wyłączenia procesów.

---
*Autor: MrEon50*
