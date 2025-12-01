"""
Module to run Head-to-Head games between Baseline (Minimax) and Hybrid (Minimax + MC) engines.
"""

import chess
import time
from minimax.minimax_ab import select_best_move
from simulation.metrics import measure_move_time

def play_h2h_game(baseline_depth, hybrid_depth, hybrid_rollouts, baseline_is_white=True):
    """
    Plays a single game: Baseline vs Hybrid.
    
    Args:
        baseline_depth: Depth for Baseline engine.
        hybrid_depth: Depth for Hybrid engine.
        hybrid_rollouts: Rollouts for Hybrid engine.
        baseline_is_white: True if Baseline plays White, False if Black.
        
    Returns:
        dict: Game result and metrics.
    """
    board = chess.Board()
    baseline_moves = []
    hybrid_moves = []
    baseline_times = []
    hybrid_times = []
    
    baseline_color = chess.WHITE if baseline_is_white else chess.BLACK
    hybrid_color = chess.BLACK if baseline_is_white else chess.WHITE
    
    outcome = None
    
    try:
        while not board.is_game_over():
            if board.turn == baseline_color:
                # Baseline Move (Minimax only)
                move, duration = measure_move_time(
                    select_best_move, 
                    board, 
                    depth=baseline_depth, 
                    use_mc=False
                )
                baseline_times.append(duration)
                baseline_moves.append(move.uci() if move else "None")
            else:
                # Hybrid Move (Minimax + MC)
                move, duration = measure_move_time(
                    select_best_move, 
                    board, 
                    depth=hybrid_depth, 
                    use_mc=True, 
                    rollout_count=hybrid_rollouts
                )
                hybrid_times.append(duration)
                hybrid_moves.append(move.uci() if move else "None")
                
            if move is None:
                break
                
            board.push(move)
            
        outcome = board.outcome()
        
    except Exception as e:
        print(f"Game error: {e}")
        return None

    # Determine winner
    winner = "Draw"
    if outcome.winner == baseline_color:
        winner = "Baseline"
    elif outcome.winner == hybrid_color:
        winner = "Hybrid"
        
    return {
        "winner": winner,
        "baseline_is_white": baseline_is_white,
        "baseline_times": baseline_times,
        "hybrid_times": hybrid_times,
        "fen": board.fen(),
        "termination": str(outcome.termination) if outcome else "Unknown",
        "moves": [m.uci() for m in board.move_stack]
    }
