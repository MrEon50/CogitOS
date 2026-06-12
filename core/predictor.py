import re
from typing import Dict

class PredictionState:
    """Stan predykcyjny określający wstępne obciążenie po szybkim skanie."""
    def __init__(self, delta_tc: float = 0.0, delta_ta: float = 0.0, is_complex: bool = False, is_affective: bool = False):
        self.delta_tc = delta_tc
        self.delta_ta = delta_ta
        self.is_complex = is_complex
        self.is_affective = is_affective

    def as_dict(self) -> Dict[str, float]:
        return {
            "delta_tc": self.delta_tc,
            "delta_ta": self.delta_ta,
            "is_complex": self.is_complex,
            "is_affective": self.is_affective
        }

class Predictor:
    """
    Szybki skan (Lightweight Predictive Scan) - System 0.
    Oblicza pre-emptively koszty poznawcze przed uruchomieniem ciężkiego przetwarzania LLM.
    """
    def __init__(self):
        # Prosty słownik afektywny dla szybkiego skanu polskiego języka
        self.affective_keywords = [
            "zły", "nie", "głupi", "błąd", "źle", "strasznie", "problem", "dlaczego", 
            "bez sensu", "awaria", "krytyczny", "pilne", "szybko", "nienawidzę", "kocham", 
            "świetnie", "super", "genialnie", "tragedia", "wściekły", "smutny", "napięcie"
        ]
        
        # Słowa wskazujące na silne zawiłości analityczne
        self.complexity_keywords = [
            "oblicz", "zaprojektuj", "przeanalizuj", "algorytm", "architektura", "skrypt", 
            "zoptymalizuj", "struktura", "system", "zależności", "wygeneruj", "porównaj", "wyjaśnij"
        ]

    def scan(self, text: str) -> PredictionState:
        """Wykonuje płytki skan wejścia użytkownika i zwraca PredictionState."""
        if not text:
            return PredictionState()

        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        word_count = len(words)

        delta_tc = 0.0
        delta_ta = 0.0

        # --- Estymacja Kosztu Poznawczego (Tc) ---
        # Baza: objętość (im dłuższy tekst, tym więcej do analizy)
        if word_count > 100:
            delta_tc += 0.4
        elif word_count > 40:
            delta_tc += 0.2
        elif word_count > 15:
            delta_tc += 0.1

        # Analiza złożoności gramatycznej (ilość zdań, przecinków)
        sentences = len(re.split(r'[.!?]+', text))
        commas = text.count(',')
        
        if sentences > 5 or commas > 8:
            delta_tc += 0.2

        # Słowa kluczowe wskazujące na ciężar analityczny
        complex_hits = sum(1 for w in self.complexity_keywords if w in text_lower)
        if complex_hits > 0:
            delta_tc += min(0.3, complex_hits * 0.1)

        # --- Estymacja Napięcia Afektywnego (Ta) ---
        affect_hits = sum(1 for w in self.affective_keywords if w in text_lower)
        if affect_hits > 0:
            delta_ta += min(0.5, affect_hits * 0.15)
            
        # Wykrzykniki lub CAPS LOCK (prosty wykrywacz krzyku)
        if text.count('!') > 1 or (text.isupper() and word_count > 2):
            delta_ta += 0.2

        # Ustalenie progów
        is_complex = delta_tc >= 0.3
        is_affective = delta_ta >= 0.25

        # Normalizacja do [0.0, 1.0]
        delta_tc = min(1.0, max(0.0, delta_tc))
        delta_ta = min(1.0, max(0.0, delta_ta))

        return PredictionState(
            delta_tc=delta_tc,
            delta_ta=delta_ta,
            is_complex=is_complex,
            is_affective=is_affective
        )
