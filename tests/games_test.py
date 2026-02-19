import unittest
import ast
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from games import Game

class TestGame(unittest.TestCase):
    """Tests for games.py: config parsing, payoffs, validation."""

    def setUp(self):
        """Setup PD game from config dict (mimicking config.json)."""
        self.pd_config = {
            "payoffs": {
                "('C', 'C')": [3, 3],
                "('C', 'D')": [0, 5],
                "('D', 'C')": [5, 0],
                "('D', 'D')": [1, 1]
            },
            "valid_actions": ["C", "D"]
        }
        self.game = Game.from_config(self.pd_config)

    def test_from_config_parsing(self):
        """Test config parsing with ast.literal_eval for string tuple keys."""
        self.assertIsInstance(self.game, Game)
        # Verify string keys parsed to tuples
        self.assertIn(('C', 'C'), self.game.payoffs)
        self.assertEqual(self.game.payoffs[('C', 'C')], (3, 3))
        self.assertEqual(self.game.payoffs[('D', 'C')], (5, 0))
        self.assertEqual(self.game.valid_actions, ["C", "D"])

    def test_get_payoff_valid(self):
        """Test payoff matrix for all PD outcomes."""
        self.assertEqual(self.game.get_payoff('C', 'C'), (3, 3))
        self.assertEqual(self.game.get_payoff('C', 'D'), (0, 5))
        self.assertEqual(self.game.get_payoff('D', 'C'), (5, 0))
        self.assertEqual(self.game.get_payoff('D', 'D'), (1, 1))

    def test_invalid_moves(self):
        """Test validation raises ValueError for invalid moves (edge case)."""
        with self.assertRaises(ValueError) as cm:
            self.game.get_payoff('X', 'C')
        self.assertIn("Invalid move: X", str(cm.exception))

        with self.assertRaises(ValueError):
            self.game.validate_move('')

        with self.assertRaises(ValueError):
            self.game.get_payoff('C', 'Invalid')

    def test_validate_move(self):
        """Explicit test for validate_move method."""
        # Valid should not raise
        self.game.validate_move('C')
        self.game.validate_move('D')
        # Invalid
        with self.assertRaises(ValueError):
            self.game.validate_move('Cooperate')

    def test_new_games_config_parsing(self):
        """Test Hawk-Dove and Stag Hunt from config (desc, payoffs, valid_actions order for mapping)."""
        # HD config snippet
        hd_config = {
            "payoffs": {
                "('Dove', 'Dove')": [2, 2],
                "('Dove', 'Hawk')": [1, 3],
                "('Hawk', 'Dove')": [3, 1],
                "('Hawk', 'Hawk')": [0, 0]
            },
            "valid_actions": ["Dove", "Hawk"],  # [0]=coop-like, [1]=defect-like
            "description": "Hawk-Dove test"
        }
        hd_game = Game.from_config(hd_config)
        self.assertEqual(hd_game.description, "Hawk-Dove test")
        self.assertEqual(hd_game.valid_actions, ["Dove", "Hawk"])
        self.assertEqual(hd_game.payoffs[('Dove', 'Hawk')], (1, 3))

        # SH similar
        sh_config = {
            "payoffs": {
                "('Stag', 'Stag')": [5, 5],
                "('Stag', 'Hare')": [0, 3],
                "('Hare', 'Stag')": [3, 0],
                "('Hare', 'Hare')": [3, 3]
            },
            "valid_actions": ["Stag", "Hare"],
            "description": "Stag Hunt test"
        }
        sh_game = Game.from_config(sh_config)
        self.assertEqual(sh_game.valid_actions[0], "Stag")  # coop-like
        self.assertEqual(sh_game.get_payoff('Stag', 'Hare'), (0, 3))

    def test_game_description_fallback(self):
        """Test desc from config or fallback; keeps generic."""
        no_desc_config = {"payoffs": {"('X', 'Y')": [1, 1]}, "valid_actions": ["X", "Y"]}
        g = Game.from_config(no_desc_config)
        self.assertIn("Game payoff matrix", g.description)

if __name__ == '__main__':
    unittest.main()
