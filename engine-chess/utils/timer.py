"""
Timer utility for measuring execution time.
"""

import time
from contextlib import contextmanager

@contextmanager
def measure_time(name):
    start = time.time()
    yield
    end = time.time()
    print(f"{name} took {end - start:.4f} seconds")
