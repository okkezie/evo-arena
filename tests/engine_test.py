import unittest
import os
import sys
import json
from unittest.mock import patch, mock_open

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine import GameTheoryEngine
from games import Game
# STRATEGY_REGISTRY imported but unused; kept for potential registry tests

class TestGameTheoryEngine(unittest.TestCase):
    """Tests for engine.py: config load, play_game in all modes (using mocks for human input)."""

    def setUp(self):
        """Setup engine with config (mocked for isolation)."""
        # Mock config.json content to avoid file dep in tests
        self.mock_config = {
            "games": {
                "PD": {
                    "payoffs": {
                        "('C', 'C')": [3, 3],
                        "('C', 'D')": [0, 5],
                        "('D', 'C')": [5, 0],
                        "('D', 'D')": [1, 1]
                    },
                    "valid_actions": ["C", "D"]
                }
            },
            "strategies": ["AlwaysCooperate", "AlwaysDefect", "TitForTat", "GrimTrigger"],
            "default_rounds": 2  # Small for fast tests
        }
        # Patch open and json.load for config
        self.config_patcher = patch('builtins.open', mock_open(read_data=json.dumps(self.mock_config)))
        self.mock_file = self.config_patcher.start()
        self.engine = GameTheoryEngine(config_path='config.json')  # uses mock

    def tearDown(self):
        """Stop patchers."""
        self.config_patcher.stop()

    def test_config_load(self):
        """Test engine init loads games, strategies, default_rounds from config."""
        self.assertIn('PD', self.engine.games)
        # Verify it's a Game instance (from games.py)
        self.assertIsInstance(self.engine.games['PD'], Game)
        self.assertEqual(self.engine.strategy_names, self.mock_config['strategies'])
        self.assertEqual(self.engine.default_rounds, 2)

    @patch('engine.GameTheoryEngine._get_human_move')
    def test_play_game_auto_mode(self, mock_human):
        """Test auto mode (0): AI vs AI, no human input."""
        # Mocks not called for AI-only
        result = self.engine.play_game(
            game_name='PD',
            mode=0,
            strat1_name='TitForTat',
            strat2_name='AlwaysDefect',
            rounds=2
        )
        self.assertIn('scores', result)
        self.assertIn('moves', result)
        self.assertEqual(len(result['moves']), 2)  # rounds=2
        # TitForTat vs AlwaysDefect: P1 starts C, then mirrors D -> C then D; P2 always D
        # Expected moves: [('C','D'), ('D','D')]
        self.assertEqual(result['moves'][0], ('C', 'D'))
        self.assertEqual(result['moves'][1], ('D', 'D'))
        # Payoffs: (0+1, 5+1) = (1,6)
        self.assertEqual(result['scores'], (1, 6))
        # Ensure no human input called
        mock_human.assert_not_called()

    @patch('engine.GameTheoryEngine._get_human_move')
    def test_play_game_single_mode(self, mock_human):
        """Test single mode (1): human P1 vs AI P2. Mock human inputs."""
        # Mock human moves for P1: ['C', 'D'] over 2 rounds
        mock_human.side_effect = ['C', 'D']
        result = self.engine.play_game(
            game_name='PD',
            mode=1,
            strat2_name='AlwaysCooperate',  # AI P2 always C
            rounds=2
        )
        # Human P1 vs Always C: moves [('C','C'), ('D','C')], payoffs (3,3) + (5,0) = (8,3)
        self.assertEqual(result['scores'], (8, 3))
        self.assertEqual(result['moves'], [('C', 'C'), ('D', 'C')])
        # _get_human_move called twice (once per round)
        self.assertEqual(mock_human.call_count, 2)

    @patch('engine.GameTheoryEngine._get_human_move')
    def test_play_game_multi_mode(self, mock_human):
        """Test multi mode (2): human vs human. Mock alternating inputs."""
        # For 1 round (override default=2? use 1), but use default=2: P1,P2,P1,P2 -> 4 calls
        # Set rounds=1 for simplicity
        mock_human.side_effect = ['C', 'D', 'D', 'C']  # but for rounds=1: only 2 needed
        result = self.engine.play_game(
            game_name='PD',
            mode=2,
            rounds=1  # P1 then P2 input
        )
        # Moves: P1=C, P2=D -> payoff (0,5)
        self.assertEqual(result['moves'], [('C', 'D')])
        self.assertEqual(result['scores'], (0, 5))
        # Called 2 times for 1 round
        self.assertEqual(mock_human.call_count, 2)

    @patch('engine.GameTheoryEngine._get_human_move')
    def test_invalid_modes_and_strats(self, mock_human):
        """Test error handling: invalid mode, missing strats (edge cases)."""
        # Invalid mode
        with self.assertRaises(ValueError) as cm:
            self.engine.play_game('PD', mode=99)
        self.assertIn("Mode must be", str(cm.exception))

        # Auto mode missing strat
        with self.assertRaises(ValueError) as cm:
            self.engine.play_game('PD', mode=0, strat1_name='TitForTat')  # missing strat2
        self.assertIn("requires both", str(cm.exception))

        # Single mode missing strat2
        with self.assertRaises(ValueError):
            self.engine.play_game('PD', mode=1)

        # Unknown game
        with self.assertRaises(ValueError):
            self.engine.play_game('UnknownGame', mode=0, strat1_name='TitForTat', strat2_name='AlwaysDefect')

    def test_strategy_errors(self):
        """Test unknown strategy raises in _get_strategy."""
        with self.assertRaises(ValueError) as cm:
            self.engine.play_game('PD', mode=0, strat1_name='NonExistent', strat2_name='TitForTat')
        self.assertIn("Unknown strategy", str(cm.exception))

    def test_noisy_decide(self):
        """Test noise utility: flips move with prob, within 0-0.2."""
        strat = self.engine._get_strategy('AlwaysCooperate')  # always 'C'
        # noise=0: always 'C'
        self.assertEqual(self.engine._noisy_decide(strat, []), 'C')
        # With noise=0.2: may flip to 'D', but probabilistic; test range
        # For determinism in test, mock random
        with patch('engine.random.random', return_value=0.3):  # >0.2 no flip
            self.assertEqual(self.engine._noisy_decide(strat, [], noise=0.2), 'C')
        with patch('engine.random.random', return_value=0.1):  # < flip to 'D'
            self.assertEqual(self.engine._noisy_decide(strat, [], noise=0.2), 'D')
        # Invalid noise
        with self.assertRaises(ValueError):
            self.engine._noisy_decide(strat, [], noise=0.3)

    @patch('engine.GameTheoryEngine._play_match')
    def test_repeated_match(self, mock_match):
        """Test single repeated match feature (wraps _play_match)."""
        mock_match.return_value = {"scores": (300, 100), "strats": ("TitForTat", "AlwaysDefect")}
        result = self.engine.repeated_match(strat1_name="TitForTat", strat2_name="AlwaysDefect", rounds=100, noise=0.01)
        mock_match.assert_called_once()
        self.assertEqual(result["scores"], (300, 100))

    @patch('engine.GameTheoryEngine._play_match')
    def test_round_robin_tournament(self, mock_match):
        """Test tournament: calls _play_match for all pairs, produces ranking."""
        # Mock returns for simplicity (e.g., always 300-0 for first strat)
        mock_match.return_value = {"scores": (300, 100)}
        result = self.engine.round_robin_tournament(rounds_per_match=10, repeats=1, noise=0)
        self.assertIn("total_scores", result)
        self.assertIn("ranking", result)
        # With 4 strats, expect ranking dict
        self.assertEqual(len(result["total_scores"]), 4)
        # Called 4*4 =16 times (full matrix)
        self.assertEqual(mock_match.call_count, 16)

    @patch('matplotlib.pyplot.show')
    @patch('engine.GameTheoryEngine._play_match')
    def test_evolutionary_simulation(self, mock_match, mock_plot):
        """Test DEAP evo: runs GA, stats, freqs, plot; small params for speed."""
        # Mock match returns positive score
        mock_match.return_value = {"scores": (100, 0)}
        result = self.engine.evolutionary_simulation(
            pop_size=20, generations=2, rounds_per_match=10, noise=0, plot=True
        )
        self.assertIn("winner", result)
        self.assertIn("final_ranking", result)
        self.assertTrue(mock_plot.called)  # plot attempted
        # _play_match called multiple times in fitness evals
        self.assertGreater(mock_match.call_count, 0)

if __name__ == '__main__':
    unittest.main()
