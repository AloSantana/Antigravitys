#!/usr/bin/env python3
"""
Test script for Performance Dashboard implementation
Tests all endpoints and functionality
"""

import requests
import time
import json
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_TIMEOUT = 5


def test_endpoint(name: str, url: str, expected_keys: list = None) -> bool:
    """Test an endpoint and validate response"""
    try:
        print(f"\n🧪 Testing {name}...")
        response = requests.get(url, timeout=TEST_TIMEOUT)
        
        if response.status_code != 200:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        if expected_keys:
            for key in expected_keys:
                if key not in data:
                    print(f"   ❌ Failed: Missing key '{key}'")
                    return False
        
        print(f"   ✅ Success")
        print(f"   📊 Response preview: {json.dumps(data, indent=2)[:200]}...")
        return True
        
    except requests.exceptions.Timeout:
        print(f"   ❌ Failed: Request timeout")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Failed: Connection error (is backend running?)")
        return False
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
        return False


def main():
    """Run all performance dashboard tests"""
    print("=" * 70)
    print("🚀 Performance Dashboard Test Suite")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Health endpoint
    results['health'] = test_endpoint(
        "Performance Health",
        f"{BACKEND_URL}/performance/health",
        ['status', 'health_score', 'warnings']
    )
    
    # Test 2: Main metrics endpoint
    results['metrics'] = test_endpoint(
        "Performance Metrics",
        f"{BACKEND_URL}/performance/metrics",
        ['system', 'websocket', 'requests', 'cache', 'mcp']
    )
    
    # Test 3: Metrics history
    results['history'] = test_endpoint(
        "Metrics History",
        f"{BACKEND_URL}/performance/metrics/history?minutes=5"
    )
    
    # Test 4: Summary endpoint
    results['summary'] = test_endpoint(
        "Performance Summary",
        f"{BACKEND_URL}/performance/summary"
    )
    
    # Test 5: WebSocket stats
    results['websocket'] = test_endpoint(
        "WebSocket Statistics",
        f"{BACKEND_URL}/performance/websocket-stats",
        ['active_connections', 'total_connections']
    )
    
    # Test 6: Cache stats
    results['cache'] = test_endpoint(
        "Cache Statistics",
        f"{BACKEND_URL}/performance/cache-stats",
        ['size', 'hits', 'misses', 'hit_rate_percent']
    )
    
    # Test 7: Request stats
    results['request'] = test_endpoint(
        "Request Statistics",
        f"{BACKEND_URL}/performance/request-stats",
        ['total_requests', 'total_errors', 'error_rate_percent']
    )
    
    # Test 8: MCP stats
    results['mcp'] = test_endpoint(
        "MCP Server Statistics",
        f"{BACKEND_URL}/performance/mcp-stats"
    )
    
    # Test 9: Analysis endpoint
    results['analysis'] = test_endpoint(
        "Performance Analysis",
        f"{BACKEND_URL}/performance/analysis",
        ['health', 'summary', 'recommendations']
    )
    
    # Test 10: Report endpoint
    results['report'] = test_endpoint(
        "Performance Report",
        f"{BACKEND_URL}/performance/report",
        ['report']
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 70)
    
    # Frontend check
    print("\n🌐 Frontend Dashboard Check:")
    print(f"   Open: http://localhost:3000")
    print(f"   Then click on: 📊 Performance tab")
    print(f"   Expected: Real-time charts and metrics updating every 2 seconds")
    
    if passed == total:
        print("\n✨ All tests passed! Performance Dashboard is ready!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
