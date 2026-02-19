# EvoArena: Console-Based Python Game Theory Simulator

## Overview
EvoArena is a config-driven game theory simulator that supports single (human vs AI), multi (human vs human), and auto (AI vs AI) modes. Currently implements Prisoner's Dilemma (PD), with easy extensibility for additional games and strategies via `config.json` and strategy registry.

## Quick Start
Run the simulator:
```
python main.py
```

## Testing Guide
- **Console Testing**:
  - Auto mode (AI vs AI): `python main.py` → select game=PD, mode=0, strats e.g. TitForTat vs AlwaysDefect
  - Single mode (Human vs AI): mode=1, provide moves for Player 1 (C/D)
  - Multi mode (Human vs Human): mode=2, alternate inputs
- **Edge Cases**:
  - Invalid moves: Input invalid action (e.g., 'X') → should raise ValueError
  - Config errors: Modify config.json (e.g., invalid payoffs) → engine should handle gracefully or raise appropriate errors
  - Run tests: `python -m unittest tests.games_test tests.strategies_test tests.engine_test` (or individually; note: discover with default pattern needs test*.py rename for auto)

## Extensibility
- Add new games: Extend `"games"` section in `config.json` with payoffs and valid_actions
- New strategies: Implement subclass of `Strategy` in `strategies.py` and register in `STRATEGY_REGISTRY`
- Future: Integrate DEAP for evolution (via requirements.txt)

## Game Modes
- `0`: Auto (0 humans) - AI vs AI, observer mode
- `1`: Single (1 human) - Human (P1 input) vs AI
- `2`: Multi (2 humans) - Alternating console inputs

## New Simulation Features
Run via `python main.py` and select sim type:

### 1. Single Repeated Match (type=1)
- AI vs AI (e.g., TitForTat vs GrimTrigger)
- Default 100 rounds; optional noise (0-0.2) randomly flips moves
- Prints per-round moves/payoffs/totals + summary
- Example: `...` → detailed console output

### 2. Round-Robin Tournament (type=2)
- All strategies vs all others (incl. self-matches)
- Uses match logic internally (no per-round spam)
- Config: rounds/match (100), repeats (avg), noise
- Outputs ranked leaderboard by total points
- Fast even with repeats

### 3. Evolutionary Simulation (type=3, uses DEAP)
- Population of agents (50-150) evolving strategy genes
- Fitness from tournaments; standard GA (sel/cx/mut)
- Per-gen stats (best/avg fitness, strat freqs)
- Final ranking + winner; optional matplotlib freq plot
- Tuned for speed (short matches, sampling)

## Updated Testing Guide
- **New Features Console Tests**:
  - Repeated: sim=1, strats=TitForTat/AlwaysDefect, noise=0.1
  - Tournament: sim=2, repeats=1
  - Evo: sim=3, pop=50, gens=20 (check plot/stats)
- **Edge Cases**: noise>0.2 error, small pop for evo, invalid strats
- Unit tests now cover: `python -m unittest tests.engine_test` (noise, sims)
- Run in venv: `source venv/bin/activate && python main.py`

## Extensibility
- Add new games: Extend `"games"` section in `config.json` with payoffs and valid_actions
- New strategies: Implement subclass of `Strategy` in `strategies.py` and register in `STRATEGY_REGISTRY`
- DEAP evolution: Customize toolbox/ fitness in engine.evolutionary_simulation for advanced (e.g., more complex GA)