"""
Automated setup script for Stockfish chess engine.
Downloads and installs Stockfish for Windows.
"""

import urllib.request
import zipfile
import os
import sys
import subprocess

STOCKFISH_VERSION = "16.1"
STOCKFISH_VARIANT = "stockfish-windows-x86-64-avx2"
STOCKFISH_URL = f"https://github.com/official-stockfish/Stockfish/releases/download/sf_{STOCKFISH_VERSION}/stockfish-windows-x86-64-avx2.zip"
STOCKFISH_DIR = os.path.join(os.path.dirname(__file__), "stockfish")
STOCKFISH_EXE = os.path.join(STOCKFISH_DIR, f"{STOCKFISH_VARIANT}.exe")

def download_stockfish():
    """Download Stockfish from official GitHub releases."""
    print(f"Downloading Stockfish {STOCKFISH_VERSION}...")
    print(f"URL: {STOCKFISH_URL}")
    
    # Create stockfish directory if it doesn't exist
    os.makedirs(STOCKFISH_DIR, exist_ok=True)
    
    zip_path = os.path.join(STOCKFISH_DIR, "stockfish.zip")
    
    try:
        # Download the file
        urllib.request.urlretrieve(STOCKFISH_URL, zip_path)
        print(f"✓ Downloaded to {zip_path}")
        
        # Extract the ZIP file
        print("Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(STOCKFISH_DIR)
        print(f"✓ Extracted to {STOCKFISH_DIR}")
        
        # Remove the ZIP file
        os.remove(zip_path)
        print("✓ Cleaned up ZIP file")
        
        # Find the executable
        exe_found = False
        for root, dirs, files in os.walk(STOCKFISH_DIR):
            for file in files:
                if file.endswith(".exe") and "stockfish" in file.lower():
                    exe_path = os.path.join(root, file)
                    # Move to expected location if needed
                    if exe_path != STOCKFISH_EXE:
                        import shutil
                        shutil.move(exe_path, STOCKFISH_EXE)
                    exe_found = True
                    break
            if exe_found:
                break
        
        if exe_found:
            print(f"✓ Stockfish executable ready at: {STOCKFISH_EXE}")
        else:
            print("⚠ Warning: Could not find Stockfish executable")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error downloading Stockfish: {e}")
        return False

def verify_stockfish():
    """Verify that Stockfish is working correctly."""
    if not os.path.exists(STOCKFISH_EXE):
        print(f"✗ Stockfish executable not found at {STOCKFISH_EXE}")
        return False
    
    print("\nVerifying Stockfish installation...")
    try:
        # Test UCI protocol
        result = subprocess.run(
            [STOCKFISH_EXE],
            input=b"uci\nquit\n",
            capture_output=True,
            timeout=5
        )
        
        output = result.stdout.decode('utf-8', errors='ignore')
        
        if "uciok" in output:
            print("✓ Stockfish is responding correctly to UCI commands")
            
            # Extract version info if available
            for line in output.split('\n'):
                if line.startswith('id name'):
                    print(f"✓ {line}")
                    break
            
            return True
        else:
            print("✗ Stockfish did not respond with 'uciok'")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Stockfish verification timed out")
        return False
    except Exception as e:
        print(f"✗ Error verifying Stockfish: {e}")
        return False

def main():
    """Main setup function."""
    print("=" * 60)
    print("Stockfish Chess Engine Setup")
    print("=" * 60)
    
    # Check if already installed
    if os.path.exists(STOCKFISH_EXE):
        print(f"\n✓ Stockfish already exists at: {STOCKFISH_EXE}")
        print("Verifying existing installation...")
        if verify_stockfish():
            print("\n✓ Setup complete! Stockfish is ready to use.")
            print(f"\nStockfish path: {STOCKFISH_EXE}")
            print("\nExample usage:")
            print(f'  python main.py --stockfish "{STOCKFISH_EXE}" --games 5 --depth 3 --mode minimax')
            return 0
        else:
            print("\n⚠ Existing installation appears broken. Re-downloading...")
            os.remove(STOCKFISH_EXE)
    
    # Download Stockfish
    if not download_stockfish():
        print("\n✗ Failed to download Stockfish")
        return 1
    
    # Verify installation
    if not verify_stockfish():
        print("\n✗ Stockfish installation verification failed")
        return 1
    
    print("\n" + "=" * 60)
    print("✓ Setup complete! Stockfish is ready to use.")
    print("=" * 60)
    print(f"\nStockfish path: {STOCKFISH_EXE}")
    print("\nExample usage:")
    print(f'  python main.py --stockfish "{STOCKFISH_EXE}" --games 5 --depth 3 --mode minimax')
    print(f'  python main.py --stockfish "{STOCKFISH_EXE}" --games 5 --depth 2 --mode hybrid --rollouts 20')
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
