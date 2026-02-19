import importlib
import pkgutil
from typing import Dict, Type

# Import base Strategy for subclass check
from .system.built_in import Strategy

def load_strategies() -> Dict[str, Type[Strategy]]:
    """
    Auto-discover and load ALL Strategy subclasses from strategies/system/ and strategies/custom/.
    - Uses pkgutil/importlib for folder-based dynamic loading.
    - Builds unified registry by class name.
    - Handles duplicates/errors gracefully (skip + log).
    - Called on startup for engine/menu.
    """
    registry: Dict[str, Type[Strategy]] = {}
    for subfolder in ['system', 'custom']:
        package = f"strategies.{subfolder}"
        try:
            # Ensure package importable
            pkg = importlib.import_module(package)
            # Scan modules in subfolder (non-recursive for simplicity)
            for finder, mod_name, is_pkg in pkgutil.iter_modules(pkg.__path__, package + "."):
                if is_pkg:
                    continue  # skip subpkgs
                try:
                    # Import module
                    module = importlib.import_module(mod_name)
                    # Find Strategy subclasses (non-abstract concrete impls)
                    # (isabstract removed for compatibility; ABC subclass + != base suffices)
                    for attr_name in dir(module):
                        cls = getattr(module, attr_name)
                        if (
                            isinstance(cls, type)
                            and issubclass(cls, Strategy)
                            and cls is not Strategy
                        ):
                            name = cls.__name__
                            if name in registry:
                                print(f"Warning: duplicate strategy '{name}' from {mod_name} (skipping)")
                                continue
                            registry[name] = cls
                            print(f"Loaded strategy: {name} from {subfolder}/")
                except Exception as e:
                    print(f"Error loading {mod_name}: {e} (skipped)")
        except Exception as e:
            print(f"Error scanning {subfolder}/: {e} (skipped)")
    return registry

# Unified registry (system + custom)
STRATEGY_REGISTRY: Dict[str, Type[Strategy]] = load_strategies()