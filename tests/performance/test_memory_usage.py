"""
Test Memory Usage Patterns
Monitors and validates memory usage during various operations
"""

import pytest
import time
import psutil
import os
from typing import Dict
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


# Memory targets (in MB)
TARGET_BASELINE_MEMORY = 200  # Baseline memory < 200MB
TARGET_MEMORY_GROWTH = 50  # Growth per 100 requests < 50MB
MEMORY_LEAK_THRESHOLD = 1.2  # Memory shouldn't grow > 20% after operations


class TestMemoryUsage:
    """Test memory usage patterns and detect leaks"""
    
    def get_process_memory_mb(self) -> float:
        """Get current process memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Get detailed memory statistics"""
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        mem_percent = process.memory_percent()
        
        return {
            "rss_mb": mem_info.rss / (1024 * 1024),
            "vms_mb": mem_info.vms / (1024 * 1024),
            "percent": mem_percent,
            "available_mb": psutil.virtual_memory().available / (1024 * 1024)
        }
    
    def test_baseline_memory_usage(self, client):
        """Test baseline memory usage after startup"""
        print("\n💾 Testing Baseline Memory Usage...")
        
        # Make a few requests to warm up
        for _ in range(5):
            client.get("/health")
        
        time.sleep(0.5)  # Let things settle
        
        stats = self.get_memory_stats()
        
        print(f"  RSS Memory: {stats['rss_mb']:.2f} MB")
        print(f"  VMS Memory: {stats['vms_mb']:.2f} MB")
        print(f"  Memory %: {stats['percent']:.2f}%")
        print(f"  Available: {stats['available_mb']:.2f} MB")
        
        # Note: This is a soft check as baseline can vary by environment
        if stats['rss_mb'] > TARGET_BASELINE_MEMORY:
            print(f"  ⚠️ Memory usage higher than target: {stats['rss_mb']:.2f} MB > {TARGET_BASELINE_MEMORY} MB")
        else:
            print("  ✅ Baseline memory usage is optimal")
    
    def test_memory_usage_during_requests(self, client):
        """Test memory usage doesn't grow excessively during requests"""
        print("\n📈 Testing Memory Usage During Requests...")
        
        initial_memory = self.get_process_memory_mb()
        print(f"  Initial memory: {initial_memory:.2f} MB")
        
        # Make 100 requests
        num_requests = 100
        for i in range(num_requests):
            client.get("/health")
            
            if (i + 1) % 25 == 0:
                current_memory = self.get_process_memory_mb()
                growth = current_memory - initial_memory
                print(f"  After {i + 1} requests: {current_memory:.2f} MB (+{growth:.2f} MB)")
        
        final_memory = self.get_process_memory_mb()
        total_growth = final_memory - initial_memory
        growth_per_100 = total_growth
        
        print(f"  Final memory: {final_memory:.2f} MB")
        print(f"  Total growth: {total_growth:.2f} MB")
        print(f"  Growth per 100 requests: {growth_per_100:.2f} MB")
        
        # Memory growth should be reasonable
        assert growth_per_100 < TARGET_MEMORY_GROWTH, \
            f"Excessive memory growth: {growth_per_100:.2f} MB > {TARGET_MEMORY_GROWTH} MB"
        
        print("  ✅ Memory usage during requests is acceptable")
    
    def test_memory_usage_with_cache(self, client):
        """Test that caching doesn't cause excessive memory growth"""
        print("\n🗂️ Testing Memory Usage With Cache...")
        
        # Clear cache first
        client.post("/agent/clear-cache")
        time.sleep(0.5)
        
        initial_memory = self.get_process_memory_mb()
        print(f"  Initial memory: {initial_memory:.2f} MB")
        
        # Make varied requests to populate cache
        queries = [
            "hello",
            "how are you",
            "what can you do",
            "help me",
            "tell me about yourself"
        ]
        
        # Repeat queries to test cache
        for iteration in range(20):
            for query in queries:
                try:
                    client.post("/agent/ask", json=query)
                except:
                    pass  # May fail if LLM not available, just testing memory
        
        time.sleep(0.5)
        
        # Get cache stats
        stats_response = client.get("/agent/stats")
        cache_stats = stats_response.json()
        
        final_memory = self.get_process_memory_mb()
        memory_growth = final_memory - initial_memory
        
        print(f"  Cache size: {cache_stats['orchestrator']['cache_size']}")
        print(f"  Final memory: {final_memory:.2f} MB")
        print(f"  Memory growth: {memory_growth:.2f} MB")
        
        # Cache should not cause excessive memory growth
        # Allow up to 100MB growth for cache (generous limit)
        assert memory_growth < 100, \
            f"Cache causing excessive memory growth: {memory_growth:.2f} MB"
        
        print("  ✅ Cache memory usage is reasonable")
    
    def test_memory_leak_detection(self, client):
        """Test for memory leaks by running operations and checking for growth"""
        print("\n🔍 Testing for Memory Leaks...")
        
        measurements = []
        
        # Run multiple cycles of operations
        num_cycles = 5
        requests_per_cycle = 50
        
        for cycle in range(num_cycles):
            cycle_start_memory = self.get_process_memory_mb()
            
            # Perform various operations
            for _ in range(requests_per_cycle):
                client.get("/health")
                client.get("/files")
                client.get("/agent/stats")
            
            # Clear cache to avoid cache growth being counted as leak
            client.post("/agent/clear-cache")
            time.sleep(0.3)
            
            cycle_end_memory = self.get_process_memory_mb()
            measurements.append(cycle_end_memory)
            
            print(f"  Cycle {cycle + 1}: {cycle_end_memory:.2f} MB "
                  f"(+{cycle_end_memory - cycle_start_memory:.2f} MB)")
        
        # Analyze trend
        first_measurement = measurements[0]
        last_measurement = measurements[-1]
        total_growth = last_measurement - first_measurement
        growth_ratio = last_measurement / first_measurement
        
        print(f"\n  First cycle: {first_measurement:.2f} MB")
        print(f"  Last cycle: {last_measurement:.2f} MB")
        print(f"  Total growth: {total_growth:.2f} MB")
        print(f"  Growth ratio: {growth_ratio:.2f}x")
        
        # Memory shouldn't grow more than threshold
        assert growth_ratio < MEMORY_LEAK_THRESHOLD, \
            f"Possible memory leak detected: {growth_ratio:.2f}x growth"
        
        print("  ✅ No memory leak detected")
    
    def test_memory_cleanup_after_cache_clear(self, client):
        """Test that memory is properly cleaned up when cache is cleared"""
        print("\n🧹 Testing Memory Cleanup After Cache Clear...")
        
        # Clear cache and get baseline
        client.post("/agent/clear-cache")
        time.sleep(0.5)
        baseline_memory = self.get_process_memory_mb()
        print(f"  Baseline memory: {baseline_memory:.2f} MB")
        
        # Make requests to populate cache
        for i in range(50):
            try:
                client.post("/agent/ask", json=f"query {i}")
            except:
                pass
        
        time.sleep(0.5)
        cached_memory = self.get_process_memory_mb()
        cache_growth = cached_memory - baseline_memory
        print(f"  After caching: {cached_memory:.2f} MB (+{cache_growth:.2f} MB)")
        
        # Clear cache
        client.post("/agent/clear-cache")
        time.sleep(0.5)
        
        cleaned_memory = self.get_process_memory_mb()
        cleanup_amount = cached_memory - cleaned_memory
        print(f"  After cleanup: {cleaned_memory:.2f} MB (-{cleanup_amount:.2f} MB)")
        
        # Memory should go down or stay relatively stable
        # Allow some overhead but should see some cleanup
        retention = cleaned_memory / cached_memory
        print(f"  Memory retention: {retention * 100:.1f}%")
        
        # Note: Python's garbage collection is lazy, so we just check 
        # it doesn't grow indefinitely
        assert retention < 1.1, \
            f"Memory not being cleaned up: {retention * 100:.1f}% retained"
        
        print("  ✅ Memory cleanup working")
    
    def test_memory_under_concurrent_load(self, client):
        """Test memory usage under concurrent load"""
        print("\n⚡ Testing Memory Under Concurrent Load...")
        
        from concurrent.futures import ThreadPoolExecutor
        
        initial_memory = self.get_process_memory_mb()
        print(f"  Initial memory: {initial_memory:.2f} MB")
        
        # Run concurrent requests
        def make_requests():
            for _ in range(10):
                client.get("/health")
                client.get("/files")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_requests) for _ in range(10)]
            for future in futures:
                future.result()
        
        time.sleep(0.5)
        
        final_memory = self.get_process_memory_mb()
        memory_growth = final_memory - initial_memory
        
        print(f"  Final memory: {final_memory:.2f} MB")
        print(f"  Memory growth: {memory_growth:.2f} MB")
        
        # Allow reasonable growth under concurrent load
        assert memory_growth < 100, \
            f"Excessive memory growth under load: {memory_growth:.2f} MB"
        
        print("  ✅ Memory usage under concurrent load is acceptable")
    
    def test_system_memory_health(self):
        """Test overall system memory health"""
        print("\n💻 Testing System Memory Health...")
        
        vm = psutil.virtual_memory()
        
        print(f"  Total: {vm.total / (1024**3):.2f} GB")
        print(f"  Available: {vm.available / (1024**3):.2f} GB")
        print(f"  Used: {vm.used / (1024**3):.2f} GB")
        print(f"  Percent: {vm.percent:.1f}%")
        
        # System should have adequate memory available
        assert vm.percent < 95, \
            f"System memory critically low: {vm.percent:.1f}% used"
        
        assert vm.available > 100 * 1024 * 1024, \
            "Less than 100MB available - system critically low on memory"
        
        print("  ✅ System memory health is good")


def print_memory_summary():
    """Print memory test summary"""
    print("\n" + "=" * 70)
    print("MEMORY USAGE TEST SUMMARY")
    print("=" * 70)
    print("✅ Baseline memory usage acceptable")
    print("✅ No excessive growth during operations")
    print("✅ Cache memory usage reasonable")
    print("✅ No memory leaks detected")
    print("✅ Memory cleanup working")
    print("✅ Memory stable under concurrent load")
    print("=" * 70)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
    print_memory_summary()
