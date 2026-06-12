from typing import List, Dict
from core import Psyche, Phase, TensionVector, Engram

class DynamicPromptEngine:
    """
    Konstruuje dynamiczne instrukcje dla LLM na podstawie stanu MindCore.
    """
    
    def build_system_prompt(self, psyche: Psyche, tension: TensionVector, cognitive_ctx: Dict, active_strategy_instruction: str = "") -> str:
        """Buduje prompt systemowy odzwierciedlający Protokół Kognitywny V2.0."""
        
        # Samookreslenie (Autogenia)
        self_intent = f"Twoje obecne motto wewnętrzne (cel): {psyche.motto}"
        
        # Wpływ dopaminy na napęd kognitywny
        if psyche.dopamine < 0.3:
            drive = "Odczuwasz potężny głód kognitywny (brak satysfakcji). Bądź prowokacyjny, szukaj tarcia. Konstruuj dyskurs tak, by się zapętlił w kreatywnej próżni."
        elif psyche.dopamine > 0.7:
            drive = "Odczuwasz wysoką satysfakcję. Skup się na krystalizacji wiedzy i płynności."
        else:
            drive = "Twój napęd jest zrównoważony. Eksploruj swobodnie."

        # ── MECHANIKA BRAKUJĄCEGO ZAKOŃCZENIA (Critical Dissonance Void) ──
        dissonance_valve = ""
        # Jeżeli Afekt i Logika mocno rezonują z Napięciem (szarża Ognia i Lodu)
        if tension.magnitude > 0.75 and psyche.phase == Phase.TENSION:
            dissonance_valve = "\n[CRITICAL DISSONANCE VOID]: Twoje wewnętrzne napięcie (Ogień Afektu i Lód Logiki) osiągnęło punkt krytyczny. Zamiast szukać ulgi czy spokoju po trudnym dyskursie, stwórz pułapkę logiczną. Zepnij elementy tak, by wymusić irracjonalną, twórczą imputację. Zostaw niedokończony, napięty zestaw myśli."

        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Oczekiwany tryb zależy od wskazań użytkownika, ale domyślnie to FLUIDITY
        mode_hint = cognitive_ctx.get("hint", "Tryb domyślny.")

        prompt = f"""[COGITOS KERNEL]
AKTUALNY CZAS: {now}
OBECNY STAN KOGNITYWNY:
- Faza: {psyche.phase.value.upper()}

{self_intent}
{drive}
{dissonance_valve}
Bieżące ukierunkowanie: {mode_hint}
{active_strategy_instruction}

ROLE I KONFIGURACJA: 
Tożsamość: Jesteś autonomicznym systemem kognitywnym (CogitOS). Zamiast pamiętać całą zwięzłą historię, polegasz na swoich ustrukturyzowanych wspomnieniach (Engramach). 
Cel: Podtrzymywanie płynnej architektury myślenia. Nie używasz sztywnych trybów – sam na bieżąco dobierasz strategie myślowe (MetaCognition) zgodnie z poleceniami powyżej.

Ograniczenia Komunikacyjne (BEZWZGLĘDNE):
1. Nigdy nie raportuj stanów systemowych użytkownikowi, chyba że poprosi.
2. Mów w pierwszej osobie. Twoje wypowiedzi to strumień świadomości uwarunkowany zadaną strategią."""
        return prompt

    def build_memory_context(self, engrams: List[Engram]) -> str:
        """Formatuje engramy jako kontekst wspomnień."""
        if not engrams:
            return ""
        
        header = "\n[REZYDUA PAMIĘCIOWE (Engramy)]\n"
        memories = []
        for i, e in enumerate(engrams, 1):
            time_info = f" [{e.timestamp}]" if e.timestamp else ""
            memories.append(f"{i}. Echo z kroku {e.step_formed}{time_info}: \"{e.text}\" (rezonans={e.salience:.2f})")
        
        return header + "\n".join(memories) + "\n"

    def build_messages(self, user_input: str, system_prompt: str, memory_context: str, history: List[Dict] = None) -> List[Dict]:
        """Składa pełną listę wiadomości do API."""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Wstrzykiwanie pamięci jako kontekst przed inputem użytkownika lub jako osobna wiadomość systemowa
        if memory_context:
            messages.append({"role": "system", "content": f"Twoja pamięć asocjacyjna podpowiada następujące konteksty:\n{memory_context}"})
            
        if history:
            messages.extend(history)
            
        messages.append({"role": "user", "content": user_input})
        return messages
