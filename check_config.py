#!/usr/bin/env python3
"""
Configuration validation script for RAG-LLM system.
Checks all dependencies and configurations before running.
"""

import os
import sys

def check_python_version():
    """Verify Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Found: {version.major}.{version.minor}")
        return False
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_required_files():
    """Check if all required files exist"""
    required_files = [
        "main.py",
        "data_operations.py",
        "tools/embeddings.py",
        "tools/prompts.py",
        "data/medium.csv",
        ".env"
    ]
    
    missing = []
    for file in required_files:
        if not os.path.isfile(file):
            missing.append(file)
    
    if missing:
        print(f"❌ Missing required files:")
        for f in missing:
            print(f"   - {f}")
        return False
    
    print(f"✓ All {len(required_files)} required files found")
    return True


def check_env_configuration():
    """Validate .env file configuration"""
    if not os.path.isfile(".env"):
        print("❌ .env file not found!")
        return False
    
    try:
        with open(".env", "r") as f:
            env_content = f.read()
        
        if "GOOGLE_API_KEY" not in env_content:
            print("❌ GOOGLE_API_KEY not found in .env file")
            return False
        
        if "your_api_key_here" in env_content:
            print("❌ GOOGLE_API_KEY is still the placeholder value!")
            print("   Replace it with your actual API key from https://makersuite.google.com/app/apikey")
            return False
        
        print("✓ GOOGLE_API_KEY configured")
        return True
    except Exception as e:
        print(f"❌ Error reading .env: {str(e)}")
        return False


def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        "google.generativeai",
        "pandas",
        "dotenv",
        "llama_index",
        "langchain_text_splitters",
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing Python packages:")
        for p in missing:
            print(f"   - {p}")
        print("\nRun: pip install -r requirements-minimal.txt")
        return False
    
    print(f"✓ All {len(required_packages)} required packages installed")
    return True


def check_data_directory():
    """Verify data directory exists and is accessible"""
    if not os.path.isdir("data"):
        print("❌ data/ directory not found")
        return False
    
    if not os.path.isfile("data/medium.csv"):
        print("❌ data/medium.csv not found. Please add your Medium articles CSV file.")
        return False
    
    print("✓ Data directory and medium.csv found")
    return True


def validate_csv_structure():
    """Check if medium.csv has the required structure"""
    try:
        import pandas as pd
        df = pd.read_csv("data/medium.csv")
        
        if df.empty:
            print("❌ medium.csv is empty")
            return False
        
        if "Text" not in df.columns:
            print(f"❌ 'Text' column not found in medium.csv")
            print(f"   Available columns: {df.columns.tolist()}")
            return False
        
        print(f"✓ CSV valid: {len(df)} rows, {len(df.columns)} columns")
        return True
    except Exception as e:
        print(f"❌ Error reading medium.csv: {str(e)}")
        return False


def main():
    """Run all configuration checks"""
    print("=" * 60)
    print("🔍 RAG-LLM Configuration Checker")
    print("=" * 60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_required_files),
        ("Environment Config", check_env_configuration),
        ("Dependencies", check_dependencies),
        ("Data Directory", check_data_directory),
        ("CSV Structure", validate_csv_structure),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error during check: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} checks passed")
    
    if all(results):
        print("✅ All checks passed! Ready to run: python main.py")
        print("=" * 60)
        return 0
    else:
        print("❌ Please fix the issues above before running main.py")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
