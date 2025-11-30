"""
Chart generation module for chess engine experiments.
"""

import matplotlib.pyplot as plt
import os

def generate_charts(summary, output_dir):
    """
    Generates charts based on the experiment summary.
    summary: Dict containing experiment results.
    output_dir: Directory to save the charts.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract data
    config = summary.get("config", {})
    metrics = summary.get("metrics", {})
    
    # 1. Win Rate Chart (Pie Chart)
    # Since we only have a single win rate, maybe a bar chart comparing to 1.0?
    # Or if we had multiple experiments, we could compare.
    # For a single run, let's just visualize the Win/Loss/Draw if we had detailed results.
    # But summary only has win_rate.
    # Let's assume win_rate is % wins. 
    # Actually, win_rate in metrics.py was sum(scores)/len.
    # Score: 1.0 win, 0.5 draw, 0.0 loss.
    # So win_rate is average score.
    
    # Let's just plot the Average Move Time for now as a bar chart
    # to show the performance.
    
    plt.figure(figsize=(6, 4))
    plt.bar(['Avg Move Time'], [metrics['avg_move_time']], yerr=[metrics['std_move_time']], capsize=10)
    plt.ylabel('Time (s)')
    plt.title(f"Performance (Depth {config.get('depth')}, MC={config.get('use_mc')})")
    plt.savefig(os.path.join(output_dir, 'move_time.png'))
    plt.close()
    
    print(f"Charts saved to {output_dir}")
