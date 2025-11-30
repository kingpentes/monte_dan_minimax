"""
Module to run games against Stockfish.
"""

import chess
import chess.engine
import time
from ..minimax.minimax_ab import select_best_move
from .metrics import measure_move_time

def play_vs_stockfish(stockfish_path, engine_depth, use_mc, rollout_count, engine_color=chess.WHITE, time_limit=0.1):
    """
    Plays a single game: Custom Engine vs Stockfish.
    
    Args:
        stockfish_path: Path to Stockfish executable.
        engine_depth: Depth for custom engine.
        use_mc: Boolean, use Monte Carlo evaluation.
        rollout_count: Number of rollouts for MC.
        engine_color: chess.WHITE or chess.BLACK.
        time_limit: Time limit for Stockfish per move.
        
    Returns:
        dict: Game result and metrics.
    """
    board = chess.Board()
    engine_move_times = []
    
    try:
        # Use simple engine for Stockfish
        # Note: User must provide valid path.
        transport, stockfish = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    except FileNotFoundError:
        print(f"Stockfish not found at {stockfish_path}")
        return None

    try:
        while not board.is_game_over():
            if board.turn == engine_color:
                # Custom Engine Move
                move, duration = measure_move_time(
                    select_best_move, 
                    board, 
                    depth=engine_depth, 
                    use_mc=use_mc, 
                    rollout_count=rollout_count
                )
                engine_move_times.append(duration)
                if move is None:
                    # Should not happen unless no legal moves (game over check handles this)
                    break
                board.push(move)
            else:
                # Stockfish Move
                result = stockfish.play(board, chess.engine.Limit(time=time_limit))
                board.push(result.move)
                
    finally:
        stockfish.quit()
        
    # Determine result
    result_score = 0.0 # 0 for loss, 0.5 draw, 1 win (from engine perspective)
    outcome = board.outcome()
    
    if outcome:
        if outcome.winner == engine_color:
            result_score = 1.0
        elif outcome.winner is None:
            result_score = 0.5
        else:
            result_score = 0.0
            
    return {
        "result_score": result_score,
        "engine_move_times": engine_move_times,
        "fen": board.fen(),
        "termination": str(outcome.termination) if outcome else "Unknown"
    }
