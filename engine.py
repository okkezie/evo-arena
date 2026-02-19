import json
from typing import Dict, List, Tuple, Optional
from games import Game
from strategies import STRATEGY_REGISTRY, Strategy

class GameTheoryEngine:
    """
    Config-driven engine for game theory simulations.
    Supports auto (AI vs AI), single (human vs AI), multi (human vs human) modes.
    """
    def __init__(self, config_path: str = 'config.json'):
        """Load config, initialize games from Game.from_config, strategies list."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        # Create game instances
        self.games: Dict[str, Game] = {}
        for name, data in self.config['games'].items():
            self.games[name] = Game.from_config(data)
        self.strategy_names: List[str] = self.config['strategies']
        self.default_rounds: int = self.config.get('default_rounds', 10)

    def _get_strategy(self, name: str) -> Strategy:
        """Instantiate strategy from registry."""
        if name not in STRATEGY_REGISTRY:
            raise ValueError(f"Unknown strategy: {name}. Available: {list(STRATEGY_REGISTRY.keys())}")
        return STRATEGY_REGISTRY[name]()

    def _get_human_move(self, game: Game, player: str) -> str:
        """Get validated move from human input via console."""
        while True:
            move = input(f"Player {player}'s move {game.valid_actions} (C/D for PD): ").strip().upper()
            try:
                game.validate_move(move)
                return move
            except ValueError as e:
                print(f"Error: {e}. Try again.")

    def play_game(
        self,
        game_name: str,
        mode: int,
        strat1_name: Optional[str] = None,
        strat2_name: Optional[str] = None,
        rounds: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Run a game session.
        - mode 0: auto AI vs AI (requires both strats)
        - mode 1: single human P1 vs AI P2 (requires strat2_name)
        - mode 2: multi human vs human (no strats)
        Returns dict with final scores and move history.
        """
        if rounds is None:
            rounds = self.default_rounds
        if game_name not in self.games:
            raise ValueError(f"Unknown game: {game_name}")

        game = self.games[game_name]

        # Load AI strategies if needed for the mode
        # - P1 AI only in auto (mode 0)
        # - P2 AI in auto (0) and single (1)
        strat1 = self._get_strategy(strat1_name) if strat1_name and mode == 0 else None
        strat2 = self._get_strategy(strat2_name) if strat2_name and mode in (0, 1) else None

        # Validation for required strategies per mode
        # mode 0: auto AI vs AI - both strats required
        if mode == 0 and (not strat1_name or not strat2_name):
            raise ValueError("Auto mode requires both strat1_name and strat2_name")
        # mode 1: single human P1 vs AI P2 - strat2 required
        if mode == 1 and not strat2_name:
            raise ValueError("Single mode requires strat2_name")
        # mode 2: multi human vs human - no strats needed
        if mode not in [0, 1, 2]:
            raise ValueError("Mode must be 0 (auto), 1 (single), 2 (multi)")

        # Histories: list of opponent's moves for each player's strategy
        p1_moves: List[str] = []  # for P2's opp history
        p2_moves: List[str] = []  # for P1's opp history
        p1_score = 0
        p2_score = 0
        move_history: List[Tuple[str, str]] = []

        print(f"\n=== Starting {game_name} | Mode: {mode} | Rounds: {rounds} ===")
        if mode == 0:
            print(f"AI1: {strat1_name} vs AI2: {strat2_name}")
        elif mode == 1:
            print(f"Human (P1) vs AI: {strat2_name}")
        else:
            print("Human (P1) vs Human (P2)")

        for round_num in range(1, rounds + 1):
            # Determine moves based on mode
            if mode == 0:  # auto AI vs AI
                p1_move = strat1.decide(p2_moves)  # P1 sees P2's previous moves
                p2_move = strat2.decide(p1_moves)
            elif mode == 1:  # human P1 vs AI P2
                p1_move = self._get_human_move(game, "1")
                p2_move = strat2.decide(p1_moves)
            elif mode == 2:  # multi human vs human
                p1_move = self._get_human_move(game, "1")
                p2_move = self._get_human_move(game, "2")

            # Record moves and update histories
            p1_moves.append(p1_move)
            p2_moves.append(p2_move)
            move_history.append((p1_move, p2_move))

            # Get payoffs and update scores
            payoff = game.get_payoff(p1_move, p2_move)
            p1_score += payoff[0]
            p2_score += payoff[1]

            # Print turn result
            print(f"Round {round_num}: P1={p1_move}, P2={p2_move} | Payoffs=({payoff[0]}, {payoff[1]}) | Scores=(P1:{p1_score}, P2:{p2_score})")

        print(f"\n=== Game Over === Final Scores: P1={p1_score}, P2={p2_score}")
        return {'scores': (p1_score, p2_score), 'moves': move_history}
