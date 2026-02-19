# strategies package for folder-based loading
# - system/ : built-in strategies (core)
# - custom/ : user-added strategies (extend here)
# Auto-discovery via registry.py; unified STRATEGY_REGISTRY exposed here.

from .registry import load_strategies, STRATEGY_REGISTRY
# Re-export base for convenience/tests
from .system.built_in import Strategy

# On import: registry auto-builds (prints loaded for debug)
# Supports duplicates/errors gracefully as per spec.