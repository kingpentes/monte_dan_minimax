"""
Debug script to check imports.
"""
import sys
import os

print("Current working directory:", os.getcwd())
print("sys.path:", sys.path)

try:
    import minimax
    print("Successfully imported minimax package")
    import minimax.minimax_ab
    print("Successfully imported minimax.minimax_ab")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")

import unittest
# Add current directory to sys.path explicitly if not present
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
