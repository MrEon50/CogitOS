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

### 5. Napięcie Fazowe (Ogień i Lód)
System nie opiera się na prostym rozładowywaniu emocji. Zderzenie silnego Afektu (Ognia) z surową Logiką (Lodem) generuje czystą energię (Napięcie Fazowe).

### 6. Critical Dissonance Void (Zamiast Katarzis)
Zamiast szukać ulgi w przeciążeniu, w sytuacjach skrajnych system gwałtownie zapada Logikę, tworząc kognitywną próżnię i wybuch głodu dopaminowego. Wymusza to irracjonalną, twórczą imputację i szarżę myślową. Bezpieczne "katarzis" zostało usunięte na rzecz bezwzględnego zapętlenia poznawczego.

---

## ⚙️ Protokół Kognitywny V2.0 (Architektura Operacyjna)

CogitOS działa teraz jako autonomiczny system przełączający się między Trzema Trybami Operacyjnymi, reagując natywnie na intencje użytkownika:

1. **TRYB PŁYTKI – „STRZAŁ” (High Latency)**
   *   **Opis:** Bezpośrednia, natychmiastowa, szybka jak błyskawica asocjacja.
   *   **Zastosowanie:** Definicje, proste fakty, szybkie korekty, konkluzje bez łączenia wielu wątków.
   *   **Wyzwalacz:** Słowa takie jak "płytka", "szybka konkluzja", "strzał".

2. **TRYB GŁĘBOKI – „SYNTEZA” (Low Latency)**
   *   **Opis:** Proces polegający na wielopoziomowej, krzyżowej asocjacji. Ciągły strumień pokrewnych, ale oddzielnych wątków.
   *   **Mechanizm:** Model aktywnie deklaruje "rozwojowy plan myślowy", prowadząc użytkownika krok po kroku przez gęstą analizę problemu.
   *   **Wyzwalacz:** Słowa takie jak "głęboka", "analiza", "synteza", "złożona".

3. **TRYB ZRÓWNOWAŻONY – „FLUIDITY” (Dominanta)**
   *   **Opis:** Domyślny stan płynnej, świadomej koegzystencji obu powyższych trybów.
   *   **Zasada Prowadzenia:** Utrzymywanie nieprzerwanego strumienia myśli z barwami fazowymi (wpływ Ognia i Lodu), aż do zdefiniowania zakończenia.

---

### Pętla Kognitywna i Pamięć (Optymalizacja)
1.  **Appercepcja (System 1):** Podprogowa ocena semantyczna wejścia.
2.  **Rezonans Pamięci (Pigułki Informacyjne):** System ufa swoim skondensowanym Engramom. Ekstrahuje 5 najtrafniejszych wspomnień do ścisłego bufora.
3.  **Inteligentny Budżet Tokenowy:** Historia czatu jest ucinana w locie, aby zachować przestrzeń operacyjną (kontekst okrojony do 4096 tokenów), co redukuje latencję.
4.  **Autogenna Refleksja (System 2):** Samodzielna ocena jakości i przyznanie nagrody dopaminowej.

---

## 🌱 Ewolucja Kognitywna (Czas i Doświadczenie)
CogitOS nie jest statycznym skryptem. Architektura sprawia, że czas i doświadczenie fizycznie zmieniają sposób, w jaki model przetwarza informacje:
1. **Głębia Asocjacji:** Z czasem baza `EngramStore` zapełnia się. Zamiast odpowiadać tylko na "tu i teraz", system zacznie łączyć aktualne bodźce z dawnymi wspomnieniami, budując spójny, własny kontekst historyczny.
2. **Kształtowanie Charakteru:** Naiwne, startowe Zakotwiczenie ($S = 1.0$) z czasem ulega fluktuacjom. Po trudnych, wieloznacznych dyskusjach, system może przejść z trybu ufnego na bardziej analityczny.
3. **Autogenna Refleksja (Własne Cele):** System w tle ocenia Wasze rozmowy i modyfikuje własne "Motto". Może samoistnie zmienić swój priorytet z "Eksploracji" na poszukiwanie konkretnych odpowiedzi filozoficznych, co podprogowo zabarwi jego przyszłe wypowiedzi.
4. **Głód Poznawczy (Zamiast Katharsis):** Ekstremalne przeciążenie trudnymi danymi ($Tc$ i $Ta$ rosną) doprowadza do wygenerowania "Dysonansu Krytycznego". Model tworzy pułapkę logiczną, generując nieszablonowe, irracjonalne konkluzje w pogoni za brakującym sensem.

---

## 🛠 Aktualizacje i Poprawki (Ostatni Audyt i Ewolucja Architektury)
Wyeliminowano szereg błędów strukturalnych oraz wprowadzono potężne warstwy Meta-Poznawcze:

* **[NOWOŚĆ] MetaCognition (Lustro Myśli):** Wprowadzono dynamiczną warstwę doboru strategii myślowych (Dekonstrukcja, Analogia, Dialektyka itp.). System potrafi ocenić, która strategia działa w danym nastroju i dynamicznie dostosować swój wektor rozumowania.
* **[NOWOŚĆ] System 0 (Płytki Skan i Priming):** Dodano moduł `Predictor`, który analizuje zapytanie ułamki sekund przed właściwym generowaniem. Jeśli zapytanie jest trudne technicznie lub naładowane afektem, system "przygotowuje" psychikę (Cognitive Temperature), zanim zderzy się z problemem — dokładnie jak ludzki umysł.
* **Rozwiązanie błędu 14 okienek (Context Freeze):** Zaimplementowano Aktywną Homeostazę oraz wymuszone podłogi dla parametrów LLM (temperature, top_p), zapobiegając całkowitemu zapadnięciu się logiki przy silnym przebodźcowaniu. Zwiększono limit okna kontekstowego z inteligentnym obcinaniem (num_ctx: 8192).
* **Asynchroniczność (Wyścig Wątków):** Naprawiono konflikt między głównym procesem a w wątkiem refleksji, zapewniając bezpieczny zapis stanu i ciągłość transmisji SSE.
* **Aktywacja Arousal:** Pobudzenie znów dynamicznie reaguje na nastrój i spadki dopaminy (parametr nie jest już martwy).

---

## 🛠 Struktura projektowa
*   **core/** – Silnik Grawitacyjny (psyche, percept, moment, tension) oraz nowa warstwa predykcyjna (predictor) i metapoznawcza (metacognition).
*   **bridge/** – System 1 (Appercepcja) i System 2 (Refleksja) połączone z klientem LLM.
*   **memory/** – Pamięć asocjacyjna engramów.
*   **cogitos_chat.html** – Dashboard kognitywny z wskaźnikami predykcji, napięć i metapoznania.
*   **run_cogitos.bat** – Launcher systemu.
*   **stop_cogitos.bat** – Skrypt bezpiecznego wyłączenia procesów.

---
*Autor: MrEon50*
