"""
Monte Carlo evaluator using random rollouts.
"""

import chess
import random

def simulate_random(board: chess.Board, max_steps=40) -> float:
    """
    Simulates a random game from the current position up to max_steps.
    Returns:
        1.0 if White wins
        -1.0 if Black wins
        0.0 for Draw
        Static evaluation (normalized) if max_steps reached without game over.
    """
    temp_board = board.copy()
    steps = 0
    
    while not temp_board.is_game_over() and steps < max_steps:
        legal_moves = list(temp_board.legal_moves)
        if not legal_moves:
            break
        move = random.choice(legal_moves)
        temp_board.push(move)
        steps += 1

    if temp_board.is_game_over():
        result = temp_board.result()
        if result == "1-0":
            return 1.0
        elif result == "0-1":
            return -1.0
        else:
            return 0.0
            
    # If not game over, return a small heuristic or 0
    # For simplicity in this hybrid model, we can return 0 or a very simple material check
    # But strictly following "Return nilai float -1 sampai 1", 0.0 is safe for unfinished.
    return 0.0

def evaluate_mc(board: chess.Board, rollout_count=100) -> float:
    """
    Runs multiple random simulations and returns the average score.
    Range: -1.0 (Black wins all) to 1.0 (White wins all).
    """
    total_score = 0.0
    for _ in range(rollout_count):
        total_score += simulate_random(board)
    
    return total_score / rollout_count
