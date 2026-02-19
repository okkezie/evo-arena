from typing import Dict, Tuple, List
import ast

class Game:
    """
    Abstract Game class for game theory simulations.
    Config-driven via from_config classmethod.
    """
    def __init__(self, payoffs: Dict[Tuple[str, str], Tuple[int, int]], valid_actions: List[str]):
        """
        Initialize game with payoff matrix and valid actions.
        payoffs: dict with (p1_move, p2_move) -> (p1_payoff, p2_payoff)
        """
        self.payoffs = payoffs
        self.valid_actions = valid_actions

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
        """
        payoffs: Dict[Tuple[str, str], Tuple[int, int]] = {}
        for key_str, value in data['payoffs'].items():
            # Convert string representation of tuple to actual tuple
            moves: Tuple[str, str] = ast.literal_eval(key_str)
            payoffs[moves] = tuple(value)
        return cls(payoffs, data['valid_actions'])
