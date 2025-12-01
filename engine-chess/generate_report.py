"""
Script to generate comparison charts and paper-ready tables from experiment results.
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
CHARTS_DIR = os.path.join(RESULTS_DIR, "charts")
BASELINE_FILE = os.path.join(RESULTS_DIR, "baseline_summary.json")
HYBRID_FILE = os.path.join(RESULTS_DIR, "hybrid_summary.json")
OUTPUT_TABLE_FILE = os.path.join(RESULTS_DIR, "paper_table.md")

def load_summary(filepath):
    """Load JSON summary file."""
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return None
    with open(filepath, 'r') as f:
        return json.load(f)

def generate_comparison_charts(baseline, hybrid):
    """Generate comparison charts for Time and Score."""
    os.makedirs(CHARTS_DIR, exist_ok=True)
    
    # Data preparation
    labels = ['Baseline (Minimax)', 'Hybrid (MC)']
    
    # Time Data
    times = [
        baseline['metrics']['avg_move_time'],
        hybrid['metrics']['avg_move_time']
    ]
    std_devs = [
        baseline['metrics']['std_move_time'],
        hybrid['metrics']['std_move_time']
    ]
    
    # Score Data (Win Rate)
    scores = [
        baseline['metrics']['win_rate'],
        hybrid['metrics']['win_rate']
    ]
    
    # Accuracy Data
    cp_losses = [
        baseline['metrics'].get('avg_cp_loss', 0),
        hybrid['metrics'].get('avg_cp_loss', 0)
    ]
    match_rates = [
        baseline['metrics'].get('move_match_rate', 0),
        hybrid['metrics'].get('move_match_rate', 0)
    ]
    
    # 1. Time Comparison Chart
    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, times, yerr=std_devs, capsize=10, color=['#3498db', '#e74c3c'], alpha=0.8)
    
    # Add value labels on top
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}s',
                ha='center', va='bottom')
                
    plt.ylabel('Average Move Time (seconds)')
    plt.title('Performance Comparison: Move Time')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    output_path = os.path.join(CHARTS_DIR, 'comparison_time.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Generated chart: {output_path}")
    
    # 2. Score Comparison Chart
    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, scores, color=['#2ecc71', '#f1c40f'], alpha=0.8)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom')
                
    plt.ylabel('Average Score (Win Rate)')
    plt.ylim(0, 1.1)  # Score is 0-1
    plt.title('Performance Comparison: Win Rate')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    output_path = os.path.join(CHARTS_DIR, 'comparison_score.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Generated chart: {output_path}")

    # 3. CP Loss Comparison Chart
    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, cp_losses, color=['#9b59b6', '#8e44ad'], alpha=0.8)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom')
                
    plt.ylabel('Average Centipawn Loss')
    plt.title('Performance Comparison: Accuracy (Lower is Better)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    output_path = os.path.join(CHARTS_DIR, 'comparison_cpl.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Generated chart: {output_path}")

    # 4. Match Rate Comparison Chart
    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, match_rates, color=['#1abc9c', '#16a085'], alpha=0.8)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2%}',
                ha='center', va='bottom')
                
    plt.ylabel('Best Move Match Rate')
    plt.ylim(0, 1.0)
    plt.title('Performance Comparison: Move Matching')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    output_path = os.path.join(CHARTS_DIR, 'comparison_match_rate.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Generated chart: {output_path}")

def generate_markdown_table(baseline, hybrid):
    """Generate a Markdown table for the paper."""
    
    # Extract data
    b_conf = baseline['config']
    b_met = baseline['metrics']
    h_conf = hybrid['config']
    h_met = hybrid['metrics']
    
    table = f"""# Experiment Results

| Metric | Baseline (Minimax) | Hybrid (Minimax + MC) |
| :--- | :--- | :--- |
| **Configuration** | Depth={b_conf['depth']} | Depth={h_conf['depth']}, Rollouts={h_conf['rollout_count']} |
| **Games Played** | {b_conf['n_games']} | {h_conf['n_games']} |
| **Win Rate (Score)** | {b_met['win_rate']:.2f} | {h_met['win_rate']:.2f} |
| **Avg Move Time** | {b_met['avg_move_time']:.4f} s | {h_met['avg_move_time']:.4f} s |
| **Avg CP Loss** | {b_met.get('avg_cp_loss', 0):.2f} | {h_met.get('avg_cp_loss', 0):.2f} |
| **Best Move Match** | {b_met.get('move_match_rate', 0):.2%} | {h_met.get('move_match_rate', 0):.2%} |
| **Total Moves** | {b_met['total_moves']} | {h_met['total_moves']} |

*Note: Win Rate is calculated as Average Score (1.0 for Win, 0.5 for Draw, 0.0 for Loss). CP Loss is Centipawn Loss (lower is better).*
"""
    
    with open(OUTPUT_TABLE_FILE, 'w') as f:
        f.write(table)
        
    print(f"Generated table: {OUTPUT_TABLE_FILE}")
    return table

def main():
    print("Loading results...")
    baseline = load_summary(BASELINE_FILE)
    hybrid = load_summary(HYBRID_FILE)
    
    if not baseline or not hybrid:
        print("Error: Could not load summary files. Make sure you have run both experiments.")
        return
        
    print("Generating visualizations...")
    generate_comparison_charts(baseline, hybrid)
    
    print("Generating paper table...")
    table = generate_markdown_table(baseline, hybrid)
    
    print("\n--- Generated Table Preview ---\n")
    print(table)

if __name__ == "__main__":
    main()
