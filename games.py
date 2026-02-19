from typing import Dict, Tuple, List
import ast

class Game:
    """
    Abstract Game class for game theory simulations.
    Config-driven via from_config classmethod; supports any 2x2 game with custom actions/labels.
    """
    def __init__(
        self,
        payoffs: Dict[Tuple[str, str], Tuple[int, int]],
        valid_actions: List[str],
        description: str = ""
    ):
        """
        Initialize game with payoff matrix, valid actions (ordered: [0]=coop-like 'C', [1]=defect-like 'D'),
        and description. Enables extensibility for Hawk-Dove, Stag Hunt, etc.
        """
        self.payoffs = payoffs
        self.valid_actions = valid_actions
        self.description = description

    def validate_move(self, move: str) -> None:
        """Validate if move is in valid_actions."""
        if move not in self.valid_actions:
            raise ValueError(f"Invalid move: {move}. Valid actions: {self.valid_actions}")

    def get_payoff(self, p1_move: str, p2_move: str) -> Tuple[int, int]:
        """Get payoffs for given moves, after validation."""
        self.validate_move(p1_move)
        self.validate_move(p2_move)
        return self.payoffs[(p1_move, p2_move)]

    @classmethod
    def from_config(cls, data: dict) -> 'Game':
        """
        Create Game instance from config dict.
        Parses string keys like "('C', 'C')" using ast.literal_eval.
        Also extracts optional 'description' for UI.
        Assumes binary actions ordered [0]=coop-like ('C' for strats), [1]=defect-like.
        """
        payoffs: Dict[Tuple[str, str], Tuple[int, int]] = {}
        for key_str, value in data['payoffs'].items():
            # Convert string representation of tuple to actual tuple (concrete labels)
            moves: Tuple[str, str] = ast.literal_eval(key_str)
            payoffs[moves] = tuple(value)
        # Description for menu/output; defaults empty
        description = data.get("description", f"{data.get('name', 'Game')} payoff matrix.")
        # Pass valid_actions (concrete names) + desc; payoffs use concrete tuples
        return cls(payoffs, data["valid_actions"], description)
