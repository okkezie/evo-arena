from abc import ABC, abstractmethod
from typing import List, Dict, Type

class Strategy(ABC):
    """
    Base abstract class for game strategies.
    Subclasses implement decide() based on opponent's history.
    All strategies loaded dynamically from system/ and custom/.
    """
    @abstractmethod
    def decide(self, opponent_history: List[str]) -> str:
        """
        Decide next move based on opponent's move history (abstract 'C'/'D').
        Returns: 'C' (coop-like) or 'D' (defect-like) for semantic compatibility.
        """
        pass

class AlwaysCooperate(Strategy):
    """Always cooperates, regardless of history. [system]"""
    def decide(self, opponent_history: List[str]) -> str:
        return 'C'

class AlwaysDefect(Strategy):
    """Always defects, regardless of history. [system]"""
    def decide(self, opponent_history: List[str]) -> str:
        return 'D'

class TitForTat(Strategy):
    """
    Cooperates first, then copies opponent's last move.
    Classic forgiving strategy. [system]
    """
    def decide(self, opponent_history: List[str]) -> str:
        if not opponent_history:
            return 'C'  # Start with cooperate
        return opponent_history[-1]  # Mirror last move

class GrimTrigger(Strategy):
    """
    Cooperates until opponent defects once, then always defects.
    Punitive strategy. [system]
    """
    def decide(self, opponent_history: List[str]) -> str:
        if 'D' in opponent_history:
            return 'D'  # Permanent punishment
        return 'C'

# Note: registry built dynamically by discovery; no static dict here