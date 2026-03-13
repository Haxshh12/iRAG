#!/usr/bin/env python3
"""
Quick-start script to verify optimized RAG-LLM system
"""

import os
import sys
from pathlib import Path

def check_file(path: str, description: str) -> bool:
    """Check if file exists and report"""
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"✓ {description}: {path} ({size:,} bytes)")
        return True
    else:
        print(f"❌ {description}: {path} NOT FOUND")
        return False

def check_imports() -> bool:
    """Check if required packages are installed"""
    print("\n📦 Checking required packages...")
    packages = [
        ('google.generativeai', 'Google Generative AI'),
        ('pandas', 'Pandas'),
        ('llama_index', 'LlamaIndex'),
        ('dotenv', 'python-dotenv'),
        ('tqdm', 'tqdm'),
        ('psutil', 'psutil'),
    ]
    
    all_good = True
    for package, name in packages:
        try:
            __import__(package)
            print(f"✓ {name}")
        except ImportError:
            print(f"❌ {name} - NOT INSTALLED")
            all_good = False
    
    return all_good

def check_api_key() -> bool:
    """Check if API key is configured"""
    print("\n🔑 Checking API configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"✓ API Key: {api_key[:15]}...")
        return True
    else:
        print("❌ API Key not found in .env file")
        print("   Steps:")
        print("   1. Copy: cp .env.example .env")
        print("   2. Get key: https://makersuite.google.com/app/apikey")
        print("   3. Add to .env: GOOGLE_API_KEY=<your-key>")
        return False

def check_data() -> bool:
    """Check if data files exist"""
    print("\n📊 Checking data files...")
    
    os.makedirs("data", exist_ok=True)
    
    has_original = check_file("data/medium.csv", "Original data")
    has_embedded = check_file("data/embedded_data.csv", "Cached embeddings")
    
    return has_original or has_embedded

def check_optimizations() -> bool:
    """Check if optimization files exist"""
    print("\n⚡ Checking optimization files...")
    
    files = [
        ("main_optimized.py", "Optimized main entry point"),
        ("data_operations_optimized.py", "Optimized data operations"),
        ("embeddings_optimized.py", "Optimized embeddings"),
        ("config.py", "Performance configuration"),
        ("cache.py", "Caching system"),
    ]
    
    all_good = True
    for path, desc in files:
        if not check_file(path, desc):
            all_good = False
    
    return all_good

def show_next_steps():
    """Show next steps to run the system"""
    print("\n" + "="*60)
    print("  ✅ OPTIMIZATION CHECK COMPLETE")
    print("="*60)
    
    print("\n🚀 Next Steps:\n")
    print("1. Install/Update dependencies:")
    print("   pip install -r requirements-minimal.txt\n")
    
    print("2. Run the optimized system:")
    print("   python main_optimized.py\n")
    
    print("3. Try interactive commands:")
    print("   - Ask questions about articles")
    print("   - Type 'stats' to see cache performance")
    print("   - Type 'memory' to check memory usage")
    print("   - Type 'config' to see performance settings")
    print("   - Type 'help' for all commands\n")

def main():
    """Run all checks"""
    print("\n" + "🔍 "*15)
    print("RAG-LLM High-Performance Optimization Checker")
    print("🔍 "*15 + "\n")
    
    # Run checks
    checks = [
        ("Files", lambda: all([
            check_file("main_optimized.py", "main_optimized.py"),
            check_file("config.py", "config.py"),
            check_file("cache.py", "cache.py"),
            check_file("embeddings_optimized.py", "embeddings_optimized.py"),
            check_file(".env.example", ".env.example"),
        ])),
        ("Dependencies", check_imports),
        ("API Key", check_api_key),
        ("Data", check_data),
        ("Optimizations", check_optimizations),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error during {name} check: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    
    for name, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    if all(results.values()):
        print("\n✅ All checks passed!")
        show_next_steps()
    else:
        print("\n⚠️  Some checks failed - see above for details")
        print("Please fix the issues and try again")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
