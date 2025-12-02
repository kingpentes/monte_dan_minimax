"""
Module to run games against Stockfish.
"""

import chess
import chess.engine
import time
from minimax.minimax_ab import select_best_move
from simulation.metrics import measure_move_time

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
    engine_cp_losses = []
    engine_best_move_matches = []
    
    try:
        if stockfish_path == "mock":
            class MockEngine:
                def play(self, board, limit):
                    import random
                    if not list(board.legal_moves):
                         return chess.engine.PlayResult(None, None)
                    move = random.choice(list(board.legal_moves))
                    return chess.engine.PlayResult(move, None)
                def quit(self):
                    pass
            stockfish = MockEngine()
        else:
            # Use simple engine for Stockfish
            # Note: User must provide valid path.
            stockfish = chess.engine.SimpleEngine.popen_uci(stockfish_path)
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
                print(f"\r    Move {board.fullmove_number} (Engine): {duration:.2f}s", end="", flush=True)
                engine_move_times.append(duration)
                if move is None:
                    # Should not happen unless no legal moves (game over check handles this)
                    break
                
                # Analyze Move (if Stockfish is available and not mock)
                if stockfish and not isinstance(stockfish, type) and hasattr(stockfish, 'analyse'):
                    try:
                        # 1. Analyze position to get Best Move & Score
                        limit = chess.engine.Limit(time=0.1)
                        info = stockfish.analyse(board, limit, multipv=1)
                        
                        # Handle case where info might be a list (though usually it's a dict for multipv=1)
                        if isinstance(info, list):
                            info = info[0]
                            
                        best_move = info["pv"][0]
                        best_score = info["score"].relative.score(mate_score=10000)
                        
                        # 2. Analyze Chosen Move
                        info_chosen = stockfish.analyse(board, limit, root_moves=[move])
                        
                        if isinstance(info_chosen, list):
                            info_chosen = info_chosen[0]
                            
                        chosen_score = info_chosen["score"].relative.score(mate_score=10000)
                        
                        # Calculate Metrics
                        cp_loss = max(0, best_score - chosen_score)
                        is_match = (move == best_move)
                        
                        engine_cp_losses.append(cp_loss)
                        engine_best_move_matches.append(1 if is_match else 0)
                        
                        # print(f"    Move Analysis: CP Loss={cp_loss}, Match={is_match}")
                        
                    except Exception as e:
                        print(f"Analysis failed: {e} (Type: {type(info) if 'info' in locals() else 'unknown'})")
                        
                board.push(move)
            else:
                # Stockfish Move
                result = stockfish.play(board, chess.engine.Limit(time=time_limit))
                board.push(result.move)
                
    finally:
        print() # Newline after progress bar
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
        "result_score": result_score,
        "engine_move_times": engine_move_times,
        "engine_cp_losses": engine_cp_losses,
        "engine_best_move_matches": engine_best_move_matches,
        "fen": board.fen(),
        "fen": board.fen(),
        "termination": str(outcome.termination) if outcome else "Unknown"
    }
