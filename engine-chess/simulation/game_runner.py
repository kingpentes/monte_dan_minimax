"""
Runner for running multiple games and collecting aggregate metrics.
"""

from .auto_vs_stockfish import play_vs_stockfish
from .metrics import calculate_stats, calculate_winrate, save_summary_json
import chess

def run_experiment(n_games, stockfish_path, engine_depth, use_mc, rollout_count, output_file):
    """
    Runs N games against Stockfish and saves the results.
    """
    results = []
    all_move_times = []
    
    print(f"Starting experiment: {n_games} games, Depth={engine_depth}, MC={use_mc}")
    
    for i in range(n_games):
        print(f"  Game {i+1}/{n_games}...")
        # Alternate colors? Or fixed? Let's fix engine as White for consistency in this simplified test
        # Or alternate to be fair. Let's alternate.
        engine_color = chess.WHITE if i % 2 == 0 else chess.BLACK
        
        game_data = play_vs_stockfish(
            stockfish_path, 
            engine_depth, 
            use_mc, 
            rollout_count, 
            engine_color=engine_color
        )
        
        if game_data:
            results.append(game_data["result_score"])
            all_move_times.extend(game_data["engine_move_times"])
            print(f"    Result: {game_data['result_score']}, Avg Time: {calculate_stats(game_data['engine_move_times'])[0]:.4f}s")
        else:
            print("    Game failed (Stockfish error?)")

    avg_time, std_time = calculate_stats(all_move_times)
    win_rate = calculate_winrate(results)
    
    summary = {
        "config": {
            "n_games": n_games,
            "depth": engine_depth,
            "use_mc": use_mc,
            "rollout_count": rollout_count
        },
        "metrics": {
            "win_rate": win_rate,
            "avg_move_time": avg_time,
            "std_move_time": std_time,
            "total_moves": len(all_move_times)
        }
    }
    
    save_summary_json(summary, output_file)
    print(f"Experiment finished. Win Rate: {win_rate}, Avg Time: {avg_time:.4f}s")
    return summary
