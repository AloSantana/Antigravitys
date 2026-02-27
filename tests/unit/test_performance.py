"""
Unit tests for backend.utils.performance module
Tests performance monitoring and optimization utilities
"""

import pytest


@pytest.mark.unit
class TestPerformanceMonitor:
    """Test suite for PerformanceMonitor class."""
    
    def test_initialization(self, temp_dir):
        """Test PerformanceMonitor initializes correctly."""
        from backend.utils.performance import PerformanceMonitor
        
        metrics_file = temp_dir / "metrics.json"
        monitor = PerformanceMonitor(metrics_file=str(metrics_file))
        
        assert monitor.metrics_file == metrics_file
        assert isinstance(monitor.metrics_history, list)
        assert monitor.start_time > 0
    
    def test_capture_metrics(self, mock_performance_monitor):
        """Test capturing performance metrics."""
        metrics = mock_performance_monitor.capture_metrics()
        
        assert hasattr(metrics, 'timestamp')
        assert hasattr(metrics, 'cpu_percent')
        assert hasattr(metrics, 'memory_percent')
        assert hasattr(metrics, 'disk_usage_percent')
        assert metrics.cpu_percent >= 0
        assert metrics.memory_percent >= 0
    
    def test_get_system_health(self, mock_performance_monitor):
        """Test getting system health status."""
        health = mock_performance_monitor.get_system_health()
        
        assert 'status' in health
        assert 'health_score' in health
        assert 'warnings' in health
        assert 'uptime_seconds' in health
        assert 'metrics' in health
        assert health['status'] in ['healthy', 'warning', 'critical']
    
    def test_get_performance_summary_empty(self, temp_dir):
        """Test performance summary with no history."""
        from backend.utils.performance import PerformanceMonitor
        
        monitor = PerformanceMonitor(metrics_file=str(temp_dir / "metrics.json"))
        monitor.metrics_history = []
        
        summary = monitor.get_performance_summary()
        
        assert summary == {}
    
    def test_get_performance_summary_with_data(self, mock_performance_monitor):
        """Test performance summary with data."""
        # Capture some metrics
        for _ in range(3):
            mock_performance_monitor.capture_metrics()
        
        summary = mock_performance_monitor.get_performance_summary()
        
        assert 'cpu' in summary
        assert 'memory' in summary
        assert 'uptime_seconds' in summary
        assert 'samples' in summary
        assert summary['samples'] >= 3
    
    def test_save_metrics(self, temp_dir):
        """Test saving metrics to file."""
        from backend.utils.performance import PerformanceMonitor
        
        metrics_file = temp_dir / "metrics.json"
        monitor = PerformanceMonitor(metrics_file=str(metrics_file))
        
        # Capture and save
        monitor.capture_metrics()
        monitor.save_metrics()
        
        assert metrics_file.exists()
    
    def test_load_metrics(self, temp_dir):
        """Test loading metrics from file."""
        from backend.utils.performance import PerformanceMonitor
        
        metrics_file = temp_dir / "metrics.json"
        
        # Create and save some metrics
        monitor1 = PerformanceMonitor(metrics_file=str(metrics_file))
        monitor1.capture_metrics()
        monitor1.save_metrics()
        
        # Load in new instance
        monitor2 = PerformanceMonitor(metrics_file=str(metrics_file))
        monitor2.load_metrics()
        
        assert len(monitor2.metrics_history) > 0


@pytest.mark.unit
class TestPerformanceOptimizer:
    """Test suite for PerformanceOptimizer class."""
    
    def test_analyze_performance(self, mock_performance_monitor):
        """Test performance analysis."""
        from backend.utils.performance import PerformanceOptimizer
        
        # Capture some metrics
        mock_performance_monitor.capture_metrics()
        
        analysis = PerformanceOptimizer.analyze_performance(mock_performance_monitor)
        
        assert 'health' in analysis
        assert 'summary' in analysis
        assert 'recommendations' in analysis
        assert 'priority_actions' in analysis
        assert isinstance(analysis['recommendations'], list)
    
    def test_format_performance_report(self, mock_performance_monitor):
        """Test formatting performance report."""
        from backend.utils.performance import PerformanceOptimizer, format_performance_report
        
        mock_performance_monitor.capture_metrics()
        analysis = PerformanceOptimizer.analyze_performance(mock_performance_monitor)
        
        report = format_performance_report(analysis)
        
        assert isinstance(report, str)
        assert "PERFORMANCE ANALYSIS REPORT" in report
        assert "System Status:" in report
