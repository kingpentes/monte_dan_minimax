"""
Minimax algorithm with Alpha-Beta Pruning.
Supports switching between Static Evaluation and Monte Carlo Evaluation.
"""

import chess
import math
from .evaluator_static import evaluate_static
from .evaluator_mc import evaluate_mc

def minimax(board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool, use_mc=False, rollout_count=30):

    if depth == 0 or board.is_game_over():
        if use_mc:
            return evaluate_mc(board, rollout_count) * 1000 
        else:
            return evaluate_static(board)

    legal_moves = list(board.legal_moves)
    
    if maximizing:
        max_eval = -math.inf
        for move in legal_moves:
            board.push(move)
            eval_val = minimax(board, depth - 1, alpha, beta, False, use_mc, rollout_count)
            board.pop()
            max_eval = max(max_eval, eval_val)
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in legal_moves:
            board.push(move)
            eval_val = minimax(board, depth - 1, alpha, beta, True, use_mc, rollout_count)
            board.pop()
            min_eval = min(min_eval, eval_val)
            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval

def select_best_move(board: chess.Board, depth=3, use_mc=False, rollout_count=30):
    best_move = None
    max_eval = -math.inf
    min_eval = math.inf
    alpha = -math.inf
    beta = math.inf
    
    maximizing = board.turn == chess.WHITE
    legal_moves = list(board.legal_moves)
    
    # Simple move ordering: captures first could be added here for optimization
    # legal_moves.sort(key=...) 

    for move in legal_moves:
        board.push(move)
        eval_val = minimax(board, depth - 1, alpha, beta, not maximizing, use_mc, rollout_count)
        board.pop()
        
        if maximizing:
            if eval_val > max_eval:
                max_eval = eval_val
                best_move = move
            alpha = max(alpha, eval_val)
        else:
            if eval_val < min_eval:
                min_eval = eval_val
                best_move = move
            beta = min(beta, eval_val)
            
    return best_move
