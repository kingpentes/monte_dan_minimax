# Code Quality Review Report

**Project**: Chess Engine (Minimax + Alpha-Beta + Monte Carlo)  
**Date**: 30 November 2025  
**Reviewer**: AI Code Analyzer

---

## 📊 Overall Assessment

**Overall Grade**: **B+ (Good/Very Good)**

### Summary
Kode sudah terstruktur dengan baik dan mengikuti sebagian besar best practices Python. Namun ada beberapa area yang bisa ditingkatkan untuk production-readiness.

---

## ✅ Strengths (Yang Sudah Baik)

### 1. **Project Structure** ⭐⭐⭐⭐⭐
- Modular design yang jelas (separation of concerns)
- Package organization yang baik
- Naming conventions konsisten (snake_case)
- File structure sesuai dengan konsep.md

### 2. **Type Hints** ⭐⭐⭐⭐
- Sebagian besar fungsi sudah menggunakan type hints
- Contoh: `evaluate_static(board: chess.Board) -> int`
- Membantu IDE autocomplete dan catches bugs early

### 3. **Documentation** ⭐⭐⭐⭐
- Docstrings tersedia di fungsi-fungsi utama
- Module-level docstrings present
- Parameter descriptions clear

### 4. **Algorithm Correctness** ⭐⭐⭐⭐⭐
- Minimax implementation benar
- Alpha-beta pruning logic sound
- Monte Carlo rollout valid

---

## ⚠️ Issues & Recommendations

### 🔴 **CRITICAL Issues**

#### 1. **Magic Number Scaling (minimax_ab.py:35)**
```python
return evaluate_mc(board, rollout_count) * 1000  # Scale up to match static magnitude
```
**Problem**: 
- Scaling factor 1000 adalah arbitrary/magic number
- Menyebabkan MC scores tidak comparable dengan static eval
- Comment sendiri menyatakan "might be tricky if not careful"

**Fix**:
```python
# Define as constant at module level
MC_SCALING_FACTOR = 1000  # To match static eval range (±100-900)

def minimax(...):
    if use_mc:
        return evaluate_mc(board, rollout_count) * MC_SCALING_FACTOR
```

**Better Solution**: Normalize static eval to [-1, 1] range instead

---

#### 2. **No Error Handling for Empty Move List (minimax_ab.py:39-97)**
```python
legal_moves = list(board.legal_moves)
# No check if legal_moves is empty
for move in legal_moves:  # Empty loop if no moves
```

**Problem**: 
- Jika `legal_moves` kosong (seharusnya tidak terjadi karena `is_game_over()` check)
- `max_eval` tetap `-math.inf`, `min_eval` tetap `math.inf`
- Return value undefined behavior

**Fix**:
```python
legal_moves = list(board.legal_moves)
if not legal_moves:
    # Fallback to terminal evaluation
    return evaluate_static(board) if not use_mc else evaluate_mc(board, rollout_count) * MC_SCALING_FACTOR
```

---

#### 3. **Resource Leak Potential (auto_vs_stockfish.py:44)**
```python
transport, stockfish = chess.engine.SimpleEngine.popen_uci(stockfish_path)
```

**Problem**: 
- `transport` variable assigned but never closed
- Potential resource leak if exception occurs before `quit()`

**Fix**:
```python
transport = None
stockfish = None
try:
    if stockfish_path != "mock":
        transport, stockfish = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    ...
finally:
    if stockfish:
        stockfish.quit()
    if transport:
        transport.close()  # Explicitly close transport
```

---

### 🟡 **MEDIUM Issues**

#### 4. **Inconsistent Import Style (auto_vs_stockfish.py:33)**
```python
class MockEngine:
    def play(self, board, limit):
        import random  # Import inside method
```

**Problem**: 
- `random` di-import di dalam method
- Inconsistent dengan top-level imports
- Performance overhead (walau kecil)

**Fix**: Move `import random` to top of file

---

#### 5. **Missing Return Type Hints**
Beberapa fungsi tidak punya return type:
- `play_vs_stockfish()` → should be `-> Optional[dict]`
- `run_experiment()` → should be `-> dict`
- `generate_charts()` → should be `-> None`

**Fix**:
```python
from typing import Optional

def play_vs_stockfish(...) -> Optional[dict]:
    ...
```

---

#### 6. **Hard-coded Constants**
```python
# evaluator_static.py:25
return -9999 if board.turn == chess.WHITE else 9999

# evaluator_mc.py:8
def simulate_random(board: chess.Board, max_steps=40) -> float:
```

**Problem**: Magic numbers scattered
**Fix**: Define module-level constants
```python
CHECKMATE_SCORE = 9999
MAX_ROLLOUT_STEPS = 40
```

---

#### 7. **Inefficient List Conversion (minimax_ab.py:39)**
```python
legal_moves = list(board.legal_moves)
```

**Problem**: 
- `board.legal_moves` returns generator
- Converting to list uses more memory
- Tidak perlu jika hanya iterate once

**Note**: Sebenarnya OK karena kita perlu random access untuk move ordering nanti

---

### 🟢 **MINOR Issues (Nice to Have)**

#### 8. **No Logging**
Semua output menggunakan `print()`. Untuk production:
```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"Starting experiment: {n_games} games")
```

---

#### 9. **No Input Validation**
```python
def minimax(board, depth, alpha, beta, maximizing, use_mc=False, rollout_count=30):
    # No validation: depth > 0, rollout_count > 0
```

**Fix**:
```python
if depth < 0:
    raise ValueError("Depth must be non-negative")
if rollout_count < 1:
    raise ValueError("Rollout count must be positive")
```

---

#### 10. **Code Duplication (minimax_ab.py:41-62)**
Maximizing and minimizing branches sangat mirip
**Solution**: Extract common logic or use -/+ sign trick

---

#### 11. **Missing Numpy Usage**
`evaluator_mc.py` imports numpy via requirements.txt tapi tidak dipakai
**Action**: Either use numpy for averaging or remove from requirements

---

## 🎯 Code Metrics

### Complexity
- **Cyclomatic Complexity**: Low-Medium (good ✅)
- **Function Length**: Most < 30 lines (good ✅)
- **Nesting Depth**: Max 3 levels (acceptable ✅)

### Maintainability
- **DRY Principle**: Mostly followed ✅
- **Single Responsibility**: Well separated ✅
- **Coupling**: Low (good) ✅
- **Cohesion**: High (good) ✅

### Readability
- **Variable Names**: Descriptive ✅
- **Comments**: Adequate ✅
- **Formatting**: Consistent ✅

---

## 📝 Recommended Action Items

### Priority 1 (Critical)
- [ ] Fix MC scaling factor (use constant or normalize eval)
- [ ] Add empty moves check in minimax
- [ ] Fix resource leak (close transport)

### Priority 2 (High)
- [ ] Add return type hints to all functions
- [ ] Move imports to module level
- [ ] Define magic numbers as constants

### Priority 3 (Medium)
- [ ] Add input validation
- [ ] Implement logging instead of print()
- [ ] Add error handling for file I/O

### Priority 4 (Nice to Have)
- [ ] Reduce code duplication in minimax branches
- [ ] Add more comprehensive unit tests
- [ ] Add performance benchmarks

---

## 🔧 Quick Wins (Implementasi Mudah)

1. **Constants File**: Buat `minimax/constants.py`
```python
# Material values
PIECE_VALUES = {...}

# Evaluation constants
CHECKMATE_SCORE = 9999
MC_SCALING_FACTOR = 1000

# Simulation constants
MAX_ROLLOUT_STEPS = 40
DEFAULT_ROLLOUT_COUNT = 30
```

2. **Type Hints**: Tambahkan di semua function signatures

3. **Error Messages**: Lebih descriptive
```python
except FileNotFoundError:
    print(f"Error: Stockfish executable not found at '{stockfish_path}'")
    print("Please download from https://stockfishchess.org/download/")
```

---

## 🏆 Best Practices Followed

✅ Modular architecture  
✅ Type hints (partial)  
✅ Docstrings  
✅ Unit tests  
✅ Git version control  
✅ Requirements.txt  
✅ Clean separation of concerns  

---

## 📈 Suggested Refactoring Priority

1. **Week 1**: Fix critical issues (P1)
2. **Week 2**: Add type hints & constants (P2)
3. **Week 3**: Logging & validation (P3)
4. **Later**: Performance optimization & advanced features

---

## 🎓 Learning Points

Untuk developer:
1. **Always close resources** (transport, file handles)
2. **Avoid magic numbers** - use named constants
3. **Type hints improve code quality** significantly
4. **Edge cases matter** - empty lists, None values
5. **Consistent import style** makes code cleaner

---

**Final Verdict**: Code is **production-ready with minor fixes**. Setelah memperbaiki critical issues, kode ini siap untuk deployment atau submission akademik.

---

**Generated by**: AI Code Analyzer  
**Tooling**: Manual review + Static analysis principles
