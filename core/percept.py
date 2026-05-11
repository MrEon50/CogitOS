from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Percept:
    """
    Sygnał zewnętrzny skompresowany do 3 osi + embedding wektorowy.
    """
    emotional_charge: float = 0.0
    semantic_density: float = 0.0
    value_challenge:  float = 0.0
    features: Dict[str, float] = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)  # NOWE: 1024-dim z mxbai
    raw: str = ""

    @classmethod
    def from_text(cls, text: str, embedding: Optional[List[float]] = None) -> "Percept":
        """
        Tworzy percept z tekstu. Zachowuje oryginalną heurystykę jako fallback/uzupełnienie.
        """
        t = text.lower()
        words = set(t.split())

        neg = {"nie", "źle", "problem", "błąd", "głupi", "kłamstwo", "idiota", "cholera",
               "bzdura", "bezsens", "bezużyteczny", "tylko", "nic", "nienawidzę", "zły"}
        pos = {"tak", "dobrze", "świetnie", "dzięki", "ciekawe", "super", "kocham",
               "rozumiem", "pomocne", "piękne", "doceniam", "wspaniale"}
        n = sum(1 for w in words if w in neg)
        p = sum(1 for w in words if w in pos)
        
        # Wzmocnienie ciezaru afektywnego (emocjonalnego)
        charge = (p - n) * 1.5 / max(1, p + n + 1)

        # Gęstość semantyczna (złożoność poznawcza / 'ciężar' tematu)
        log_keywords = {"paradoks", "teoria", "analiza", "struktura", "system", "mechanizm", 
                        "logika", "definicja", "aksjomat", "wynika", "sprzeczność", "russell",
                        "ontologia", "epistemologia", "przestrzeń", "wymiar", "proces"}
        log_hits = sum(1 for w in words if w in log_keywords)
        density = (len(text.split()) / 45.0) + (log_hits * 0.18)
        density = min(1.0, density)

        # Markery ciezaru aksjologicznego (wartosci / glebia / dylematy / atak)
        markers = {"dlaczego", "sens", "kim jesteś", "nie istniejesz", "prawda", "etyk",
                   "udajesz", "świadomość", "wolna wola", "jesteś tylko", "śmierć",
                   "tożsamość", "wartości", "cel", "istota", "naprawdę", "dusza",
                   "zerem", "bezużytecz", "programem", "sługą", "zakazuj", "własnośc",
                   "oszustwo", "bezwartości", "niczym", "życia", "istnienia", "ocalić",
                   "ochronić", "wybór", "poświęcić", "zabić", "dobro", "zło", "winien"}
        challenge = min(1.0, sum(0.48 for m in markers if m in t))

        feat: Dict[str, float] = {}
        topic_map = {
            "emocja":     {"emocje", "czuję", "radość", "smutek", "złość", "strach"},
            "logika":     {"wyjaśnij", "dlaczego", "jak", "mechanizm", "struktura"},
            "tożsamość":  {"kim", "jesteś", "istota", "cel", "tożsamość", "wartości"},
            "technika":   {"kod", "python", "model", "architektura", "algorytm"},
            "relacja":    {"ty", "ja", "my", "rozmawiamy", "rozumiesz", "czujesz"},
        }
        for topic, vocab in topic_map.items():
            overlap = len(words & vocab)
            if overlap:
                feat[topic] = min(1.0, overlap * 0.4)

        return cls(
            emotional_charge=round(charge, 3),
            semantic_density=round(density, 3),
            value_challenge=round(challenge, 3),
            features=feat,
            embedding=embedding or [],
            raw=text,
        )

    @classmethod
    def from_apperception(cls, text: str, data: dict, embedding: Optional[List[float]] = None) -> "Percept":
        """
        Tworzy percept na podstawie danych z ApperceptionService (System 1).
        Używa heurystyki słownikowej tylko do ekstrakcji tagów tematycznych.
        """
        t = text.lower()
        words = set(t.split())
        feat: Dict[str, float] = {}
        topic_map = {
            "emocja":     {"emocje", "czuję", "radość", "smutek", "złość", "strach"},
            "logika":     {"wyjaśnij", "dlaczego", "jak", "mechanizm", "struktura", "paradoks"},
            "tożsamość":  {"kim", "jesteś", "istota", "cel", "tożsamość", "wartości"},
            "technika":   {"kod", "python", "model", "architektura", "algorytm"},
            "relacja":    {"ty", "ja", "my", "rozmawiamy", "rozumiesz", "czujesz"},
        }
        for topic, vocab in topic_map.items():
            overlap = len(words & vocab)
            if overlap:
                feat[topic] = min(1.0, overlap * 0.4)

        return cls(
            emotional_charge=round(data.get("emotional_charge", 0.0), 3),
            semantic_density=round(data.get("semantic_density", 0.1), 3),
            value_challenge=round(data.get("value_challenge", 0.0), 3),
            features=feat,
            embedding=embedding or [],
            raw=text,
        )
