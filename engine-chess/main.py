"""
Entry point for the Chess Engine project.
"""

import argparse
import os
from simulation.game_runner import run_experiment

def main():
    parser = argparse.ArgumentParser(description="Chess Engine Experiment Runner")
    parser.add_argument("--stockfish", type=str, required=True, help="Path to Stockfish executable")
    parser.add_argument("--games", type=int, default=10, help="Number of games to run")
    parser.add_argument("--depth", type=int, default=3, help="Search depth for engine")
    parser.add_argument("--mode", type=str, choices=["minimax", "hybrid"], default="minimax", help="Engine mode")
    parser.add_argument("--rollouts", type=int, default=30, help="Number of MC rollouts (hybrid mode)")
    parser.add_argument("--output", type=str, default="results/summary.json", help="Output file for summary")

    args = parser.parse_args()

    use_mc = (args.mode == "hybrid")
    
    print(f"Running Experiment: Mode={args.mode}, Games={args.games}, Depth={args.depth}")
    
    summary = run_experiment(
        n_games=args.games,
        stockfish_path=args.stockfish,
        engine_depth=args.depth,
        use_mc=use_mc,
        rollout_count=args.rollouts,
        output_file=args.output
    )
    
    # Generate charts
    from simulation.charts import generate_charts
    charts_dir = os.path.join(os.path.dirname(args.output), "charts")
    generate_charts(summary, charts_dir)

if __name__ == "__main__":
    main()
