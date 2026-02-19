from abc import ABC, abstractmethod
from typing import List, Dict, Type

class Strategy(ABC):
    """
    Base abstract class for game strategies.
    Subclasses implement decide() based on opponent's history.
    """
    @abstractmethod
    def decide(self, opponent_history: List[str]) -> str:
        """
        Decide next move based on opponent's move history.
        Returns: 'C' or 'D' (or game-specific action)
        """
        pass

class AlwaysCooperate(Strategy):
    """Always cooperates, regardless of history."""
    def decide(self, opponent_history: List[str]) -> str:
        return 'C'

class AlwaysDefect(Strategy):
    """Always defects, regardless of history."""
    def decide(self, opponent_history: List[str]) -> str:
        return 'D'

class TitForTat(Strategy):
    """
    Cooperates first, then copies opponent's last move.
    Classic forgiving strategy.
    """
    def decide(self, opponent_history: List[str]) -> str:
        if not opponent_history:
            return 'C'  # Start with cooperate
        return opponent_history[-1]  # Mirror last move

class GrimTrigger(Strategy):
    """
    Cooperates until opponent defects once, then always defects.
    Punitive strategy.
    """
    def decide(self, opponent_history: List[str]) -> str:
        if 'D' in opponent_history:
            return 'D'  # Permanent punishment
        return 'C'

# Registry for dynamic strategy loading from config
STRATEGY_REGISTRY: Dict[str, Type[Strategy]] = {
    'AlwaysCooperate': AlwaysCooperate,
    'AlwaysDefect': AlwaysDefect,
    'TitForTat': TitForTat,
    'GrimTrigger': GrimTrigger,
}
