# Stockfish Setup Guide

This guide explains how to set up the Stockfish chess engine for use with this project.

## Quick Setup (Recommended)

Run the automated setup script:

```bash
cd engine-chess
python setup_stockfish.py
```

This will:
- Download Stockfish 16.1 for Windows (AVX2 variant)
- Extract and configure the executable
- Verify the installation
- Show example usage commands

## Manual Setup

If you prefer to download manually:

1. **Download Stockfish**
   - Visit: https://stockfishchess.org/download/
   - Download: `stockfish-windows-x86-64-avx2.zip` (for modern CPUs)
   - Alternative: `stockfish-windows-x86-64.zip` (for older CPUs)

2. **Extract the Files**
   - Create directory: `engine-chess/stockfish/`
   - Extract the ZIP file to this directory
   - Ensure the `.exe` file is directly in the `stockfish/` folder

3. **Verify Installation**
   ```bash
   cd engine-chess
   python stockfish_config.py
   ```

## Usage Examples

### Run Baseline Experiment (Minimax + Alpha-Beta)
```bash
python main.py --stockfish "stockfish/stockfish-windows-x86-64-avx2.exe" --games 10 --depth 3 --mode minimax --output results/baseline_vs_stockfish.json
```

### Run Hybrid Experiment (Minimax + Alpha-Beta + Monte Carlo)
```bash
python main.py --stockfish "stockfish/stockfish-windows-x86-64-avx2.exe" --games 10 --depth 2 --mode hybrid --rollouts 30 --output results/hybrid_vs_stockfish.json
```

### Quick Test (2 games)
```bash
python main.py --stockfish "stockfish/stockfish-windows-x86-64-avx2.exe" --games 2 --depth 2 --mode minimax
```

## Configuration

Use `stockfish_config.py` to:
- Locate installed Stockfish automatically
- Validate Stockfish responds correctly
- Get version information

```bash
python stockfish_config.py
```

## Troubleshooting

### "Stockfish executable not found"
- Ensure you ran `setup_stockfish.py` or manually placed Stockfish in `engine-chess/stockfish/`
- Check the file is named `stockfish-windows-x86-64-avx2.exe` or similar

### "Stockfish validation: FAILED"
- Your CPU may not support AVX2. Download the non-AVX2 variant instead
- Check Windows Defender didn't block the executable
- Try running Stockfish directly to see error messages:
  ```bash
  stockfish\stockfish-windows-x86-64-avx2.exe
  ```
  Then type `quit` to exit

### Download fails with SSL error
- Update Python: `python -m pip install --upgrade pip`
- Or download manually from https://stockfishchess.org/

### Permission denied errors
- Run Command Prompt as Administrator
- Or move the project to a folder where you have write permissions

## Stockfish Strength Settings

Stockfish in this project uses:
- **Skill Level**: 20 (Maximum, ~3200 ELO)
- **Time per Move**: 100ms
- **Threads**: 1

To adjust strength, modify `simulation/auto_vs_stockfish.py`:
```python
stockfish.configure({
    "Skill Level": 10,  # Lower = weaker (0-20)
    "UCI_LimitStrength": True,
    "UCI_Elo": 1500  # Set specific ELO
})
```

## Next Steps

After setup, you can:
1. Run experiments with different configurations
2. Compare Minimax vs Hybrid performance
3. Analyze results in `results/` directory
4. Generate charts with matplotlib

See [progress.md](file:///e:/PKA/tubes/progress.md) for more details on the project.
