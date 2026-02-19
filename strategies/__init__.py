# strategies package for folder-based loading
# - system/ : built-in strategies (core)
# - custom/ : user-added strategies (extend here)
# Auto-discovery via registry.py; unified STRATEGY_REGISTRY exposed here.

from .registry import load_strategies, STRATEGY_REGISTRY
# Re-export base for convenience/tests
from .system.built_in import Strategy

# On import: registry auto-builds (prints loaded for debug)
# Supports duplicates/errors gracefully as per spec.

# Dynamically re-export all strategies for convenience/backward compat in tests/menu
# e.g., from strategies import ForgivingTitForTat, AlwaysCooperate
for _name, _cls in STRATEGY_REGISTRY.items():
    globals()[_name] = _cls

__all__ = list(STRATEGY_REGISTRY.keys()) + ["Strategy", "STRATEGY_REGISTRY", "load_strategies"]