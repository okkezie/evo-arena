import sys
from engine import GameTheoryEngine

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

    # Game selection (extensible via config.json)
    available_games = list(engine.games.keys())
    print(f"Available games: {available_games}")
    game_name = input(f"Select game (default: PD): ").strip() or "PD"
    if game_name not in available_games:
        print(f"Invalid game. Defaulting to PD.")
        game_name = "PD"

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

            # Strategy selection for AI players
            strat1_name = None
            strat2_name = None
            if mode == 0:  # auto AI vs AI
                strat1_name = input("Strat for P1 (default: TitForTat): ").strip() or "TitForTat"
                strat2_name = input("Strat for P2 (default: AlwaysDefect): ").strip() or "AlwaysDefect"
            elif mode == 1:  # human P1 vs AI P2
                strat2_name = input("Strat for AI P2 (default: TitForTat): ").strip() or "TitForTat"
            # mode 2: humans only

            # Validate
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
            # Repeated match
            strat1_name = input("Strat for P1 (default: TitForTat): ").strip() or "TitForTat"
            strat2_name = input("Strat for P2 (default: AlwaysDefect): ").strip() or "AlwaysDefect"
            # Validate
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
