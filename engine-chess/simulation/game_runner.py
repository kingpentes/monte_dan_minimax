"""
Runner for running multiple games and collecting aggregate metrics.
"""

from simulation.auto_vs_stockfish import play_vs_stockfish
from simulation.metrics import calculate_stats, calculate_winrate, save_summary_json
import chess
import json
import os

def run_experiment(n_games, stockfish_path, engine_depth, use_mc, rollout_count, output_file):
    """
    Runs N games against Stockfish and saves the results.
    """
    results = []
    all_move_times = []
    all_cp_losses = []
    all_matches = []
    
    print(f"Starting experiment: {n_games} games, Depth={engine_depth}, MC={use_mc}")
    
    for i in range(n_games):
        print(f"  Game {i+1}/{n_games}...")
        # Alternate colors to be fair
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
            all_cp_losses.extend(game_data.get("engine_cp_losses", []))
            all_matches.extend(game_data.get("engine_best_move_matches", []))
            
            avg_cp = calculate_stats(game_data.get("engine_cp_losses", []))[0]
            print(f"    Result: {game_data['result_score']}, Avg Time: {calculate_stats(game_data['engine_move_times'])[0]:.4f}s, Avg CP Loss: {avg_cp:.2f}")
        else:
            print("    Game failed (Stockfish error?)")

    avg_time, std_time = calculate_stats(all_move_times)
    avg_cp_loss, std_cp_loss = calculate_stats(all_cp_losses)
    match_rate = calculate_winrate(all_matches) # Reusing calculate_winrate for average
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
            "avg_cp_loss": avg_cp_loss,
            "std_cp_loss": std_cp_loss,
            "move_match_rate": match_rate,
            "total_moves": len(all_move_times)
        }
    }
    
    save_summary_json(summary, output_file)
    print(f"Experiment finished. Win Rate: {win_rate}, Avg Time: {avg_time:.4f}s")
    return summary

def run_h2h_experiment(n_games, depth, rollouts, output_file):
    """
    Runs a Head-to-Head experiment: Baseline vs Hybrid.
    Swaps colors every game.
    """
    from simulation.h2h import play_h2h_game
    
    results = {
        "Baseline": 0,
        "Hybrid": 0,
        "Draw": 0
    }
    
    games_data = []
    
    print(f"Starting H2H Experiment: {n_games} games, Depth={depth}, Rollouts={rollouts}")
    
    for i in range(n_games):
        # Swap colors: Even games (0, 2...) -> Baseline White. Odd games -> Baseline Black.
        baseline_is_white = (i % 2 == 0)
        
        print(f"  Game {i+1}/{n_games} ({'Baseline White' if baseline_is_white else 'Hybrid White'})...")
        
        game_data = play_h2h_game(depth, depth, rollouts, baseline_is_white)
        
        if game_data:
            winner = game_data["winner"]
            results[winner] += 1
            games_data.append(game_data)
            print(f"    Winner: {winner}")
            
    summary = {
        "config": {
            "n_games": n_games,
            "depth": depth,
            "rollouts": rollouts,
            "mode": "h2h"
        },
        "results": results,
        "games": games_data
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=4)
        
    return summary
