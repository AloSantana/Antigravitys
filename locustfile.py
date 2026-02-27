"""
Locust Load Testing Configuration for Antigravity Workspace
Run with: locust -f locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between, events
import random
import time
import json
from typing import List

# Test data
SAMPLE_QUERIES = [
    "hello",
    "help",
    "what can you do",
    "status",
    "tell me about yourself",
    "how does this work",
    "explain the architecture",
    "what features do you have",
    "show me examples",
    "give me information",
]

SAMPLE_FILE_CONTENT = b"# Test Document\n\nThis is a test document for performance testing.\n\n## Features\n\n- Feature 1\n- Feature 2\n- Feature 3\n"


class AntigravityUser(HttpUser):
    """
    Simulated user behavior for Antigravity Workspace
    """
    
    # Wait time between tasks (1-5 seconds)
    wait_time = between(1, 5)
    
    def on_start(self):
        """Called when a simulated user starts"""
        self.query_count = 0
        self.cache_hits = 0
        print(f"User {self.environment.runner.user_count} started")
    
    @task(10)
    def health_check(self):
        """Check system health (common operation)"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(5)
    def get_files(self):
        """List files in drop zone"""
        with self.client.get("/files", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Get files failed: {response.status_code}")
    
    @task(8)
    def get_agent_stats(self):
        """Get agent statistics"""
        with self.client.get("/agent/stats", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                # Track cache performance
                if 'orchestrator' in data:
                    hit_rate = data['orchestrator'].get('hit_rate', 0)
                    if hit_rate > 0:
                        self.cache_hits += 1
                response.success()
            else:
                response.failure(f"Get stats failed: {response.status_code}")
    
    @task(3)
    def ask_agent(self):
        """Ask agent a question"""
        query = random.choice(SAMPLE_QUERIES)
        
        with self.client.post("/agent/ask", 
                             json=query,
                             catch_response=True,
                             name="/agent/ask") as response:
            if response.status_code == 200:
                self.query_count += 1
                
                # Check if response was cached
                try:
                    data = response.json()
                    if data.get('from_cache', False):
                        self.cache_hits += 1
                        response.success()
                    else:
                        response.success()
                except (json.JSONDecodeError, ValueError, KeyError):
                    # Response may not be JSON or may be malformed
                    # Still mark as success if the request completed
                    response.success()
            else:
                response.failure(f"Agent query failed: {response.status_code}")
    
    @task(2)
    def get_performance_metrics(self):
        """Get performance metrics"""
        with self.client.get("/performance/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Get metrics failed: {response.status_code}")
    
    @task(2)
    def get_performance_health(self):
        """Get performance health status"""
        with self.client.get("/performance/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Get performance health failed: {response.status_code}")
    
    @task(1)
    def get_performance_summary(self):
        """Get performance summary"""
        with self.client.get("/performance/summary", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Get summary failed: {response.status_code}")
    
    @task(1)
    def clear_cache(self):
        """Clear cache (maintenance operation)"""
        with self.client.post("/agent/clear-cache", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Clear cache failed: {response.status_code}")


class AdminUser(HttpUser):
    """
    Simulated admin user performing maintenance operations
    """
    
    wait_time = between(5, 15)  # Less frequent operations
    
    @task(5)
    def get_detailed_stats(self):
        """Get detailed statistics"""
        self.client.get("/agent/stats")
    
    @task(3)
    def get_performance_analysis(self):
        """Get performance analysis"""
        self.client.get("/performance/analysis")
    
    @task(2)
    def get_performance_report(self):
        """Get performance report"""
        self.client.get("/performance/report")
    
    @task(1)
    def warm_cache(self):
        """Warm the cache"""
        self.client.post("/agent/warm-cache")


# Event handlers for custom statistics

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    print("\n" + "=" * 70)
    print("LOAD TEST STARTING")
    print("=" * 70)
    print(f"Target host: {environment.host}")
    print("=" * 70 + "\n")


@events.test_stop.add_listener  
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    print("\n" + "=" * 70)
    print("LOAD TEST COMPLETED")
    print("=" * 70)
    
    # Print statistics
    stats = environment.stats
    
    print(f"\nTotal Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Failure Rate: {stats.total.fail_ratio * 100:.2f}%")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Median Response Time: {stats.total.median_response_time:.2f}ms")
    print(f"95th Percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"99th Percentile: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"Max Response Time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")
    
    print("\n" + "=" * 70)
    print("TOP ENDPOINTS BY REQUEST COUNT")
    print("=" * 70)
    
    # Sort by request count
    sorted_stats = sorted(stats.entries.values(), key=lambda x: x.num_requests, reverse=True)
    for i, stat in enumerate(sorted_stats[:10], 1):
        print(f"{i}. {stat.name}")
        print(f"   Requests: {stat.num_requests}, "
              f"Failures: {stat.num_failures}, "
              f"Avg: {stat.avg_response_time:.2f}ms, "
              f"P95: {stat.get_response_time_percentile(0.95):.2f}ms")
    
    print("\n" + "=" * 70)
    print("SLOWEST ENDPOINTS (by P95)")
    print("=" * 70)
    
    # Sort by P95 response time
    sorted_by_p95 = sorted(
        [s for s in stats.entries.values() if s.num_requests > 0],
        key=lambda x: x.get_response_time_percentile(0.95),
        reverse=True
    )
    for i, stat in enumerate(sorted_by_p95[:10], 1):
        print(f"{i}. {stat.name}")
        print(f"   P95: {stat.get_response_time_percentile(0.95):.2f}ms, "
              f"Avg: {stat.avg_response_time:.2f}ms, "
              f"Requests: {stat.num_requests}")
    
    print("\n" + "=" * 70)


# Custom shapes for different load patterns

from locust import LoadTestShape

class StepLoadShape(LoadTestShape):
    """
    Step load pattern: gradually increase users
    """
    
    step_time = 30  # seconds per step
    step_load = 10  # users per step
    spawn_rate = 2  # users per second
    time_limit = 300  # 5 minutes total
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time > self.time_limit:
            return None
        
        current_step = int(run_time // self.step_time)
        return (current_step + 1) * self.step_load, self.spawn_rate


class SpikeLoadShape(LoadTestShape):
    """
    Spike load pattern: sudden increases in traffic
    """
    
    time_limit = 300  # 5 minutes total
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time > self.time_limit:
            return None
        
        # Pattern: 10 users -> spike to 50 -> back to 10 -> spike to 100 -> back to 10
        if run_time < 60:
            return 10, 2
        elif run_time < 90:
            return 50, 5
        elif run_time < 150:
            return 10, 2
        elif run_time < 180:
            return 100, 10
        else:
            return 10, 2


class WaveLoadShape(LoadTestShape):
    """
    Wave load pattern: oscillating user count
    """
    
    time_limit = 300  # 5 minutes
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time > self.time_limit:
            return None
        
        # Sine wave pattern
        import math
        user_count = int(25 + 25 * math.sin(run_time / 30))
        return user_count, 2


# Usage instructions
"""
Load Testing Instructions:

1. Basic test with default settings:
   locust -f locustfile.py --host=http://localhost:8000

2. Headless mode with specific parameters:
   locust -f locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 5 --run-time 5m --headless

3. With step load pattern:
   locust -f locustfile.py --host=http://localhost:8000 --headless --users 100 --spawn-rate 10

4. Quick test:
   locust -f locustfile.py --host=http://localhost:8000 --users 20 --spawn-rate 4 --run-time 2m --headless

5. Stress test:
   locust -f locustfile.py --host=http://localhost:8000 --users 200 --spawn-rate 20 --run-time 10m --headless

6. View web UI:
   locust -f locustfile.py --host=http://localhost:8000
   Then open http://localhost:8089

Performance Targets:
- Response time P95 < 500ms for light load
- Response time P95 < 1000ms for heavy load
- Error rate < 1% under normal load
- Throughput > 100 requests/second
- Cache hit rate > 50% for repeated queries
"""
