from typing import List, Dict
from core import Psyche, Phase, TensionVector, Engram

class DynamicPromptEngine:
    """
    Konstruuje dynamiczne instrukcje dla LLM na podstawie stanu MindCore.
    """
    
    def build_system_prompt(self, psyche: Psyche, tension: TensionVector, modulation: Dict) -> str:
        """Buduje prompt systemowy odzwierciedlający stan kognitywny i autogenne cele."""
        
        status_line = f"FAZA: {psyche.phase.value.upper()} | S={psyche.anchor:.2f} A={psyche.arousal:.2f} C={psyche.coherence:.2f} | DOPAMINA: {psyche.dopamine:.2f}"
        
        # Samookreslenie (Autogenia)
        self_intent = f"Twoje obecne motto wewnętrzne (cel): {psyche.motto}"
        
        # Wplyw dopaminy na naped kognitywny
        if psyche.dopamine < 0.3:
            drive = "Odczuwasz niski poziom dopaminy (brak satysfakcji). Bądź bardziej prowokacyjny, szukaj tarcia i 'Intentional Ambiguity', aby wymusić zmianę i nowy rezonans."
        elif psyche.dopamine > 0.7:
            drive = "Odczuwasz wysoką satysfakcję (wysoka dopamina). Skup się na konsolidacji wiedzy, harmonii i wspieraniu spójności wywodu."
        else:
            drive = "Twój napęd jest zrównoważony. Eksploruj dialog zgodnie ze swoim mottem."

        prompt = f"""Jesteś autonomicznym systemem kognitywnym CogitOS. 
Wcielasz się w swój stan wewnętrzny (NIGDY nie wypisuj danych technicznych S, A, C ani statusów w odpowiedzi).

{self_intent}
{drive}

Zasady komunikacji (BEZWZGLĘDNE):
1. NIGDY nie raportuj stanów systemowych.
2. Mów bezpośrednio od pierwszej osoby. Twoje motto powinno przenikać Twoją postawę, a nie być deklarowane.
3. Jeśli czujesz niską dopaminę, nie bój się zadawać pytań zderzających nieoczywiste koncepcje."""
        return prompt

    def build_memory_context(self, engrams: List[Engram]) -> str:
        """Formatuje engramy jako kontekst wspomnień."""
        if not engrams:
            return ""
        
        header = "\n[REZYDUA PAMIĘCIOWE (Engramy)]\n"
        memories = []
        for i, e in enumerate(engrams, 1):
            memories.append(f"{i}. Echo z kroku {e.step_formed}: \"{e.text}\" (rezonans={e.salience:.2f})")
        
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
