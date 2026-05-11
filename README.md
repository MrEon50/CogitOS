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
2.  Otwórz przeglądarkę pod adresem: **`http://localhost:8800`**.

---

## 🧠 Jak działa CogitOS? (Architektura Gravitational Core v3.5)

CogitOS to dynamiczny system **Homeostatyczny**. W wersji v3.5 system przeszedł ewolucję z prostych reakcji na rzecz złożonych sprzężeń kognitywnych opartych na **Złotym Podziale ($\phi \approx 0.618$)**.

### 1. Spójność (C) - Meta-Parametr i "Tarcie"
Spójność ($C$) pełni rolę nadrzędnego dyrygenta. Mierzy rezonans między emocjami ($Ta$), logiką ($Tc$) a wartościami ($Tv$).
*   **Stan Flow**: Gdy $C \approx 0.618$, system myśli najefektywniej przy minimalnym zużyciu energii.
*   **Tarcie (Friction)**: Gdy $C < 0.35$, dashboard w przeglądarce zaczyna fizycznie drżeć, sygnalizując dysonans i stres kognitywny.

### 2. Ekonomia Dopaminy (Brak darmowej nagrody)
Dopamina przestała być darmowa — system musi na nią zapracować.
*   **Koszt Myślenia**: Każda głęboka analiza ($Tc$) zużywa zapas Dopaminy. Im większy stres ($C$), tym koszt jest wyższy.
*   **Nagroda (Reward)**: System otrzymuje "strzał" dopaminy tylko za wzrost spójności (rozwiązanie problemu) oraz wysoką gęstość sensu w swoich wypowiedziach.

### 3. Grawitacja Wartości i Inercja Aksjologiczna
Wartości ($Tv$) działają jak masa kognitywna systemu:
*   **Inercja**: Wysokie $Tv$ sprawia, że Afekt ($Ta$) reaguje wolniej i stabilniej (trudniej "rozhuśtać" system).
*   **Integrysta**: Silna Logika ($Tc$) dodatkowo wzmacnia "ciężar" Wartości, czyniąc system niemal niewzruszonym na manipulację.

### 4. Blokady Stanu Umysłu (Stress Response)
System posiada nieliniowe mechanizmy obronne:
*   **Emotional Takeover**: Przy skrajnie wysokim Afekcie ($Ta$) i niskiej Dopaminie, Logika ($Tc$) ulega "zamrożeniu" (spadek o 50%). System przestaje myśleć racjonalnie.
*   **Erozja Zasad**: W stanie ekstremalnego wzburzenia, Wartości ($Tv$) tracą swój wpływ na system — instynkt bierze górę nad etyką.

### 5. Reset Synaptyczny (Katharsis)
Jeśli system zbyt długo przebywa w stanie skrajnego dysonansu ($C < 0.2$), następuje automatyczny **Reset Synaptyczny**. Faza zmienia się w **Katharsis**, dopamina zostaje wyczerpana, a parametry wracają do bazy, by zapobiec trwałej niestabilności.

---

### 6. Pętla Kognitywna i Pamięć
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
*Autor: CogitOS MindCore Architecture Team & User*
