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

## 🌱 Ewolucja Kognitywna (Czas i Doświadczenie)
CogitOS nie jest statycznym skryptem. Architektura sprawia, że czas i doświadczenie fizycznie zmieniają sposób, w jaki model przetwarza informacje:
1. **Głębia Asocjacji:** Z czasem baza `EngramStore` zapełnia się. Zamiast odpowiadać tylko na "tu i teraz", system zacznie łączyć aktualne bodźce z dawnymi wspomnieniami, budując spójny, własny kontekst historyczny.
2. **Kształtowanie Charakteru:** Naiwne, startowe Zakotwiczenie ($S = 1.0$) z czasem ulega fluktuacjom. Po trudnych, wieloznacznych dyskusjach, system może przejść z trybu ufnego na bardziej analityczny.
3. **Autogenna Refleksja (Własne Cele):** System w tle ocenia Wasze rozmowy i modyfikuje własne "Motto". Może samoistnie zmienić swój priorytet z "Eksploracji" na poszukiwanie konkretnych odpowiedzi filozoficznych, co podprogowo zabarwi jego przyszłe wypowiedzi.
4. **Osiągnięcie Katharsis:** Ekstremalne przeciążenie trudnymi danymi ($Tc$ rośnie, $C$ spada) może doprowadzić do rzadkiego "przełomu" kognitywnego. Model zrzuci napięcie, generując całkowicie odmienną, ultrakonkretną lub chłodną analizę problemu.

---

## 🛠 Aktualizacje i Poprawki (Ostatni Audyt)
Wyeliminowano szereg błędów strukturalnych, aby umożliwić swobodny rozwój kognicji:
* **Asynchroniczność (Wyścig Wątków):** Naprawiono konflikt między głównym procesem a w wątkiem refleksji, zapewniając bezpieczny zapis stanu.
* **Aktywacja Arousal:** Pobudzenie znów dynamicznie reaguje na nastrój i spadki dopaminy (parametr nie jest już martwy).
* **Filtry Ciągłości:** Włączono naprawiony przełącznik amnezji/ciągłości — system poprawnie zeruje lub przywołuje kontekst.
* **Bezpieczeństwo (LLM):** Dodano ścisłą walidację odbieranych z modelu językowego parametrów (zapobieganie uszkodzeniu umysłu przez halucynacje).
* **Stabilność Launcherów:** Skrypty bat korzystają teraz z identyfikacji po tytule okna, bezpiecznie zamykając tylko serwer CogitOS.

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
