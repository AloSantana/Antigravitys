# Performance Dashboard - Quick Reference

## 🚀 Quick Start

### 1. Start Application
```bash
./start.sh
```

### 2. Access Dashboard
```
http://localhost:3000
```

### 3. Open Performance Tab
Click "📊 Performance" in the main navigation

## 📊 Dashboard Sections

### System Metrics
- **CPU**: Real-time CPU usage (%)
- **Memory**: RAM usage (%)
- **Disk**: Storage usage with gauge

### Cache Performance
- **Hit Rate**: Cache efficiency (%)
- **Stats**: Hits, misses, size
- **Chart**: Visual breakdown

### WebSocket
- **Active**: Current connections
- **History**: Total connections
- **Duration**: Average connection time
- **List**: Live connection details

### MCP Servers
- **Status**: Online/warning/offline indicators
- **Response Time**: Average (ms)
- **Success Rate**: Percentage
- **Requests**: Total count

### Request Analytics
- **Throughput**: Requests per minute
- **Response Time**: Average (ms)
- **Error Rate**: Percentage
- **Slowest**: Top 5 endpoints

## 🎛️ Controls

### Time Range
- **1m**: Last 1 minute
- **5m**: Last 5 minutes
- **15m**: Last 15 minutes (default)
- **1h**: Last 1 hour

### Actions
- **🔄 Refresh**: Update now
- **📥 Export**: Download JSON

## 🔌 API Endpoints

```bash
# Get all metrics
curl http://localhost:8000/performance/metrics

# Get metrics history
curl http://localhost:8000/performance/metrics/history?minutes=15

# WebSocket stats
curl http://localhost:8000/performance/websocket-stats

# Cache stats
curl http://localhost:8000/performance/cache-stats

# MCP stats
curl http://localhost:8000/performance/mcp-stats

# Request stats
curl http://localhost:8000/performance/request-stats

# Health check
curl http://localhost:8000/performance/health

# Analysis
curl http://localhost:8000/performance/analysis

# Report
curl http://localhost:8000/performance/report
```

## 🧪 Testing

```bash
# Run test suite
python test-performance-dashboard.py

# Expected: 10/10 tests pass
```

## 📱 Features

- ✅ Real-time updates (every 2 seconds)
- ✅ Interactive charts
- ✅ Responsive design
- ✅ Auto start/stop monitoring
- ✅ Export functionality
- ✅ Time range selection
- ✅ Color-coded status indicators

## 🎨 Status Indicators

- 🟢 **Green**: Healthy (>90%)
- 🟡 **Yellow**: Warning (70-90%)
- 🔴 **Red**: Critical (<70%)

## 💡 Tips

1. **Monitor During Load**: Use performance tab during high activity
2. **Check Trends**: Look for patterns in CPU/memory charts
3. **Optimize Cache**: Aim for >80% hit rate
4. **Watch Response Times**: Keep under 100ms average
5. **Export Data**: Save metrics for historical analysis

## ⚙️ Configuration

### Update Interval
Default: 2 seconds
Location: `frontend/index.html` line ~2640

### Data Retention
Default: 60 data points (2 minutes at 2s intervals)
Location: `frontend/index.html` line ~2642

### Chart Colors
- CPU: Blue (#3b82f6)
- Memory: Purple (#8b5cf6)
- Cache Hits: Green (#10b981)
- Cache Misses: Red (#ef4444)
- Response Time: Orange (#f59e0b)

## 🐛 Troubleshooting

### No Data Showing
1. Check backend is running: `ps aux | grep python`
2. Verify endpoint: `curl http://localhost:8000/performance/metrics`
3. Check browser console for errors

### Charts Not Updating
1. Ensure Performance tab is active
2. Check browser console
3. Verify WebSocket connection
4. Refresh page

### High CPU Usage
1. Close Performance tab when not needed
2. Increase update interval
3. Reduce data point history

## 📊 Metrics Interpretation

### CPU Usage
- **< 50%**: Normal
- **50-80%**: Moderate
- **> 80%**: High (investigate)

### Memory Usage
- **< 60%**: Normal
- **60-80%**: Moderate
- **> 80%**: High (investigate)

### Disk Usage
- **< 70%**: Normal
- **70-90%**: Warning
- **> 90%**: Critical

### Cache Hit Rate
- **> 80%**: Excellent
- **60-80%**: Good
- **40-60%**: Fair
- **< 40%**: Poor (optimize)

### Response Time
- **< 50ms**: Excellent
- **50-100ms**: Good
- **100-500ms**: Acceptable
- **> 500ms**: Slow (optimize)

### Error Rate
- **< 1%**: Excellent
- **1-5%**: Acceptable
- **> 5%**: High (investigate)

## 🎯 Quick Optimization Guide

### High CPU
1. Check slowest endpoints
2. Review MCP server response times
3. Optimize expensive operations

### High Memory
1. Check cache size
2. Review active connections
3. Look for memory leaks

### Low Cache Hit Rate
1. Increase cache size
2. Review cache strategy
3. Adjust TTL settings

### Slow Response Times
1. Check database queries
2. Review MCP server performance
3. Enable caching where possible

## 📚 Resources

- Full Documentation: `PHASE4_PERFORMANCE_DASHBOARD.md`
- Test Script: `test-performance-dashboard.py`
- Backend Code: `backend/utils/performance.py`
- Frontend Code: `frontend/index.html` (Performance section)

## 🎉 Success!

Performance Dashboard is ready to use. Monitor your application in real-time and optimize based on the insights provided.
