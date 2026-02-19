import sys
from engine import GameTheoryEngine

def select_strategy(available_strats: list[str], player_label: str = "") -> str:
    """
    Show full list of loaded strategies (system + custom), allow selection by name or number.
    Handles invalid gracefully with default.
    Supports dynamic registry from folders.
    """
    if not available_strats:
        raise ValueError("No strategies loaded")
    label = f" for {player_label}" if player_label else ""
    print(f"\nAvailable strategies{label}: {available_strats}")
    # Numbered for ease
    for i, s in enumerate(available_strats, 1):
        print(f"  {i}. {s}")
    choice = input(f"Select by name or # (default: {available_strats[0]}): ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(available_strats):
            return available_strats[idx]
    if choice in available_strats:
        return choice
    # Fallback
    print(f"Invalid choice '{choice}'. Defaulting to {available_strats[0]}")
    return available_strats[0]

if __name__ == "__main__":
    """
    Console menu for EvoArena.
    - Game selection from config.json
    - Sim type: basic (orig human/AI), repeated match, round-robin tournament, evolutionary (DEAP)
    - Params prompts for new sims: strats, rounds, noise (0-0.2), tourn repeats, pop/gens for evo
    - Calls engine methods; graceful errors
    """
    print("=== EvoArena: Game Theory Simulator ===")
    engine = GameTheoryEngine()

    # Game selection (extensible via config.json; now supports PD, Hawk-Dove, Stag Hunt)
    # Accepts full name, initials/abbrev (case-insensitive, e.g., pd/HD/sh/stag hunt)
    available_games = list(engine.games.keys())
    print(f"Available games: {available_games}")
    game_name = input(f"Select game (default: PD): ").strip() or "PD"

    # Abbrev mapping for convenience (common initials/full variants)
    game_abbrev = {
        # PD
        "pd": "PD", "prisoners": "PD", "prisonersdilemma": "PD",
        # Hawk-Dove
        "hd": "HawkDove", "hawkdove": "HawkDove", "hawk": "HawkDove", "dove": "HawkDove",
        # Stag Hunt
        "sh": "StagHunt", "stag": "StagHunt", "staghunt": "StagHunt", "stag hunt": "StagHunt",
        "stag-hunt": "StagHunt", "hare": "StagHunt",
    }
    # Normalize input (lower, no spaces/punct)
    norm = game_name.lower().replace(" ", "").replace("-", "").replace("_", "").replace("'", "")
    if norm in game_abbrev:
        game_name = game_abbrev[norm]
        print(f"Resolved abbreviation to: {game_name}")
    if game_name not in available_games:
        print(f"Invalid game '{game_name}'. Defaulting to PD.")
        game_name = "PD"

    # Print game description (one-line overview)
    game = engine.games[game_name]
    print(f"\nSelected Game: {game_name} - {game.description}")

    # Simulation type selection
    print("\nSimulation Types:")
    print("  0 = Basic Game (human vs AI, multi-human; original modes)")
    print("  1 = Single Repeated Match (AI vs AI, defaults 100 rounds)")
    print("  2 = Round-Robin Tournament (all strats vs all, ranked)")
    print("  3 = Evolutionary Simulation (DEAP GA, pop evolution)")
    sim_input = input("Select sim type (default: 0): ").strip()
    try:
        sim_type = int(sim_input) if sim_input else 0
    except ValueError:
        print("Invalid sim type. Defaulting to 0 (basic).")
        sim_type = 0

    available_strats = engine.strategy_names
    print(f"\nAvailable strategies: {available_strats}")

    # Common error handling
    try:
        if sim_type == 0:
            # Original basic modes (human/AI)
            print("\nBasic Modes (for humans):")
            print("  0 = Auto (AI vs AI)")
            print("  1 = Single (human vs AI)")
            print("  2 = Multi (human vs human)")
            mode_input = input("Select basic mode (default: 0): ").strip()
            mode = int(mode_input) if mode_input else 0

            # Strategy selection for AI players (from full dynamic registry: system/ + custom/)
            # Use helper for name/number pick
            strat1_name = None
            strat2_name = None
            if mode == 0:  # auto AI vs AI
                strat1_name = select_strategy(available_strats, "P1")
                strat2_name = select_strategy(available_strats, "P2")
            elif mode == 1:  # human P1 vs AI P2
                strat2_name = select_strategy(available_strats, "AI P2")
            # mode 2: humans only

            # Validate (redundant with helper but kept)
            for strat in [s for s in [strat1_name, strat2_name] if s]:
                if strat not in available_strats:
                    print(f"Invalid strategy: {strat}. Available: {available_strats}")
                    sys.exit(1)

            # Rounds
            rounds_input = input(f"Rounds (default: {engine.default_rounds}): ").strip()
            rounds = int(rounds_input) if rounds_input else None

            # Run
            print("\nStarting basic game...")
            result = engine.play_game(
                game_name=game_name,
                mode=mode,
                strat1_name=strat1_name,
                strat2_name=strat2_name,
                rounds=rounds
            )
            print(f"\nGame completed. Final result: {result}")

        elif sim_type == 1:
            # Repeated match (AI vs AI from full registry)
            strat1_name = select_strategy(available_strats, "P1")
            strat2_name = select_strategy(available_strats, "P2")
            # Validate (redundant with helper)
            for strat in [strat1_name, strat2_name]:
                if strat not in available_strats:
                    print(f"Invalid: {strat}")
                    sys.exit(1)
            rounds_in = input("Rounds (default: 100): ").strip()
            rounds = int(rounds_in) if rounds_in else 100
            noise_in = input("Noise prob (0-0.2, default 0): ").strip()
            noise = float(noise_in) if noise_in else 0.0
            print("\nStarting repeated match...")
            engine.repeated_match(game_name, strat1_name, strat2_name, rounds, noise)

        elif sim_type == 2:
            # Round-robin
            rounds_m_in = input("Rounds per match (default: 100): ").strip()
            rounds_per_match = int(rounds_m_in) if rounds_m_in else 100
            repeats_in = input("Repeats for averaging (default: 1): ").strip()
            repeats = int(repeats_in) if repeats_in else 1
            noise_in = input("Noise (0-0.2, default 0): ").strip()
            noise = float(noise_in) if noise_in else 0.0
            print("\nStarting tournament...")
            engine.round_robin_tournament(game_name, rounds_per_match, repeats, noise)

        elif sim_type == 3:
            # Evo sim
            pop_in = input("Population size (50-150, default: 100): ").strip()
            pop_size = int(pop_in) if pop_in else 100
            gens_in = input("Generations (20-50, default: 30): ").strip()
            generations = int(gens_in) if gens_in else 30
            rounds_m_in = input("Rounds per match in fitness (default: 50): ").strip()
            rounds_per_match = int(rounds_m_in) if rounds_m_in else 50
            noise_in = input("Noise (0-0.2, default 0): ").strip()
            noise = float(noise_in) if noise_in else 0.0
            plot_in = input("Show frequency plot? (y/n, default y): ").strip().lower()
            plot = plot_in != "n"
            print("\nStarting evolution (may take a minute)...")
            engine.evolutionary_simulation(game_name, pop_size, generations, rounds_per_match, noise, plot)

        else:
            print("Invalid sim type.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nError: {e} (check params, e.g., noise<=0.2, strats valid)")
        sys.exit(1)
