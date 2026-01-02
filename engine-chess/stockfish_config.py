"""
Configuration helper for Stockfish chess engine.
Provides utilities to locate and validate Stockfish installation.
"""

import os
import subprocess

def get_default_stockfish_path():
    """
    Get the default Stockfish path based on project structure.
    
    Returns:
        str: Path to Stockfish executable or None if not found
    """
    # Path relative to this file
    script_dir = os.path.dirname(__file__)
    stockfish_dir = os.path.join(script_dir, "stockfish")
    
    import sys
    
    # Check system PATH first
    import shutil
    if shutil.which("stockfish"):
        return shutil.which("stockfish")

    # Determine OS-specific binary names
    if sys.platform.startswith('win'):
        possible_names = [
            "stockfish-windows-x86-64-avx2.exe",
            "stockfish.exe",
            "stockfish-windows.exe"
        ]
    else:
        # Linux/Mac
        possible_names = [
            "stockfish",
            "stockfish-ubuntu-x86-64-avx2",
            "stockfish-ubuntu-x86-64-modern",
            "stockfish_15_x64_avx2.bin" # Common variants
        ]
        
    # Check explicitly defined system paths (fallback for Linux)
    if not sys.platform.startswith('win'):
        system_paths = [
            "/usr/bin/stockfish",
            "/usr/local/bin/stockfish",
            "/app/.nix-profile/bin/stockfish" # Nixpacks specific
        ]
        for path in system_paths:
            if os.path.exists(path):
                return path
    
    for name in possible_names:
        path = os.path.join(stockfish_dir, name)
        if os.path.exists(path):
            return path
    
    return None

def validate_stockfish(path):
    """
    Validate that Stockfish executable works correctly.
    
    Args:
        path: Path to Stockfish executable
        
    Returns:
        bool: True if Stockfish is valid, False otherwise
    """
    if not os.path.exists(path):
        return False
    
    try:
        # Test UCI protocol
        result = subprocess.run(
            [path],
            input=b"uci\nquit\n",
            capture_output=True,
            timeout=5
        )
        
        output = result.stdout.decode('utf-8', errors='ignore')
        return "uciok" in output
        
    except Exception:
        return False

def get_stockfish_info(path):
    """
    Get information about Stockfish version.
    
    Args:
        path: Path to Stockfish executable
        
    Returns:
        dict: Dictionary with 'name' and 'author' keys, or None if error
    """
    if not os.path.exists(path):
        return None
    
    try:
        result = subprocess.run(
            [path],
            input=b"uci\nquit\n",
            capture_output=True,
            timeout=5
        )
        
        output = result.stdout.decode('utf-8', errors='ignore')
        info = {}
        
        for line in output.split('\n'):
            if line.startswith('id name'):
                info['name'] = line.split('id name')[1].strip()
            elif line.startswith('id author'):
                info['author'] = line.split('id author')[1].strip()
        
        return info if info else None
        
    except Exception:
        return None

def main():
    """Test configuration helper."""
    print("Stockfish Configuration Helper")
    print("=" * 60)
    
    default_path = get_default_stockfish_path()
    
    if default_path:
        print(f"✓ Found Stockfish at: {default_path}")
        
        if validate_stockfish(default_path):
            print("✓ Stockfish validation: OK")
            
            info = get_stockfish_info(default_path)
            if info:
                print(f"✓ Engine: {info.get('name', 'Unknown')}")
                print(f"✓ Author: {info.get('author', 'Unknown')}")
        else:
            print("✗ Stockfish validation: FAILED")
    else:
        print("✗ Stockfish not found in default location")
        print(f"   Expected location: {os.path.join(os.path.dirname(__file__), 'stockfish')}")
        print("\nTo install Stockfish, run:")
        print("  python setup_stockfish.py")

if __name__ == "__main__":
    main()
