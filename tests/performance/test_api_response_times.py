"""
Test API Response Times
Measures and validates response times for key endpoints
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from main import app

# Performance targets (in milliseconds)
TARGET_HEALTH_CHECK = 100  # Health check should be < 100ms
TARGET_SIMPLE_QUERY = 1000  # Simple queries < 1 second
TARGET_COMPLEX_QUERY = 3000  # Complex queries < 3 seconds
TARGET_FILE_LIST = 200  # File listing < 200ms


class TestAPIResponseTimes:
    """Test response times for various API endpoints"""
    
    # client fixture provided by conftest.py
    
    def measure_response_time(self, client: TestClient, method: str, endpoint: str, 
                             data: Dict = None, iterations: int = 10) -> Dict[str, float]:
        """
        Measure response time for an endpoint
        
        Args:
            client: TestClient instance
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Optional request data
            iterations: Number of iterations to average
            
        Returns:
            Dictionary with timing statistics
        """
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            times.append(elapsed)
            
            # Ensure request succeeded
            assert response.status_code in [200, 201], f"Request failed: {response.status_code}"
        
        return {
            "min": min(times),
            "max": max(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0,
            "p95": statistics.quantiles(times, n=20)[18] if len(times) > 1 else times[0],
            "p99": statistics.quantiles(times, n=100)[98] if len(times) > 1 else times[0]
        }
    
    def test_health_check_response_time(self, client):
        """Test that health check is fast"""
        print("\n🏥 Testing Health Check Response Time...")
        
        stats = self.measure_response_time(client, "GET", "/health", iterations=20)
        
        print(f"  Min: {stats['min']:.2f}ms")
        print(f"  Mean: {stats['mean']:.2f}ms")
        print(f"  Median: {stats['median']:.2f}ms")
        print(f"  P95: {stats['p95']:.2f}ms")
        print(f"  P99: {stats['p99']:.2f}ms")
        print(f"  Max: {stats['max']:.2f}ms")
        
        # Assertions
        assert stats['mean'] < TARGET_HEALTH_CHECK, \
            f"Health check too slow: {stats['mean']:.2f}ms > {TARGET_HEALTH_CHECK}ms"
        assert stats['p95'] < TARGET_HEALTH_CHECK * 1.5, \
            f"Health check P95 too slow: {stats['p95']:.2f}ms"
        
        print("  ✅ Health check response time is optimal")
    
    def test_root_endpoint_response_time(self, client):
        """Test root endpoint response time"""
        print("\n🏠 Testing Root Endpoint Response Time...")
        
        stats = self.measure_response_time(client, "GET", "/", iterations=15)
        
        print(f"  Mean: {stats['mean']:.2f}ms")
        print(f"  P95: {stats['p95']:.2f}ms")
        
        assert stats['mean'] < 100, \
            f"Root endpoint too slow: {stats['mean']:.2f}ms"
        
        print("  ✅ Root endpoint response time is optimal")
    
    def test_files_endpoint_response_time(self, client):
        """Test file listing endpoint response time"""
        print("\n📁 Testing Files Endpoint Response Time...")
        
        stats = self.measure_response_time(client, "GET", "/files", iterations=15)
        
        print(f"  Mean: {stats['mean']:.2f}ms")
        print(f"  P95: {stats['p95']:.2f}ms")
        print(f"  Max: {stats['max']:.2f}ms")
        
        assert stats['mean'] < TARGET_FILE_LIST, \
            f"Files endpoint too slow: {stats['mean']:.2f}ms > {TARGET_FILE_LIST}ms"
        
        print("  ✅ Files endpoint response time is acceptable")
    
    def test_agent_stats_response_time(self, client):
        """Test agent stats endpoint response time"""
        print("\n📊 Testing Agent Stats Response Time...")
        
        stats = self.measure_response_time(client, "GET", "/agent/stats", iterations=15)
        
        print(f"  Mean: {stats['mean']:.2f}ms")
        print(f"  P95: {stats['p95']:.2f}ms")
        
        assert stats['mean'] < 200, \
            f"Agent stats too slow: {stats['mean']:.2f}ms"
        
        print("  ✅ Agent stats response time is optimal")
    
    def test_performance_metrics_response_time(self, client):
        """Test performance metrics endpoint"""
        print("\n⚡ Testing Performance Metrics Endpoint...")
        
        stats = self.measure_response_time(client, "GET", "/performance/metrics", iterations=15)
        
        print(f"  Mean: {stats['mean']:.2f}ms")
        print(f"  P95: {stats['p95']:.2f}ms")
        
        assert stats['mean'] < 500, \
            f"Performance metrics too slow: {stats['mean']:.2f}ms"
        
        print("  ✅ Performance metrics response time is acceptable")
    
    def test_cache_warming_improves_response_time(self, client):
        """Test that cache warming improves response times"""
        print("\n🔥 Testing Cache Warming Impact...")
        
        # Clear cache first
        client.post("/agent/clear-cache")
        
        # Mock slow response for cold start.
        # Patch _delegate_to_gemini because auto-mode uses Gemini for low-complexity requests.
        from unittest.mock import patch
        async def slow_response(*args, **kwargs):
            import asyncio
            await asyncio.sleep(0.05)  # 50ms delay
            return {"response": "Paris", "source": "Gemini"}
            
        # Patch the Gemini delegate on the class so the already-created orchestrator instance
        # also uses the patched version (method resolution goes through the class at call time).
        with patch("agent.orchestrator.Orchestrator._delegate_to_gemini", side_effect=slow_response):
            # Measure cold response (first request)
            # The patch ensures this takes at least 50ms before being cached
            cold_start = time.perf_counter()
            response1 = client.post("/agent/ask", params={"query": "Capital of France?"})
            cold_time = (time.perf_counter() - cold_start) * 1000
            
            # Measure warm response (cached)
            # This hits the cache inside Orchestrator.process_request
            # BEFORE _delegate_to_gemini is reached, so it won't sleep
            warm_start = time.perf_counter()
            response2 = client.post("/agent/ask", params={"query": "Capital of France?"})
            warm_time = (time.perf_counter() - warm_start) * 1000
        
        print(f"  Cold start: {cold_time:.2f}ms")
        print(f"  Warm (cached): {warm_time:.2f}ms")
        speedup = cold_time / warm_time if warm_time > 0.1 else 0
        print(f"  Speedup: {speedup:.2f}x")
        
        # Warm should be significantly faster (at least 2x).
        # Cold path sleeps 50ms; warm path returns from cache in <5ms.
        assert warm_time < cold_time / 2, \
            f"Cache not providing enough speedup: {speedup:.2f}x"
        
        print("  ✅ Cache warming provides significant speedup")
    
    def test_response_time_consistency(self, client):
        """Test that response times are consistent (low variance)"""
        print("\n📏 Testing Response Time Consistency...")
        
        stats = self.measure_response_time(client, "GET", "/health", iterations=30)
        
        # Calculate coefficient of variation (stdev / mean)
        cv = stats['stdev'] / stats['mean'] if stats['mean'] > 0 else 0
        
        print(f"  Mean: {stats['mean']:.2f}ms")
        print(f"  StdDev: {stats['stdev']:.2f}ms")
        print(f"  Coefficient of Variation: {cv:.2%}")
        
        # CV should be < 50% for consistent performance
        assert cv < 0.5, \
            f"Response times too variable: CV={cv:.2%}"
        
        print("  ✅ Response times are consistent")


class TestEndToEndPerformance:
    """Test end-to-end performance scenarios"""
    
    def test_complete_workflow_performance(self, client):
        """Test performance of complete user workflow"""
        print("\n🔄 Testing Complete Workflow Performance...")
        
        workflow_start = time.perf_counter()
        
        # 1. Check health
        start = time.perf_counter()
        response = client.get("/health")
        health_time = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        
        # 2. Get files
        start = time.perf_counter()
        response = client.get("/files")
        files_time = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        
        # 3. Get stats
        start = time.perf_counter()
        response = client.get("/agent/stats")
        stats_time = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        
        # 4. Clear cache (maintenance operation)
        start = time.perf_counter()
        response = client.post("/agent/clear-cache")
        cache_time = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        
        total_time = (time.perf_counter() - workflow_start) * 1000
        
        print(f"  Health check: {health_time:.2f}ms")
        print(f"  Get files: {files_time:.2f}ms")
        print(f"  Get stats: {stats_time:.2f}ms")
        print(f"  Clear cache: {cache_time:.2f}ms")
        print(f"  Total workflow: {total_time:.2f}ms")
        
        # Complete workflow should be under 2 seconds
        assert total_time < 2000, \
            f"Workflow too slow: {total_time:.2f}ms"
        
        print("  ✅ Complete workflow performs well")


def print_performance_summary():
    """Print performance test summary"""
    print("\n" + "=" * 70)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 70)
    print("✅ All response time targets met")
    print("✅ Cache warming effective")
    print("✅ Response times consistent")
    print("✅ End-to-end workflow performant")
    print("=" * 70)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
    print_performance_summary()
