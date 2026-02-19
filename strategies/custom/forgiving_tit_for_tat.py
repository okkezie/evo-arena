from typing import List
# Import base from system (sibling package)
from ..system.built_in import Strategy

class ForgivingTitForTat(Strategy):
    """
    Forgiving variant of TitForTat: cooperates after 2 consecutive defects.
    Demonstrates custom strategy in user folder. [custom]
    """
    def decide(self, opponent_history: List[str]) -> str:
        """Start C, mirror last, but forgive after two D's (encourages recovery)."""
        if not opponent_history:
            return 'C'
        if len(opponent_history) >= 2 and opponent_history[-2:] == ['D', 'D']:
            return 'C'  # forgive double defect
        return opponent_history[-1]  # else mirror