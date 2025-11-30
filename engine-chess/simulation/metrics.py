"""
Metrics helper functions for the chess engine experiment.
"""

import time
import json
import os
import statistics

def measure_move_time(func, *args, **kwargs):
    """
    Executes a function and returns (result, execution_time).
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time

def calculate_winrate(results):
    """
    Calculates winrate from a list of game results.
    results: List of tuples/dicts containing 'winner' ('white', 'black', 'draw').
    Assumes engine is always one color or tracks 'engine_win'.
    
    For simplicity, let's assume results is a list of scores for the engine:
    1.0 (win), 0.5 (draw), 0.0 (loss).
    """
    if not results:
        return 0.0
    return sum(results) / len(results)

def save_summary_json(results, filepath):
    """
    Saves the experiment summary to a JSON file.
    results: Dict containing experiment data.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=4)

def calculate_stats(move_times):
    """
    Returns mean and stdev of move times.
    """
    if not move_times:
        return 0.0, 0.0
    return statistics.mean(move_times), statistics.stdev(move_times) if len(move_times) > 1 else 0.0
