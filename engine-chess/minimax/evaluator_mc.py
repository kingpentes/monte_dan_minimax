"""
Monte Carlo evaluator using random rollouts.
"""

import chess
import random

def simulate_random(board: chess.Board, max_steps=20) -> float:
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
    return 0.0

def evaluate_mc(board: chess.Board, rollout_count=30) -> float:
    total_score = 0.0
    for _ in range(rollout_count):
        total_score += simulate_random(board)
    
    return total_score / rollout_count
