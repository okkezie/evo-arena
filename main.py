import sys
from engine import GameTheoryEngine

if __name__ == "__main__":
    """
    Console menu for EvoArena.
    - Selects game (from config, default PD)
    - Chooses mode (0=auto, 1=single human, 2=multi human)
    - Picks strategies for AI players (from config registry)
    - Runs game via engine.play_game()
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

    # Mode selection
    print("\nModes:")
    print("  0 = Auto (AI vs AI, 0 humans)")
    print("  1 = Single (1 human vs AI)")
    print("  2 = Multi (2 humans, alternating input)")
    mode_input = input("Select mode (default: 0): ").strip()
    try:
        mode = int(mode_input) if mode_input else 0
    except ValueError:
        print("Invalid mode. Defaulting to 0 (auto).")
        mode = 0

    # Strategy selection for AI players (from registry in strategies.py)
    available_strats = engine.strategy_names
    print(f"\nAvailable strategies: {available_strats}")
    strat1_name = None
    strat2_name = None
    if mode == 0:  # auto: both AI
        strat1_name = input(f"Strategy for P1 (default: TitForTat): ").strip() or "TitForTat"
        strat2_name = input(f"Strategy for P2 (default: AlwaysDefect): ").strip() or "AlwaysDefect"
    elif mode == 1:  # single: human P1 vs AI P2
        strat2_name = input(f"Strategy for AI (P2) (default: TitForTat): ").strip() or "TitForTat"
    # mode 2: both human, no strats needed

    # Optional rounds override
    rounds_input = input(f"Rounds (default: {engine.default_rounds}): ").strip()
    rounds = int(rounds_input) if rounds_input else None

    # Validate strat choices if provided
    for strat in [s for s in [strat1_name, strat2_name] if s]:
        if strat not in available_strats:
            print(f"Invalid strategy: {strat}. Available: {available_strats}")
            sys.exit(1)

    # Run the game
    print("\nStarting game...")
    try:
        result = engine.play_game(
            game_name=game_name,
            mode=mode,
            strat1_name=strat1_name,
            strat2_name=strat2_name,
            rounds=rounds
        )
        print(f"\nGame completed. Final result: {result}")
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except Exception as e:
        print(f"\nError during game: {e}")
        sys.exit(1)
