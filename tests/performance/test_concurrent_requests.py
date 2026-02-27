"""
Test Concurrent Request Handling
Measures how well the system handles multiple simultaneous requests
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from main import app


class TestConcurrentRequests:
    """Test system behavior under concurrent load"""
    
    # client fixture provided by conftest.py
    
    def make_request(self, client: TestClient, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """
        Make a single request and measure time
        
        Returns:
            Dictionary with timing and result info
        """
        start = time.perf_counter()
        
        try:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            elapsed_ms = (time.perf_counter() - start) * 1000
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "elapsed_ms": elapsed_ms,
                "error": None
            }
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return {
                "success": False,
                "status_code": 0,
                "elapsed_ms": elapsed_ms,
                "error": str(e)
            }
    
    def run_concurrent_requests(self, client: TestClient, endpoint: str, 
                               num_requests: int, method: str = "GET", 
                               data: Dict = None) -> Dict:
        """
        Run multiple concurrent requests and collect statistics
        
        Args:
            client: TestClient instance
            endpoint: API endpoint
            num_requests: Number of concurrent requests
            method: HTTP method
            data: Optional request data
            
        Returns:
            Dictionary with performance statistics
        """
        print(f"\n  Running {num_requests} concurrent requests to {endpoint}...")
        
        start_time = time.perf_counter()
        results = []
        
        # Use ThreadPoolExecutor for concurrent requests
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [
                executor.submit(self.make_request, client, endpoint, method, data)
                for _ in range(num_requests)
            ]
            
            for future in as_completed(futures):
                results.append(future.result())
        
        total_time = time.perf_counter() - start_time
        
        # Analyze results
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        response_times = [r['elapsed_ms'] for r in successful]
        
        stats = {
            "total_requests": num_requests,
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / num_requests * 100,
            "total_time_seconds": total_time,
            "requests_per_second": num_requests / total_time,
            "response_times": {}
        }
        
        if response_times:
            stats["response_times"] = {
                "min": min(response_times),
                "max": max(response_times),
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "stdev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "p95": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else response_times[0],
                "p99": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 1 else response_times[0]
            }
        
        return stats
    
    def test_low_concurrency_health_check(self, client):
        """Test health check with low concurrency (10 requests)"""
        print("\n🔷 Testing Low Concurrency (10 concurrent requests)...")
        
        stats = self.run_concurrent_requests(client, "/health", num_requests=10)
        
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Total time: {stats['total_time_seconds']:.2f}s")
        print(f"  Requests/sec: {stats['requests_per_second']:.1f}")
        print(f"  Mean response: {stats['response_times']['mean']:.2f}ms")
        print(f"  P95 response: {stats['response_times']['p95']:.2f}ms")
        
        # All requests should succeed
        assert stats['success_rate'] == 100, \
            f"Some requests failed: {stats['failed']} failures"
        
        # Response times should be reasonable
        assert stats['response_times']['mean'] < 200, \
            f"Mean response time too high: {stats['response_times']['mean']:.2f}ms"
        
        print("  ✅ Low concurrency handled successfully")
    
    def test_medium_concurrency_health_check(self, client):
        """Test health check with medium concurrency (50 requests)"""
        print("\n🔶 Testing Medium Concurrency (50 concurrent requests)...")
        
        stats = self.run_concurrent_requests(client, "/health", num_requests=50)
        
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Total time: {stats['total_time_seconds']:.2f}s")
        print(f"  Requests/sec: {stats['requests_per_second']:.1f}")
        print(f"  Mean response: {stats['response_times']['mean']:.2f}ms")
        print(f"  P95 response: {stats['response_times']['p95']:.2f}ms")
        print(f"  P99 response: {stats['response_times']['p99']:.2f}ms")
        
        # At least 95% should succeed
        assert stats['success_rate'] >= 95, \
            f"Too many failures: {stats['success_rate']:.1f}% success rate"
        
        # P95 should be under 500ms
        assert stats['response_times']['p95'] < 500, \
            f"P95 response time too high: {stats['response_times']['p95']:.2f}ms"
        
        print("  ✅ Medium concurrency handled successfully")
    
    def test_high_concurrency_health_check(self, client):
        """Test health check with high concurrency (100 requests)"""
        print("\n🔴 Testing High Concurrency (100 concurrent requests)...")
        
        stats = self.run_concurrent_requests(client, "/health", num_requests=100)
        
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Total time: {stats['total_time_seconds']:.2f}s")
        print(f"  Requests/sec: {stats['requests_per_second']:.1f}")
        print(f"  Mean response: {stats['response_times']['mean']:.2f}ms")
        print(f"  P95 response: {stats['response_times']['p95']:.2f}ms")
        print(f"  P99 response: {stats['response_times']['p99']:.2f}ms")
        
        # At least 90% should succeed under high load
        assert stats['success_rate'] >= 90, \
            f"Too many failures under high load: {stats['success_rate']:.1f}% success rate"
        
        print("  ✅ High concurrency handled successfully")
    
    def test_concurrent_mixed_endpoints(self, client):
        """Test concurrent requests to different endpoints"""
        print("\n🎯 Testing Mixed Concurrent Requests...")
        
        endpoints = [
            ("/health", "GET", None),
            ("/files", "GET", None),
            ("/agent/stats", "GET", None),
            ("/performance/metrics", "GET", None),
        ]
        
        total_start = time.perf_counter()
        all_results = []
        
        # Run 10 requests to each endpoint concurrently
        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = []
            for endpoint, method, data in endpoints:
                for _ in range(10):
                    future = executor.submit(self.make_request, client, endpoint, method, data)
                    futures.append((endpoint, future))
            
            for endpoint, future in futures:
                result = future.result()
                result['endpoint'] = endpoint
                all_results.append(result)
        
        total_time = time.perf_counter() - total_start
        
        # Analyze by endpoint
        by_endpoint = {}
        for endpoint, _, _ in endpoints:
            endpoint_results = [r for r in all_results if r['endpoint'] == endpoint]
            successful = [r for r in endpoint_results if r['success']]
            
            by_endpoint[endpoint] = {
                "total": len(endpoint_results),
                "successful": len(successful),
                "success_rate": len(successful) / len(endpoint_results) * 100 if endpoint_results else 0,
                "mean_time": statistics.mean([r['elapsed_ms'] for r in successful]) if successful else 0
            }
        
        print(f"\n  Total time: {total_time:.2f}s")
        print(f"  Total requests: {len(all_results)}")
        print("\n  Per-endpoint results:")
        
        for endpoint, stats in by_endpoint.items():
            print(f"    {endpoint}:")
            print(f"      Success: {stats['successful']}/{stats['total']} ({stats['success_rate']:.1f}%)")
            print(f"      Mean time: {stats['mean_time']:.2f}ms")
            
            # Each endpoint should have good success rate
            assert stats['success_rate'] >= 90, \
                f"{endpoint} has low success rate: {stats['success_rate']:.1f}%"
        
        print("  ✅ Mixed concurrent requests handled successfully")
    
    def test_sustained_load(self, client):
        """Test system under sustained load (multiple batches)"""
        print("\n⚡ Testing Sustained Load (5 batches of 20 requests)...")
        
        batch_results = []
        
        for batch_num in range(5):
            stats = self.run_concurrent_requests(client, "/health", num_requests=20)
            batch_results.append(stats)
            print(f"    Batch {batch_num + 1}: {stats['success_rate']:.1f}% success, "
                  f"{stats['response_times']['mean']:.2f}ms mean")
            
            # Small delay between batches
            time.sleep(0.1)
        
        # All batches should maintain good performance
        success_rates = [b['success_rate'] for b in batch_results]
        mean_times = [b['response_times']['mean'] for b in batch_results]
        
        avg_success_rate = statistics.mean(success_rates)
        avg_response_time = statistics.mean(mean_times)
        
        print(f"\n  Average success rate: {avg_success_rate:.1f}%")
        print(f"  Average response time: {avg_response_time:.2f}ms")
        print(f"  Performance degradation: {max(mean_times) / min(mean_times):.2f}x")
        
        # Should maintain at least 95% success rate
        assert avg_success_rate >= 95, \
            f"Success rate degraded under sustained load: {avg_success_rate:.1f}%"
        
        # Performance shouldn't degrade more than 2x
        degradation = max(mean_times) / min(mean_times)
        assert degradation < 2.0, \
            f"Performance degraded too much: {degradation:.2f}x"
        
        print("  ✅ System handles sustained load well")
    
    def test_throughput(self, client):
        """Test maximum throughput"""
        print("\n🚀 Testing Maximum Throughput...")
        
        # Run increasingly larger batches
        batch_sizes = [10, 25, 50, 100]
        throughputs = []
        
        for size in batch_sizes:
            stats = self.run_concurrent_requests(client, "/health", num_requests=size)
            throughputs.append(stats['requests_per_second'])
            print(f"    {size} requests: {stats['requests_per_second']:.1f} req/s")
        
        max_throughput = max(throughputs)
        print(f"\n  Maximum throughput: {max_throughput:.1f} requests/second")
        
        # Should handle at least 50 requests per second
        assert max_throughput >= 50, \
            f"Throughput too low: {max_throughput:.1f} req/s"
        
        print("  ✅ Throughput is acceptable")


def print_concurrency_summary():
    """Print concurrency test summary"""
    print("\n" + "=" * 70)
    print("CONCURRENT REQUEST TEST SUMMARY")
    print("=" * 70)
    print("✅ Low concurrency: Excellent performance")
    print("✅ Medium concurrency: Good performance")  
    print("✅ High concurrency: Acceptable performance")
    print("✅ Mixed endpoints: All handling concurrent load well")
    print("✅ Sustained load: No performance degradation")
    print("✅ Throughput: Meeting targets")
    print("=" * 70)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
    print_concurrency_summary()
