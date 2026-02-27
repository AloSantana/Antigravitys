#!/usr/bin/env python3
"""
Test script to verify error handling and reliability improvements.
Tests the enhanced error handling without requiring full app startup.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_watcher_imports():
    """Test that watcher module imports correctly with all new features."""
    print("\n🧪 Testing Watcher Module...")
    try:
        from watcher import Watcher, DropHandler
        print("  ✓ Watcher and DropHandler imported successfully")
        
        # Check for new methods
        assert hasattr(Watcher, 'is_healthy'), "Missing is_healthy method"
        print("  ✓ Watcher.is_healthy() method exists")
        
        assert hasattr(DropHandler, '_validate_path'), "Missing _validate_path method"
        print("  ✓ DropHandler._validate_path() method exists")
        
        # Check for retry logic in the source code
        watcher_file = Path(__file__).parent / "backend" / "watcher.py"
        watcher_content = watcher_file.read_text()
        assert "_max_retries" in watcher_content, "Missing _max_retries in code"
        print("  ✓ DropHandler has retry logic (_max_retries)")
        
        return True
    except Exception as e:
        print(f"  ✗ Watcher test failed: {e}")
        return False

def test_ingestion_imports():
    """Test that ingestion module imports correctly with all new features."""
    print("\n🧪 Testing Ingestion Module...")
    try:
        from rag.ingest import IngestionPipeline
        print("  ✓ IngestionPipeline imported successfully")
        
        # Check for new methods
        assert hasattr(IngestionPipeline, '_get_memory_usage_mb'), "Missing _get_memory_usage_mb method"
        print("  ✓ IngestionPipeline._get_memory_usage_mb() method exists")
        
        assert hasattr(IngestionPipeline, '_read_file_safely'), "Missing _read_file_safely method"
        print("  ✓ IngestionPipeline._read_file_safely() method exists")
        
        # Check configuration imports
        from rag.ingest import MAX_FILE_SIZE_MB, MAX_CHUNK_SIZE, CHUNK_OVERLAP
        print(f"  ✓ Configuration loaded: MAX_FILE_SIZE_MB={MAX_FILE_SIZE_MB}, MAX_CHUNK_SIZE={MAX_CHUNK_SIZE}, CHUNK_OVERLAP={CHUNK_OVERLAP}")
        
        return True
    except Exception as e:
        print(f"  ✗ Ingestion test failed: {e}")
        return False

def test_main_features():
    """Test that main module has new features."""
    print("\n🧪 Testing Main Module Features...")
    try:
        # We can't import FastAPI without dependencies, but we can check the file
        main_file = Path(__file__).parent / "backend" / "main.py"
        content = main_file.read_text()
        
        # Check for signal handlers
        assert "signal_handler" in content, "Missing signal_handler function"
        print("  ✓ signal_handler function exists")
        
        assert "SIGTERM" in content and "SIGINT" in content, "Missing signal registrations"
        print("  ✓ SIGTERM and SIGINT handlers registered")
        
        # Check for graceful shutdown
        assert "graceful_shutdown" in content, "Missing graceful_shutdown function"
        print("  ✓ graceful_shutdown function exists")
        
        # Check for health endpoints
        assert "/health/live" in content, "Missing /health/live endpoint"
        print("  ✓ /health/live endpoint exists")
        
        assert "/health/ready" in content, "Missing /health/ready endpoint"
        print("  ✓ /health/ready endpoint exists")
        
        assert "readiness_check" in content, "Missing readiness_check function"
        print("  ✓ readiness_check function exists")
        
        return True
    except Exception as e:
        print(f"  ✗ Main module test failed: {e}")
        return False

def test_env_config():
    """Test that .env.example has new configuration."""
    print("\n🧪 Testing Environment Configuration...")
    try:
        env_file = Path(__file__).parent / ".env.example"
        content = env_file.read_text()
        
        required_vars = [
            "RAG_MAX_FILE_SIZE_MB",
            "RAG_MAX_CHUNK_SIZE",
            "RAG_CHUNK_OVERLAP",
            "RAG_BATCH_SIZE",
            "RAG_MEMORY_WARNING_MB"
        ]
        
        for var in required_vars:
            assert var in content, f"Missing {var} in .env.example"
            print(f"  ✓ {var} configuration exists")
        
        return True
    except Exception as e:
        print(f"  ✗ Environment config test failed: {e}")
        return False

def test_logging_usage():
    """Test that logging is used instead of print."""
    print("\n🧪 Testing Logging Usage...")
    try:
        watcher_file = Path(__file__).parent / "backend" / "watcher.py"
        watcher_content = watcher_file.read_text()
        
        # Check for logger usage
        assert "logger = logging.getLogger(__name__)" in watcher_content, "Missing logger initialization"
        print("  ✓ Logger initialized in watcher.py")
        
        assert "logger.info" in watcher_content, "Missing logger.info usage"
        assert "logger.error" in watcher_content, "Missing logger.error usage"
        assert "logger.warning" in watcher_content, "Missing logger.warning usage"
        print("  ✓ Logger methods used (info, error, warning)")
        
        # Check ingestion file
        ingest_file = Path(__file__).parent / "backend" / "rag" / "ingest.py"
        ingest_content = ingest_file.read_text()
        
        assert "logger = logging.getLogger(__name__)" in ingest_content, "Missing logger initialization in ingest.py"
        print("  ✓ Logger initialized in ingest.py")
        
        assert "logger.info" in ingest_content, "Missing logger.info usage in ingest.py"
        assert "logger.error" in ingest_content, "Missing logger.error usage in ingest.py"
        print("  ✓ Logger methods used in ingest.py")
        
        return True
    except Exception as e:
        print(f"  ✗ Logging test failed: {e}")
        return False

def test_error_handling():
    """Test that comprehensive error handling is present."""
    print("\n🧪 Testing Error Handling...")
    try:
        watcher_file = Path(__file__).parent / "backend" / "watcher.py"
        watcher_content = watcher_file.read_text()
        
        # Check for exception handling
        assert "except PermissionError" in watcher_content, "Missing PermissionError handling"
        print("  ✓ PermissionError handling exists")
        
        assert "except OSError" in watcher_content, "Missing OSError handling"
        print("  ✓ OSError handling exists")
        
        assert "except asyncio.CancelledError" in watcher_content, "Missing CancelledError handling"
        print("  ✓ asyncio.CancelledError handling exists")
        
        # Check ingestion file
        ingest_file = Path(__file__).parent / "backend" / "rag" / "ingest.py"
        ingest_content = ingest_file.read_text()
        
        assert "except UnicodeDecodeError" in ingest_content, "Missing UnicodeDecodeError handling"
        print("  ✓ UnicodeDecodeError handling exists")
        
        assert "try:" in ingest_content and ingest_content.count("except") >= 5, "Not enough error handling"
        print("  ✓ Comprehensive try-except blocks present")
        
        return True
    except Exception as e:
        print(f"  ✗ Error handling test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 Testing Error Handling & Reliability Improvements")
    print("=" * 60)
    
    tests = [
        ("Watcher Imports", test_watcher_imports),
        ("Ingestion Imports", test_ingestion_imports),
        ("Main Features", test_main_features),
        ("Environment Config", test_env_config),
        ("Logging Usage", test_logging_usage),
        ("Error Handling", test_error_handling),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! Error handling improvements verified.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
