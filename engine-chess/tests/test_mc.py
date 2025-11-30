"""
Tests for Monte Carlo Evaluation.
"""

import unittest
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chess
from minimax.evaluator_mc import evaluate_mc, simulate_random

class TestMC(unittest.TestCase):
    def test_simulate_random_range(self):
        board = chess.Board()
        score = simulate_random(board, max_steps=10)
        self.assertTrue(-1.0 <= score <= 1.0, "Score should be between -1 and 1")

    def test_evaluate_mc_range(self):
        board = chess.Board()
        score = evaluate_mc(board, rollout_count=5)
        self.assertTrue(-1.0 <= score <= 1.0, "Average score should be between -1 and 1")

if __name__ == "__main__":
    unittest.main()
