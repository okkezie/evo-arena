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