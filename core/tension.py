import math
from dataclasses import dataclass

@dataclass
class TensionVector:
    """
    Trzy wymiary tarcia. Silnik systemu, nie błąd do wyeliminowania.
    """
    affective:   float = 0.0
    cognitive:   float = 0.0
    axiological: float = 0.0

    KATHARSIS_THRESHOLD = 0.76
    TENSION_MIN         = 0.28

    @property
    def magnitude(self) -> float:
        return math.sqrt(self.affective**2 + self.cognitive**2 + self.axiological**2) / math.sqrt(3)

    @property
    def dissonance(self) -> float:
        """Dysonans afektywno-poznawczy: im wyższy, tym trudniejsza chłodna analiza."""
        return abs(self.affective - self.cognitive)

    @property
    def dominant(self) -> str:
        tensions = {"affective": self.affective, "cognitive": self.cognitive, "axiological": self.axiological}
        return max(tensions, key=tensions.get)

    def as_dict(self) -> dict:
        return {"T_a": round(self.affective, 3), "T_c": round(self.cognitive, 3),
                "T_v": round(self.axiological, 3), "mag": round(self.magnitude, 3),
                "dysonans": round(self.dissonance, 3), "dom": self.dominant}
