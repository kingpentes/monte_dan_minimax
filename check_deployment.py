#!/usr/bin/env python3
"""
Pre-deployment check script for Vercel
"""

import os
import sys

def check_file_exists(filepath, required=True):
    """Check if file exists"""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} {filepath}")
    if required and not exists:
        print(f"   ERROR: Required file missing!")
        return False
    return True

def check_directory_structure():
    """Check if all required directories exist"""
    print("\n=== Checking Directory Structure ===")
    
    required_dirs = [
        "web",
        "web/static",
        "web/templates",
        "engine-chess",
        "engine-chess/minimax",
        "api"
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        exists = os.path.isdir(dir_path)
        status = "✓" if exists else "✗"
        print(f"{status} {dir_path}/")
        if not exists:
            all_ok = False
    
    return all_ok

def check_required_files():
    """Check if all required files exist"""
    print("\n=== Checking Required Files ===")
    
    required_files = [
        ("vercel.json", True),
        (".vercelignore", True),
        ("requirements.txt", True),
        ("api/index.py", True),
        ("web/app.py", True),
        ("web/templates/index.html", True),
        ("engine-chess/minimax/minimax_ab.py", True),
        ("engine-chess/stockfish_config.py", True),
    ]
    
    all_ok = True
    for filepath, required in required_files:
        if not check_file_exists(filepath, required):
            all_ok = False
    
    return all_ok

def check_imports():
    """Check if key modules can be imported"""
    print("\n=== Checking Python Imports ===")
    
    modules = [
        "chess",
        "flask",
        "numpy"
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} (not installed)")
            all_ok = False
    
    return all_ok

def check_vercel_config():
    """Check vercel.json configuration"""
    print("\n=== Checking Vercel Configuration ===")
    
    try:
        import json
        with open("vercel.json", "r") as f:
            config = json.load(f)
        
        print("✓ vercel.json is valid JSON")
        
        # Check builds
        if "builds" in config:
            print(f"✓ Found {len(config['builds'])} build(s)")
        else:
            print("✗ No builds defined")
            return False
        
        # Check routes
        if "routes" in config:
            print(f"✓ Found {len(config['routes'])} route(s)")
        else:
            print("✗ No routes defined")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error reading vercel.json: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 50)
    print("Vercel Pre-Deployment Check")
    print("=" * 50)
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Required Files", check_required_files),
        ("Python Imports", check_imports),
        ("Vercel Config", check_vercel_config)
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n✓ All checks passed! Ready to deploy to Vercel.")
        print("\nNext steps:")
        print("  1. Commit all changes: git add . && git commit -m 'Ready for Vercel'")
        print("  2. Push to GitHub: git push")
        print("  3. Deploy: vercel --prod")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
