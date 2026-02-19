import unittest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from strategies package (auto-discovery from system/ + custom/)
# Includes ForgivingTitForTat from custom/
from strategies import (
    AlwaysCooperate,
    AlwaysDefect,
    TitForTat,
    GrimTrigger,
    ForgivingTitForTat,  # from custom/
    STRATEGY_REGISTRY,
    Strategy
)

class TestStrategies(unittest.TestCase):
    """Tests for strategies.py: each strategy behavior with various histories."""

    def setUp(self):
        """Instantiate all strategy classes for testing."""
        self.always_coop = AlwaysCooperate()
        self.always_defect = AlwaysDefect()
        self.tit_for_tat = TitForTat()
        self.grim_trigger = GrimTrigger()

    def test_strategy_registry(self):
        """Test registry contains all strategies and maps to classes.
        Now dynamic from system/ + custom/ folders (5 total incl. ForgivingTitForTat).
        """
        # Expect built-in (4) + custom Forgiving
        expected = ['AlwaysCooperate', 'AlwaysDefect', 'TitForTat', 'GrimTrigger', 'ForgivingTitForTat']
        self.assertEqual(sorted(STRATEGY_REGISTRY.keys()), sorted(expected))
        # Verify instantiable + source comment in doc
        for name, cls in STRATEGY_REGISTRY.items():
            self.assertTrue(issubclass(cls, Strategy))
            instance = cls()
            self.assertIsInstance(instance, Strategy)

    def test_custom_strategy_forgiving_tit_for_tat(self):
        """Test custom strat from custom/ folder (ForgivingTitForTat)."""
        forgiver = ForgivingTitForTat()
        # Start C
        self.assertEqual(forgiver.decide([]), 'C')
        # Mirror
        self.assertEqual(forgiver.decide(['D']), 'D')
        # Forgive after two D's
        self.assertEqual(forgiver.decide(['D', 'D']), 'C')
        self.assertEqual(forgiver.decide(['C', 'D', 'D']), 'C')

    def test_always_cooperate(self):
        """AlwaysCooperate: always returns 'C' regardless of history."""
        self.assertEqual(self.always_coop.decide([]), 'C')
        self.assertEqual(self.always_coop.decide(['D', 'C', 'D']), 'C')
        self.assertEqual(self.always_coop.decide(['C'] * 10), 'C')

    def test_always_defect(self):
        """AlwaysDefect: always returns 'D' regardless of history."""
        self.assertEqual(self.always_defect.decide([]), 'D')
        self.assertEqual(self.always_defect.decide(['C', 'D']), 'D')
        self.assertEqual(self.always_defect.decide(['D'] * 5), 'D')

    def test_tit_for_tat(self):
        """TitForTat: starts with C, then mirrors opponent's last move."""
        # Empty history: cooperate first
        self.assertEqual(self.tit_for_tat.decide([]), 'C')
        # Mirror last
        self.assertEqual(self.tit_for_tat.decide(['C']), 'C')
        self.assertEqual(self.tit_for_tat.decide(['D']), 'D')
        self.assertEqual(self.tit_for_tat.decide(['C', 'D', 'C']), 'C')  # last='C'

    def test_grim_trigger(self):
        """GrimTrigger: C until any D seen, then permanent D."""
        # Initial: C
        self.assertEqual(self.grim_trigger.decide([]), 'C')
        self.assertEqual(self.grim_trigger.decide(['C', 'C']), 'C')
        # Once D seen: forever D
        self.assertEqual(self.grim_trigger.decide(['C', 'D']), 'D')
        self.assertEqual(self.grim_trigger.decide(['D']), 'D')
        # Stays D even after
        self.assertEqual(self.grim_trigger.decide(['C', 'D', 'C', 'C']), 'D')

    def test_abstract_base(self):
        """Strategy ABC: cannot instantiate directly (abstract)."""
        with self.assertRaises(TypeError):
            Strategy()  # abstractmethod

if __name__ == '__main__':
    unittest.main()
