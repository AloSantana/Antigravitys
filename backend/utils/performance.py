"""
Performance Monitoring and Optimization Tools
"""

import time
import psutil
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from collections import deque
import asyncio
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_usage_percent: float
    network_io_mb: Dict[str, float]
    process_count: int
    response_time_ms: Optional[float] = None


@dataclass
class WebSocketConnectionInfo:
    """WebSocket connection information"""
    connection_id: str
    connected_at: str
    duration_seconds: float
    status: str  # 'active', 'disconnected'
    messages_sent: int = 0
    messages_received: int = 0


@dataclass
class RequestStats:
    """Request statistics"""
    timestamp: str
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    success: bool


class StatsTracker:
    """
    Track various application statistics
    Thread-safe tracking of WebSocket connections, requests, and cache stats
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize stats tracker
        
        Args:
            max_history: Maximum number of historical items to keep
        """
        self.max_history = max_history
        self.lock = Lock()
        
        # WebSocket tracking
        self.active_websockets: Dict[str, WebSocketConnectionInfo] = {}
        self.websocket_history: deque = deque(maxlen=max_history)
        self.total_websocket_connections = 0
        
        # Request tracking
        self.request_history: deque = deque(maxlen=max_history)
        self.requests_by_endpoint: Dict[str, int] = {}
        self.total_requests = 0
        self.total_errors = 0
        
        # Cache tracking
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_size = 0
        
        # MCP server tracking
        self.mcp_response_times: Dict[str, List[float]] = {}
        self.mcp_success_count: Dict[str, int] = {}
        self.mcp_failure_count: Dict[str, int] = {}
        
    def track_websocket_connect(self, connection_id: str) -> None:
        """Track new WebSocket connection"""
        with self.lock:
            conn_info = WebSocketConnectionInfo(
                connection_id=connection_id,
                connected_at=datetime.now(timezone.utc).isoformat(),
                duration_seconds=0,
                status='active'
            )
            self.active_websockets[connection_id] = conn_info
            self.total_websocket_connections += 1
            
    def track_websocket_disconnect(self, connection_id: str) -> None:
        """Track WebSocket disconnection"""
        with self.lock:
            if connection_id in self.active_websockets:
                conn = self.active_websockets[connection_id]
                conn.status = 'disconnected'
                connected_time = datetime.fromisoformat(conn.connected_at)
                conn.duration_seconds = (datetime.now(timezone.utc) - connected_time).total_seconds()
                
                # Move to history
                self.websocket_history.append(asdict(conn))
                del self.active_websockets[connection_id]
                
    def track_websocket_message(self, connection_id: str, direction: str) -> None:
        """
        Track WebSocket message
        
        Args:
            connection_id: Connection identifier
            direction: 'sent' or 'received'
        """
        with self.lock:
            if connection_id in self.active_websockets:
                conn = self.active_websockets[connection_id]
                if direction == 'sent':
                    conn.messages_sent += 1
                elif direction == 'received':
                    conn.messages_received += 1
                    
    def track_request(self, endpoint: str, method: str, response_time_ms: float, 
                     status_code: int, success: bool) -> None:
        """Track HTTP request"""
        with self.lock:
            stats = RequestStats(
                timestamp=datetime.now(timezone.utc).isoformat(),
                endpoint=endpoint,
                method=method,
                response_time_ms=response_time_ms,
                status_code=status_code,
                success=success
            )
            self.request_history.append(asdict(stats))
            
            # Update counters
            self.total_requests += 1
            if not success:
                self.total_errors += 1
                
            # Track by endpoint
            if endpoint not in self.requests_by_endpoint:
                self.requests_by_endpoint[endpoint] = 0
            self.requests_by_endpoint[endpoint] += 1
            
    def track_cache_access(self, hit: bool, size: int) -> None:
        """
        Track cache access
        
        Args:
            hit: Whether it was a cache hit
            size: Current cache size
        """
        with self.lock:
            if hit:
                self.cache_hits += 1
            else:
                self.cache_misses += 1
            self.cache_size = size
            
    def track_mcp_request(self, server_name: str, response_time_ms: float, success: bool) -> None:
        """
        Track MCP server request
        
        Args:
            server_name: Name of MCP server
            response_time_ms: Response time in milliseconds
            success: Whether request succeeded
        """
        with self.lock:
            # Track response times
            if server_name not in self.mcp_response_times:
                self.mcp_response_times[server_name] = []
            self.mcp_response_times[server_name].append(response_time_ms)
            
            # Keep only last 100 samples per server
            if len(self.mcp_response_times[server_name]) > 100:
                self.mcp_response_times[server_name] = self.mcp_response_times[server_name][-100:]
                
            # Track success/failure
            if success:
                self.mcp_success_count[server_name] = self.mcp_success_count.get(server_name, 0) + 1
            else:
                self.mcp_failure_count[server_name] = self.mcp_failure_count.get(server_name, 0) + 1
                
    def get_websocket_stats(self) -> Dict[str, Any]:
        """Get WebSocket statistics"""
        with self.lock:
            active_connections = len(self.active_websockets)
            history_list = list(self.websocket_history)
            
            # Calculate average duration from history
            avg_duration = 0
            if history_list:
                durations = [h['duration_seconds'] for h in history_list]
                avg_duration = sum(durations) / len(durations)
                
            return {
                'active_connections': active_connections,
                'total_connections': self.total_websocket_connections,
                'average_duration_seconds': avg_duration,
                'active_connections_list': [asdict(c) for c in self.active_websockets.values()],
                'recent_history': history_list[-100:]  # Last 100 connections
            }
            
    def get_request_stats(self) -> Dict[str, Any]:
        """Get request statistics"""
        with self.lock:
            request_list = list(self.request_history)
            
            # Calculate metrics from last minute
            one_minute_ago = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
            recent_requests = [r for r in request_list if r['timestamp'] > one_minute_ago]
            
            # Calculate average response time
            avg_response_time = 0
            if request_list:
                response_times = [r['response_time_ms'] for r in request_list]
                avg_response_time = sum(response_times) / len(response_times)
                
            # Calculate error rate
            error_rate = 0
            if self.total_requests > 0:
                error_rate = (self.total_errors / self.total_requests) * 100
                
            # Find slowest endpoints
            endpoint_times: Dict[str, List[float]] = {}
            for req in request_list:
                endpoint = req['endpoint']
                if endpoint not in endpoint_times:
                    endpoint_times[endpoint] = []
                endpoint_times[endpoint].append(req['response_time_ms'])
                
            slowest_endpoints = []
            for endpoint, times in endpoint_times.items():
                slowest_endpoints.append({
                    'endpoint': endpoint,
                    'avg_time_ms': sum(times) / len(times),
                    'max_time_ms': max(times),
                    'count': len(times)
                })
            slowest_endpoints.sort(key=lambda x: x['avg_time_ms'], reverse=True)
            
            return {
                'total_requests': self.total_requests,
                'total_errors': self.total_errors,
                'error_rate_percent': error_rate,
                'requests_per_minute': len(recent_requests),
                'average_response_time_ms': avg_response_time,
                'requests_by_endpoint': self.requests_by_endpoint,
                'slowest_endpoints': slowest_endpoints[:10],  # Top 10
                'recent_requests': request_list[-100:]  # Last 100 requests
            }
            
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_accesses = self.cache_hits + self.cache_misses
            hit_rate = 0
            if total_accesses > 0:
                hit_rate = (self.cache_hits / total_accesses) * 100
                
            return {
                'size': self.cache_size,
                'hits': self.cache_hits,
                'misses': self.cache_misses,
                'total_accesses': total_accesses,
                'hit_rate_percent': hit_rate
            }
            
    def get_mcp_stats(self) -> Dict[str, Any]:
        """Get MCP server statistics"""
        with self.lock:
            mcp_servers = {}
            
            for server_name in set(list(self.mcp_response_times.keys()) + 
                                  list(self.mcp_success_count.keys()) + 
                                  list(self.mcp_failure_count.keys())):
                times = self.mcp_response_times.get(server_name, [])
                successes = self.mcp_success_count.get(server_name, 0)
                failures = self.mcp_failure_count.get(server_name, 0)
                total = successes + failures
                
                avg_time = sum(times) / len(times) if times else 0
                success_rate = (successes / total * 100) if total > 0 else 0
                
                mcp_servers[server_name] = {
                    'average_response_time_ms': avg_time,
                    'min_response_time_ms': min(times) if times else 0,
                    'max_response_time_ms': max(times) if times else 0,
                    'success_count': successes,
                    'failure_count': failures,
                    'total_requests': total,
                    'success_rate_percent': success_rate,
                    'recent_times': times[-20:]  # Last 20 response times
                }
                
            return mcp_servers


# Global stats tracker instance
_global_stats_tracker: Optional[StatsTracker] = None


def get_stats_tracker() -> StatsTracker:
    """Get or create global stats tracker"""
    global _global_stats_tracker
    if _global_stats_tracker is None:
        _global_stats_tracker = StatsTracker()
    return _global_stats_tracker


# Import timedelta for time calculations
from datetime import timedelta


class PerformanceMonitor:
    """
    Monitor system and application performance
    Track metrics and identify bottlenecks
    """
    
    def __init__(self, metrics_file: str = "logs/performance_metrics.json"):
        """
        Initialize performance monitor
        
        Args:
            metrics_file: Path to metrics storage file
        """
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_history: deque = deque(maxlen=120)  # Keep last 120 samples (2 hours at 1/min)
        self.start_time = time.time()
        self.stats_tracker = get_stats_tracker()
        
    def capture_metrics(self) -> PerformanceMetrics:
        """
        Capture current system performance metrics
        
        Returns:
            PerformanceMetrics object
        """
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_mb = memory.used / (1024 * 1024)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Network I/O
        net_io = psutil.net_io_counters()
        network_io_mb = {
            'sent': net_io.bytes_sent / (1024 * 1024),
            'recv': net_io.bytes_recv / (1024 * 1024)
        }
        
        # Process count
        process_count = len(psutil.pids())
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_mb=memory_mb,
            disk_usage_percent=disk_percent,
            network_io_mb=network_io_mb,
            process_count=process_count
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health status
        
        Returns:
            Health status dictionary
        """
        if not self.metrics_history:
            self.capture_metrics()
        
        current = self.metrics_history[-1]
        
        # Determine health status
        health_score = 100
        warnings = []
        
        if current.cpu_percent > 80:
            health_score -= 20
            warnings.append("High CPU usage")
        
        if current.memory_percent > 80:
            health_score -= 20
            warnings.append("High memory usage")
        
        if current.disk_usage_percent > 90:
            health_score -= 15
            warnings.append("Low disk space")
        
        status = "healthy"
        if health_score < 50:
            status = "critical"
        elif health_score < 70:
            status = "warning"
        
        return {
            'status': status,
            'health_score': health_score,
            'warnings': warnings,
            'uptime_seconds': time.time() - self.start_time,
            'metrics': asdict(current)
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary statistics
        
        Returns:
            Summary dictionary
        """
        if not self.metrics_history:
            return {}
        
        metrics_list = list(self.metrics_history)
        cpu_values = [m.cpu_percent for m in metrics_list]
        memory_values = [m.memory_percent for m in metrics_list]
        
        return {
            'cpu': {
                'current': cpu_values[-1],
                'average': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'current': memory_values[-1],
                'average': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values)
            },
            'uptime_seconds': time.time() - self.start_time,
            'samples': len(self.metrics_history)
        }
        
    def get_metrics_history(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Get metrics history for specified time period
        
        Args:
            minutes: Number of minutes of history to return
            
        Returns:
            List of metrics dictionaries
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        metrics_list = list(self.metrics_history)
        
        filtered = []
        for m in metrics_list:
            try:
                metric_time = datetime.fromisoformat(m.timestamp)
                if metric_time >= cutoff_time:
                    filtered.append(asdict(m))
            except:
                # Include if we can't parse timestamp
                filtered.append(asdict(m))
                
        return filtered
    
    def save_metrics(self) -> None:
        """Save metrics history to file"""
        try:
            metrics_list = list(self.metrics_history)
            data = {
                'metrics': [asdict(m) for m in metrics_list[-100:]],  # Keep last 100
                'summary': self.get_performance_summary()
            }
            
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Metrics saved to {self.metrics_file}")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def load_metrics(self) -> None:
        """Load metrics history from file"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                
                self.metrics_history = [
                    PerformanceMetrics(**m) for m in data.get('metrics', [])
                ]
                
                logger.info(f"Loaded {len(self.metrics_history)} metric samples")
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")


class PerformanceOptimizer:
    """
    Analyze performance and provide optimization recommendations
    """
    
    @staticmethod
    def analyze_performance(monitor: PerformanceMonitor) -> Dict[str, Any]:
        """
        Analyze performance metrics and provide recommendations
        
        Args:
            monitor: PerformanceMonitor instance
            
        Returns:
            Analysis results with recommendations
        """
        health = monitor.get_system_health()
        summary = monitor.get_performance_summary()
        
        recommendations = []
        priority_actions = []
        
        # CPU Analysis
        if summary.get('cpu', {}).get('average', 0) > 70:
            recommendations.append({
                'type': 'cpu',
                'severity': 'high',
                'message': 'High CPU usage detected',
                'suggestions': [
                    'Profile application to identify CPU-intensive operations',
                    'Consider implementing caching for expensive computations',
                    'Use async operations for I/O-bound tasks',
                    'Scale horizontally if consistently high'
                ]
            })
            priority_actions.append('Optimize CPU-intensive operations')
        
        # Memory Analysis
        if summary.get('memory', {}).get('average', 0) > 70:
            recommendations.append({
                'type': 'memory',
                'severity': 'high',
                'message': 'High memory usage detected',
                'suggestions': [
                    'Profile memory usage to identify leaks',
                    'Implement pagination for large datasets',
                    'Use generators instead of lists where possible',
                    'Clear caches periodically',
                    'Consider increasing server memory'
                ]
            })
            priority_actions.append('Optimize memory usage')
        
        # Disk Analysis
        current_metrics = health['metrics']
        if current_metrics['disk_usage_percent'] > 85:
            recommendations.append({
                'type': 'disk',
                'severity': 'critical',
                'message': 'Low disk space',
                'suggestions': [
                    'Clean up old logs and temporary files',
                    'Archive or delete unused data',
                    'Implement log rotation',
                    'Consider increasing disk capacity'
                ]
            })
            priority_actions.append('Free up disk space')
        
        # General optimizations
        if not priority_actions:
            recommendations.append({
                'type': 'general',
                'severity': 'low',
                'message': 'System performing well',
                'suggestions': [
                    'Continue monitoring performance',
                    'Consider implementing caching if not already done',
                    'Review and optimize database queries',
                    'Enable compression for API responses'
                ]
            })
        
        return {
            'health': health,
            'summary': summary,
            'recommendations': recommendations,
            'priority_actions': priority_actions,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


def format_performance_report(analysis: Dict[str, Any]) -> str:
    """
    Format performance analysis as readable report
    
    Args:
        analysis: Analysis results
        
    Returns:
        Formatted report string
    """
    lines = []
    lines.append("=" * 60)
    lines.append("PERFORMANCE ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append("")
    
    # System Health
    health = analysis['health']
    lines.append(f"System Status: {health['status'].upper()}")
    lines.append(f"Health Score: {health['health_score']}/100")
    lines.append(f"Uptime: {health['uptime_seconds']:.0f} seconds")
    lines.append("")
    
    # Current Metrics
    metrics = health['metrics']
    lines.append("Current Metrics:")
    lines.append(f"  CPU Usage: {metrics['cpu_percent']:.1f}%")
    lines.append(f"  Memory Usage: {metrics['memory_percent']:.1f}% ({metrics['memory_mb']:.0f} MB)")
    lines.append(f"  Disk Usage: {metrics['disk_usage_percent']:.1f}%")
    lines.append("")
    
    # Warnings
    if health['warnings']:
        lines.append("⚠️  Warnings:")
        for warning in health['warnings']:
            lines.append(f"  - {warning}")
        lines.append("")
    
    # Priority Actions
    if analysis['priority_actions']:
        lines.append("🔴 Priority Actions:")
        for action in analysis['priority_actions']:
            lines.append(f"  - {action}")
        lines.append("")
    
    # Recommendations
    lines.append("📋 Recommendations:")
    for rec in analysis['recommendations']:
        lines.append(f"\n  [{rec['severity'].upper()}] {rec['message']}")
        for suggestion in rec['suggestions']:
            lines.append(f"    • {suggestion}")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


# FastAPI integration
def add_performance_endpoints(app):
    """
    Add performance monitoring endpoints to FastAPI app
    
    Args:
        app: FastAPI application instance
    """
    from fastapi import APIRouter, Query
    
    router = APIRouter(prefix="/performance", tags=["performance"])
    monitor = PerformanceMonitor()
    stats_tracker = get_stats_tracker()
    
    @router.get("/health")
    async def get_health():
        """Get system health status"""
        return monitor.get_system_health()
    
    @router.get("/metrics")
    async def get_metrics():
        """Get current performance metrics"""
        metrics = monitor.capture_metrics()
        
        # Also include stats
        return {
            'system': asdict(metrics),
            'websocket': stats_tracker.get_websocket_stats(),
            'requests': stats_tracker.get_request_stats(),
            'cache': stats_tracker.get_cache_stats(),
            'mcp': stats_tracker.get_mcp_stats()
        }
    
    @router.get("/metrics/history")
    async def get_metrics_history(minutes: int = Query(default=60, ge=1, le=120)):
        """
        Get metrics history for specified time period
        
        Args:
            minutes: Number of minutes of history (1-120)
        """
        return {
            'metrics': monitor.get_metrics_history(minutes),
            'period_minutes': minutes
        }
    
    @router.get("/summary")
    async def get_summary():
        """Get performance summary"""
        return monitor.get_performance_summary()
    
    @router.get("/analysis")
    async def get_analysis():
        """Get performance analysis with recommendations"""
        analysis = PerformanceOptimizer.analyze_performance(monitor)
        return analysis
    
    @router.get("/report")
    async def get_report():
        """Get formatted performance report"""
        analysis = PerformanceOptimizer.analyze_performance(monitor)
        report = format_performance_report(analysis)
        return {"report": report}
    
    @router.get("/websocket-stats")
    async def get_websocket_stats():
        """Get WebSocket connection statistics"""
        return stats_tracker.get_websocket_stats()
    
    @router.get("/mcp-stats")
    async def get_mcp_stats():
        """Get MCP server performance data"""
        return stats_tracker.get_mcp_stats()
    
    @router.get("/request-stats")
    async def get_request_stats():
        """Get request analytics"""
        return stats_tracker.get_request_stats()
    
    @router.get("/cache-stats")
    async def get_cache_stats():
        """Get cache performance metrics"""
        return stats_tracker.get_cache_stats()
    
    @router.post("/reset-stats")
    async def reset_stats():
        """Reset all statistics (for testing/debugging)"""
        global _global_stats_tracker
        _global_stats_tracker = StatsTracker()
        return {"message": "Statistics reset successfully"}
    
    app.include_router(router)
    
    # Background task to capture metrics periodically
    import asyncio
    
    async def capture_metrics_task():
        while True:
            try:
                monitor.capture_metrics()
            except Exception as e:
                logger.error(f"Error capturing metrics: {e}")
            await asyncio.sleep(60)  # Capture every minute
    
    @app.on_event("startup")
    async def startup_event():
        monitor.load_metrics()
        asyncio.create_task(capture_metrics_task())
    
    @app.on_event("shutdown")
    async def shutdown_event():
        monitor.save_metrics()
    
    # Return monitor and tracker for use in middleware
    return monitor, stats_tracker


def main():
    """Main function for testing performance monitor"""
    logging.basicConfig(level=logging.INFO)
    
    print("\nPerformance Monitor Test\n")
    
    # Create monitor
    monitor = PerformanceMonitor()
    
    # Capture some metrics
    for i in range(3):
        print(f"Capturing metrics ({i+1}/3)...")
        monitor.capture_metrics()
        time.sleep(1)
    
    # Get health status
    print("\n" + "=" * 60)
    print("System Health")
    print("=" * 60)
    health = monitor.get_system_health()
    print(f"Status: {health['status']}")
    print(f"Health Score: {health['health_score']}/100")
    if health['warnings']:
        print(f"Warnings: {', '.join(health['warnings'])}")
    
    # Get performance analysis
    print("\n")
    optimizer = PerformanceOptimizer()
    analysis = optimizer.analyze_performance(monitor)
    print(format_performance_report(analysis))
    
    # Save metrics
    monitor.save_metrics()
    print(f"\nMetrics saved to {monitor.metrics_file}")


if __name__ == "__main__":
    main()
