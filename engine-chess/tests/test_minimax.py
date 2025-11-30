"""
Tests for Minimax and Static Evaluation.
"""

import unittest
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chess
from minimax.evaluator_static import evaluate_static
from minimax.minimax_ab import minimax, select_best_move

class TestMinimax(unittest.TestCase):
    def test_static_eval_initial(self):
        board = chess.Board()
        score = evaluate_static(board)
        self.assertEqual(score, 0, "Initial position should be equal")

    def test_static_eval_material_advantage(self):
        board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        # Remove black pawn
        board.remove_piece_at(chess.A7)
        score = evaluate_static(board)
        self.assertGreater(score, 0, "White should be winning with extra pawn")

    def test_minimax_mate_in_one(self):
        # White to move and mate
        board = chess.Board("7k/R7/8/8/8/8/8/7K w - - 0 1")
        # This is not mate in 1, let's find a real mate in 1
        # King on h8, Rook on a7. King on h1.
        # If Rook moves to h7, it's check.
        # Let's use a simpler one.
        # White King e1, White Rook a1. Black King e8.
        # Back rank mate: 4k3/R7/8/8/8/8/8/4K3 w - - 0 1 -> Ra8#
        board = chess.Board("4k3/R7/8/8/8/8/8/4K3 w - - 0 1")
        
        best_move = select_best_move(board, depth=1)
        self.assertEqual(best_move, chess.Move.from_uci("a7a8"), "Should find mate in 1")

if __name__ == "__main__":
    unittest.main()
