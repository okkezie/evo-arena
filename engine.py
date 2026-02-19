import json
import random
from typing import Any, Dict, List, Tuple, Optional
from games import Game
from strategies import STRATEGY_REGISTRY, Strategy

# For advanced simulations (DEAP/numpy/matplotlib): lazily imported inside evolutionary_simulation()
# to avoid import errors on minimal envs (see requirements.txt + venv).

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

    def _noisy_decide(self, strat: Strategy, opp_history: List[str], noise: float = 0.0) -> str:
        """
        Get strategy's move with optional noise (0-0.2 prob to flip to other action).
        Handles edge for extensibility (assumes binary actions like PD).
        """
        if not 0 <= noise <= 0.2:
            raise ValueError("Noise must be in [0, 0.2] for realistic error rates.")
        move = strat.decide(opp_history)
        if noise > 0 and random.random() < noise:
            # Flip to alternative valid action (game-agnostic for first game)
            game = list(self.games.values())[0]  # default to PD or first
            valid = game.valid_actions
            other_moves = [a for a in valid if a != move]
            if other_moves:
                return other_moves[0]
            return move  # fallback
        return move

    def _play_match(
        self,
        strat1_name: str,
        strat2_name: str,
        game_name: str = "PD",
        rounds: int = 100,
        noise: float = 0.0,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Private helper: AI vs AI match (reuses decision logic from play_game).
        Supports noise, verbose toggle (for tournament/evo speed), returns scores/moves.
        """
        if game_name not in self.games:
            raise ValueError(f"Unknown game: {game_name}")
        if strat1_name not in self.strategy_names or strat2_name not in self.strategy_names:
            raise ValueError(f"Strats must be from: {self.strategy_names}")

        game = self.games[game_name]
        strat1 = self._get_strategy(strat1_name)
        strat2 = self._get_strategy(strat2_name)

        p1_moves: List[str] = []
        p2_moves: List[str] = []
        p1_score = 0
        p2_score = 0
        move_history: List[Tuple[str, str]] = []

        if verbose:
            print(f"\n=== Match: {strat1_name} vs {strat2_name} | Rounds: {rounds} | Noise: {noise} ===")

        for round_num in range(1, rounds + 1):
            # Noisy decisions
            p1_move = self._noisy_decide(strat1, p2_moves, noise)
            p2_move = self._noisy_decide(strat2, p1_moves, noise)

            # Update histories/moves
            p1_moves.append(p1_move)
            p2_moves.append(p2_move)
            move_history.append((p1_move, p2_move))

            # Payoffs
            payoff = game.get_payoff(p1_move, p2_move)
            p1_score += payoff[0]
            p2_score += payoff[1]

            if verbose:
                print(f"Round {round_num}: P1={p1_move}({strat1_name}), P2={p2_move}({strat2_name}) | "
                      f"Payoffs=({payoff[0]}, {payoff[1]}) | Scores=(P1:{p1_score}, P2:{p2_score})")

        if verbose:
            print(f"\n=== Match Over === Final: {strat1_name}={p1_score}, {strat2_name}={p2_score}")

        return {
            "scores": (p1_score, p2_score),
            "moves": move_history,
            "strats": (strat1_name, strat2_name),
            "rounds": rounds,
            "noise": noise
        }

    def play_game(
        self,
        game_name: str,
        mode: int,
        strat1_name: Optional[str] = None,
        strat2_name: Optional[str] = None,
        rounds: Optional[int] = None
    ) -> Dict[str, Any]:
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

    def repeated_match(
        self,
        game_name: str = "PD",
        strat1_name: str = "TitForTat",
        strat2_name: str = "AlwaysDefect",
        rounds: int = 100,
        noise: float = 0.0
    ) -> Dict[str, Any]:
        """
        Feature 1: Single repeated match between two strategies.
        - Default 100 rounds, optional noise (0-0.2) for move flips.
        - Full console output per round + summary.
        """
        print(f"\n--- Single Repeated Match: {strat1_name} vs {strat2_name} (rounds={rounds}, noise={noise}) ---")
        rounds = rounds or 100
        noise = max(0.0, min(0.2, noise or 0.0))
        result = self._play_match(strat1_name, strat2_name, game_name, rounds, noise, verbose=True)
        p1_s, p2_s = result["scores"]
        print(f"Summary: {strat1_name}={p1_s}, {strat2_name}={p2_s} (over {rounds} rounds)")
        return result

    def round_robin_tournament(
        self,
        game_name: str = "PD",
        rounds_per_match: int = 100,
        repeats: int = 1,
        noise: float = 0.0
    ) -> Dict[str, Any]:
        """
        Feature 2: Round-robin tournament (every strat vs every other, incl. self-matches).
        - Uses _play_match (suppressed output) for speed.
        - Averages over repeats, shows ranked leaderboard by total points.
        """
        print(f"\n--- Round-Robin Tournament | Rounds/match={rounds_per_match}, Repeats={repeats}, Noise={noise} ---")
        strats = self.strategy_names
        total_scores: Dict[str, float] = {s: 0.0 for s in strats}
        # Full round-robin: every vs every (incl. self-matches, reverse for symmetry)
        for rep in range(repeats):
            for s1 in strats:
                for s2 in strats:
                    res = self._play_match(s1, s2, game_name, rounds_per_match, noise, verbose=False)
                    total_scores[s1] += res["scores"][0]  # accumulate P1 score when s1 plays

        # If repeats >1, totals already summed
        # Rank
        ranked = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
        print("\nLeaderboard (total points):")
        for rank, (strat, score) in enumerate(ranked, 1):
            print(f"  {rank}. {strat}: {score:.1f} points")
        return {"total_scores": total_scores, "ranking": ranked}

    def evolutionary_simulation(
        self,
        game_name: str = "PD",
        pop_size: int = 100,
        generations: int = 30,
        rounds_per_match: int = 50,
        noise: float = 0.0,
        plot: bool = True
    ) -> Dict[str, Any]:
        """
        Feature 3: Basic evolutionary sim using DEAP GA.
        - Pop of strategy types, fitness via mini-tournaments.
        - Std ops; per-gen stats/freqs; final rank + optional plot.
        - Tuned small for speed (short matches, sampled fitness).
        - Requires: deap, numpy, matplotlib (pip install -r requirements.txt; use venv).
        """
        print(f"\n--- Evolutionary Simulation | Pop={pop_size}, Gens={generations}, Noise={noise} ---")

        # Lazy import for DEAP/numpy/matplotlib (avoids ModuleNotFound on base Python envs;
        # only needed for this feature. See README/requirements.txt + venv setup.)
        try:
            from deap import base, creator, tools
            import numpy as np
            import matplotlib.pyplot as plt
        except ImportError as e:
            raise ImportError(
                "DEAP, numpy, and matplotlib are required for evolutionary simulations. "
                "Install with: source venv/bin/activate && pip install -r requirements.txt"
            ) from e

        # DEAP setup (handle re-runs in same process)
        try:
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
            creator.create("Individual", list, fitness=creator.FitnessMax)
        except RuntimeError:
            pass  # types already exist

        strat_list = self.strategy_names
        n_strats = len(strat_list)

        toolbox = base.Toolbox()
        toolbox.register("attr_idx", random.randint, 0, n_strats - 1)
        # Individual = [strat_idx] for categorical evolution
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_idx, n=1)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        def eval_fitness(individual):
            """Fitness: avg score from quick matches vs sampled opponents (for speed)."""
            strat_name = strat_list[individual[0]]
            score = 0.0
            n_opp = 5  # sample for perf
            short_rounds = max(5, rounds_per_match // 10)
            for _ in range(n_opp):
                opp_name = random.choice(strat_list)
                res = self._play_match(strat_name, opp_name, game_name, short_rounds, noise, verbose=False)
                score += res["scores"][0]
            return (score / n_opp,)

        toolbox.register("evaluate", eval_fitness)
        # GA ops (simple for idx lists; cxUniform safe for len=1 individuals)
        toolbox.register("mate", tools.cxUniform, indpb=0.5)  # uniform swap prob, avoids range err on small chromo
        toolbox.register("mutate", tools.mutUniformInt, low=0, up=n_strats - 1, indpb=0.2)
        toolbox.register("select", tools.selTournament, tournsize=3)

        # Init pop
        pop = toolbox.population(n=pop_size)

        # Stats + freq track
        stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        stats.register("avg", np.mean)
        stats.register("max", np.max)
        freq_history: List[Dict[str, float]] = []

        for gen in range(generations):
            # Evaluate
            fitnesses = list(map(toolbox.evaluate, pop))
            for ind, fit in zip(pop, fitnesses):
                ind.fitness.values = fit
            # Record
            record = stats.compile(pop)
            # Freqs
            idx_counts = [ind[0] for ind in pop]
            freq = {strat_list[i]: idx_counts.count(i) / pop_size for i in range(n_strats)}
            freq_history.append(freq)
            print(f"Gen {gen}: Max={record['max']:.1f}, Avg={record['avg']:.1f}, "
                  f"Freqs={{ {', '.join(f'{k}:{v:.2f}' for k,v in freq.items())} }}")

            # Evolve
            offspring = toolbox.select(pop, len(pop))
            offspring = list(map(toolbox.clone, offspring))
            # Crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.5:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            # Mutation low rate
            for mutant in offspring:
                if random.random() < 0.1:  # low
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
            pop[:] = offspring

        # Re-evaluate any invalid fitness (post last crossover/mutation)
        # Ensures all ind have .fitness.values for final ranking
        invalid_ind = [ind for ind in pop if not ind.fitness.valid]
        if invalid_ind:
            fitnesses = list(map(toolbox.evaluate, invalid_ind))
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

        # Final ranking
        ranked_final = sorted(
            [(strat_list[ind[0]], ind.fitness.values[0]) for ind in pop],
            key=lambda x: x[1], reverse=True
        )
        print("\nFinal Population Ranking (top):")
        for strat, fit in ranked_final[:5]:
            print(f"  - {strat}: {fit:.1f}")
        winner = ranked_final[0][0]
        print(f"Winner: {winner}")

        # Optional plot freqs
        if plot:
            try:
                gens = range(generations)
                for s in strat_list:
                    freqs = [f[s] for f in freq_history]
                    plt.plot(gens, freqs, label=s)
                plt.xlabel("Generation")
                plt.ylabel("Frequency")
                plt.title("Strategy Frequencies Over Evolution")
                plt.legend()
                plt.show()  # displays in console env if supported; else skip
            except Exception as e:
                print(f"Plot skipped (e.g., headless): {e}")

        return {"final_ranking": ranked_final, "winner": winner, "freq_history": freq_history}
