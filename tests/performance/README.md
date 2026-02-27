# Performance Testing Guide

This directory contains comprehensive performance tests for the Antigravity Workspace Backend.

## Test Suite Overview

### 1. API Response Times (`test_api_response_times.py`)
Tests response times for all major API endpoints and validates performance targets.

**What it tests:**
- Health check endpoint performance
- Root endpoint response time
- File listing performance
- Agent statistics retrieval
- Performance monitoring endpoints
- Cache warming effectiveness
- Response time consistency
- End-to-end workflow performance

**Performance targets:**
- Health checks: < 100ms
- Simple queries: < 1s
- Complex queries: < 3s
- File operations: < 200ms

### 2. Concurrent Request Handling (`test_concurrent_requests.py`)
Measures system behavior under concurrent load with multiple simultaneous users.

**What it tests:**
- Low concurrency (10 concurrent requests)
- Medium concurrency (50 concurrent requests)
- High concurrency (100 concurrent requests)
- Mixed endpoint concurrency
- Sustained load testing
- Maximum throughput measurement

**Success criteria:**
- 100% success rate at low concurrency
- >95% success rate at medium concurrency
- >90% success rate at high concurrency
- Minimal performance degradation over time

### 3. Memory Usage Patterns (`test_memory_usage.py`)
Monitors memory usage and detects memory leaks.

**What it tests:**
- Baseline memory usage
- Memory growth during operations
- Cache memory impact
- Memory leak detection (5 cycles)
- Memory cleanup after cache clear
- Memory under concurrent load
- System memory health

**Thresholds:**
- Baseline memory: < 200MB
- Growth per 100 requests: < 50MB
- Memory leak threshold: < 20% growth
- Cache memory: < 1% of baseline

### 4. Cache Efficiency (`test_cache_efficiency.py`)
Validates cache effectiveness and performance impact.

**What it tests:**
- Cache hit rate for repeated queries
- Cache speedup measurement
- Cache size management with LRU
- Cache TTL verification
- Cache warming functionality
- Vector store query caching
- Combined cache efficiency
- Cache clear functionality

**Targets:**
- Hit rate: >80% for repeated queries
- Speedup: >2x for cached responses
- Cache size: Properly bounded
- TTL: Working correctly

## Running Tests

### Prerequisites

```bash
# Install dependencies
pip install pytest pytest-asyncio httpx psutil statistics

# Ensure backend is running (for integration tests)
cd backend
python main.py
```

### Run All Performance Tests

```bash
# From project root
pytest tests/performance/ -v -s

# With detailed output
pytest tests/performance/ -v -s --tb=short

# Generate HTML report
pytest tests/performance/ --html=reports/performance.html --self-contained-html
```

### Run Individual Test Files

```bash
# Response time tests
pytest tests/performance/test_api_response_times.py -v -s

# Concurrency tests
pytest tests/performance/test_concurrent_requests.py -v -s

# Memory tests
pytest tests/performance/test_memory_usage.py -v -s

# Cache tests
pytest tests/performance/test_cache_efficiency.py -v -s
```

### Run Specific Tests

```bash
# Run a specific test
pytest tests/performance/test_api_response_times.py::TestAPIResponseTimes::test_health_check_response_time -v -s

# Run tests matching a pattern
pytest tests/performance/ -k "cache" -v -s
```

## Test Output

### Success Output Example
```
🏥 Testing Health Check Response Time...
  Min: 28.45ms
  Mean: 45.23ms
  Median: 42.18ms
  P95: 68.92ms
  P99: 82.35ms
  Max: 95.12ms
  ✅ Health check response time is optimal
```

### Performance Metrics Displayed
- **Min**: Fastest response time
- **Max**: Slowest response time
- **Mean**: Average response time
- **Median**: Middle value (50th percentile)
- **P95**: 95th percentile (95% of requests faster)
- **P99**: 99th percentile (99% of requests faster)
- **StdDev**: Standard deviation (consistency)

## Interpreting Results

### Response Times
- **Excellent**: < 100ms
- **Good**: 100-500ms
- **Acceptable**: 500-1000ms
- **Slow**: > 1000ms

### Cache Hit Rates
- **Excellent**: > 80%
- **Good**: 60-80%
- **Fair**: 40-60%
- **Poor**: < 40%

### Memory Growth
- **Healthy**: < 50MB per 100 requests
- **Acceptable**: 50-100MB per 100 requests
- **Concerning**: > 100MB per 100 requests

### Concurrency Success Rates
- **Excellent**: > 95%
- **Good**: 90-95%
- **Acceptable**: 85-90%
- **Poor**: < 85%

## Continuous Performance Testing

### In CI/CD Pipeline

Add to `.github/workflows/ci.yml`:

```yaml
- name: Run Performance Tests
  run: |
    pytest tests/performance/ \
      --tb=short \
      --junit-xml=reports/performance-junit.xml
      
- name: Upload Performance Report
  uses: actions/upload-artifact@v3
  with:
    name: performance-report
    path: reports/
```

### Performance Regression Detection

```python
# Example: Check for regressions
import json

def check_regression(current_metrics, baseline_metrics, threshold=1.1):
    """Check if performance has regressed"""
    for metric, value in current_metrics.items():
        baseline = baseline_metrics.get(metric, value)
        if value > baseline * threshold:
            print(f"⚠️ Regression detected: {metric}")
            print(f"   Current: {value}, Baseline: {baseline}")
            print(f"   Degradation: {(value/baseline - 1) * 100:.1f}%")
```

### Benchmarking Best Practices

1. **Consistent Environment**
   - Use same hardware/VMs
   - Close unnecessary applications
   - Run during off-peak hours

2. **Warm-up Period**
   - Make initial requests to warm up caches
   - Let system stabilize before measuring

3. **Multiple Iterations**
   - Run tests multiple times
   - Use median/P95 instead of just mean
   - Look for consistency

4. **Baseline Comparison**
   - Keep baseline metrics
   - Compare against previous runs
   - Track trends over time

## Troubleshooting

### Tests Fail Due to Backend Not Running

**Error:**
```
Connection refused: localhost:8000
```

**Solution:**
```bash
# Start backend in another terminal
cd backend
python main.py

# Or run tests with backend startup
./test-setup.sh
pytest tests/performance/ -v -s
```

### High Response Times

**Possible causes:**
- System under load
- LLM service slow/unavailable
- Network issues
- Cache not working

**Debug:**
```bash
# Check system resources
top
free -h

# Check backend logs
tail -f backend/logs/app.log

# Test cache
curl http://localhost:8000/agent/stats
```

### Memory Tests Failing

**Possible causes:**
- Other processes using memory
- Memory leak in application
- Cache growing too large

**Debug:**
```bash
# Check system memory
free -h
ps aux --sort=-%mem | head

# Check application memory
curl http://localhost:8000/performance/metrics
```

### Concurrency Tests Failing

**Possible causes:**
- System resource limits
- Rate limiting too strict
- Database connections exhausted

**Debug:**
```bash
# Check connection limits
ulimit -n

# Check rate limits in .env
cat .env | grep LIMIT

# Monitor connections
netstat -an | grep :8000 | wc -l
```

## Performance Optimization Tips

### 1. Improve Cache Hit Rate
- Warm cache on startup
- Increase cache size
- Extend TTL for stable data
- Implement cache hierarchy

### 2. Reduce Response Times
- Enable response compression
- Optimize database queries
- Use connection pooling
- Implement CDN for static assets

### 3. Handle More Concurrent Users
- Increase worker processes
- Use async operations
- Implement request queuing
- Scale horizontally

### 4. Reduce Memory Usage
- Clear expired cache entries
- Use generators for large data
- Implement pagination
- Profile memory usage

## Related Documentation

- **Performance Report**: `../docs/PERFORMANCE_REPORT.md`
- **Load Testing**: `../locustfile.py`
- **Configuration**: `../.env.example`
- **Monitoring**: `../backend/utils/performance.py`

## Contributing

When adding new performance tests:

1. Follow existing test patterns
2. Include clear documentation
3. Set reasonable targets
4. Add to CI/CD pipeline
5. Update this README

## Support

For performance issues or questions:
- Check the Performance Report
- Review backend logs
- Monitor system resources
- Run diagnostic tests
- Consult the troubleshooting guide

---

**Last Updated**: 2024
**Test Suite Version**: 2.0.0
