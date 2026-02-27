"""
Comprehensive tests for health_monitor.py

Tests all monitoring functions including:
- System resource monitoring
- Service availability checking
- Alert management
- Auto-restart functionality
- Daemon lifecycle
"""

import pytest
import tempfile
import shutil
import time
import json
import os
import signal
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from health_monitor import (
    SystemMonitor,
    ServiceMonitor,
    AlertManager,
    ServiceRestarter,
    HealthMonitor,
    SystemMetrics,
    ServiceStatus,
    HealthReport,
    ColorOutput
)


@pytest.fixture
def temp_project():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir)
    
    # Create logs directory
    (project_path / 'logs').mkdir()
    
    yield project_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return Mock()


class TestSystemMetrics:
    """Test SystemMetrics dataclass."""
    
    def test_create_metrics(self):
        """Test creating system metrics."""
        metrics = SystemMetrics(
            timestamp="2024-01-01T00:00:00",
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_available_mb=1024.0,
            disk_percent=70.0,
            disk_available_gb=50.0
        )
        
        assert metrics.cpu_percent == 50.0
        assert metrics.memory_percent == 60.0
        assert metrics.disk_percent == 70.0
    
    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = SystemMetrics(
            timestamp="2024-01-01T00:00:00",
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_available_mb=1024.0,
            disk_percent=70.0,
            disk_available_gb=50.0
        )
        
        metrics_dict = metrics.to_dict()
        
        assert metrics_dict['cpu_percent'] == 50.0
        assert metrics_dict['memory_percent'] == 60.0
        assert 'timestamp' in metrics_dict


class TestServiceStatus:
    """Test ServiceStatus dataclass."""
    
    def test_create_status(self):
        """Test creating service status."""
        status = ServiceStatus(
            name="test_service",
            status="up",
            response_time_ms=100.0,
            last_check="2024-01-01T00:00:00"
        )
        
        assert status.name == "test_service"
        assert status.status == "up"
        assert status.response_time_ms == 100.0
    
    def test_status_with_error(self):
        """Test service status with error."""
        status = ServiceStatus(
            name="failed_service",
            status="down",
            response_time_ms=None,
            last_check="2024-01-01T00:00:00",
            error="Connection refused"
        )
        
        assert status.status == "down"
        assert status.error == "Connection refused"
        assert status.response_time_ms is None


class TestHealthReport:
    """Test HealthReport dataclass."""
    
    def test_create_report(self):
        """Test creating health report."""
        metrics = SystemMetrics(
            timestamp="2024-01-01T00:00:00",
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_available_mb=1024.0,
            disk_percent=70.0,
            disk_available_gb=50.0
        )
        
        service_status = ServiceStatus(
            name="test",
            status="up",
            response_time_ms=100.0,
            last_check="2024-01-01T00:00:00"
        )
        
        report = HealthReport(
            timestamp="2024-01-01T00:00:00",
            system=metrics,
            services=[service_status],
            alerts=["Test alert"],
            overall_status="healthy"
        )
        
        assert report.overall_status == "healthy"
        assert len(report.services) == 1
        assert len(report.alerts) == 1
    
    def test_to_dict(self):
        """Test converting report to dictionary."""
        metrics = SystemMetrics(
            timestamp="2024-01-01T00:00:00",
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_available_mb=1024.0,
            disk_percent=70.0,
            disk_available_gb=50.0
        )
        
        report = HealthReport(
            timestamp="2024-01-01T00:00:00",
            system=metrics,
            services=[],
            overall_status="healthy"
        )
        
        report_dict = report.to_dict()
        
        assert 'timestamp' in report_dict
        assert 'system' in report_dict
        assert 'services' in report_dict
        assert 'overall_status' in report_dict


class TestSystemMonitor:
    """Test SystemMonitor class."""
    
    def test_get_metrics(self):
        """Test getting system metrics."""
        monitor = SystemMonitor()
        metrics = monitor.get_metrics()
        
        assert isinstance(metrics, SystemMetrics)
        assert metrics.cpu_percent >= 0
        assert metrics.memory_percent >= 0
        assert metrics.disk_percent >= 0
        assert metrics.memory_available_mb > 0
        assert metrics.disk_available_gb > 0
    
    def test_custom_thresholds(self):
        """Test custom threshold configuration."""
        thresholds = {
            'cpu_percent': 50.0,
            'memory_percent': 60.0,
            'disk_percent': 70.0
        }
        
        monitor = SystemMonitor(thresholds=thresholds)
        
        assert monitor.thresholds['cpu_percent'] == 50.0
        assert monitor.thresholds['memory_percent'] == 60.0
        assert monitor.thresholds['disk_percent'] == 70.0
    
    def test_check_thresholds_normal(self):
        """Test threshold checking with normal values."""
        monitor = SystemMonitor(thresholds={
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0
        })
        
        metrics = SystemMetrics(
            timestamp="2024-01-01T00:00:00",
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_available_mb=1024.0,
            disk_percent=70.0,
            disk_available_gb=50.0
        )
        
        alerts = monitor.check_thresholds(metrics)
        
        assert len(alerts) == 0
    
    def test_check_thresholds_exceeded(self):
        """Test threshold checking with exceeded values."""
        monitor = SystemMonitor(thresholds={
            'cpu_percent': 50.0,
            'memory_percent': 50.0,
            'disk_percent': 50.0
        })
        
        metrics = SystemMetrics(
            timestamp="2024-01-01T00:00:00",
            cpu_percent=90.0,
            memory_percent=95.0,
            memory_available_mb=100.0,
            disk_percent=96.0,
            disk_available_gb=10.0
        )
        
        alerts = monitor.check_thresholds(metrics)
        
        assert len(alerts) == 3  # All thresholds exceeded
        assert any('cpu' in alert.lower() for alert in alerts)
        assert any('memory' in alert.lower() for alert in alerts)
        assert any('disk' in alert.lower() for alert in alerts)


class TestServiceMonitor:
    """Test ServiceMonitor class."""
    
    def test_check_service_up(self):
        """Test checking a service that is up."""
        with patch('health_monitor.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            monitor = ServiceMonitor()
            status = monitor.check_service('test', 'http://localhost:8000/health')
            
            assert status.status == 'up'
            assert status.response_time_ms is not None
            assert status.error is None
    
    def test_check_service_degraded(self):
        """Test checking a service with non-200 response."""
        with patch('health_monitor.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response
            
            monitor = ServiceMonitor()
            status = monitor.check_service('test', 'http://localhost:8000/health')
            
            assert status.status == 'degraded'
            assert status.error == 'HTTP 500'
    
    def test_check_service_timeout(self):
        """Test checking a service that times out."""
        import requests
        
        with patch('health_monitor.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()
            
            monitor = ServiceMonitor()
            status = monitor.check_service('test', 'http://localhost:8000/health')
            
            assert status.status == 'down'
            assert status.error == 'Timeout'
            assert status.response_time_ms is None
    
    def test_check_service_connection_error(self):
        """Test checking a service that refuses connection."""
        import requests
        
        with patch('health_monitor.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()
            
            monitor = ServiceMonitor()
            status = monitor.check_service('test', 'http://localhost:8000/health')
            
            assert status.status == 'down'
            assert status.error == 'Connection refused'
    
    def test_check_all_services(self):
        """Test checking all configured services."""
        with patch('health_monitor.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            services = {
                'service1': 'http://localhost:8000/health',
                'service2': 'http://localhost:3000/'
            }
            
            monitor = ServiceMonitor(services=services)
            statuses = monitor.check_all_services()
            
            assert len(statuses) == 2
            assert all(s.status == 'up' for s in statuses)


class TestAlertManager:
    """Test AlertManager class."""
    
    def test_send_alert(self, mock_logger):
        """Test sending an alert."""
        manager = AlertManager(mock_logger)
        
        manager.send_alert("Test alert", level='warning')
        
        assert len(manager.alert_history) == 1
        assert manager.alert_history[0]['message'] == "Test alert"
        assert manager.alert_history[0]['level'] == 'warning'
        mock_logger.warning.assert_called_once()
    
    def test_send_critical_alert(self, mock_logger):
        """Test sending a critical alert."""
        manager = AlertManager(mock_logger)
        
        manager.send_alert("Critical issue", level='critical')
        
        assert manager.alert_history[0]['level'] == 'critical'
        mock_logger.critical.assert_called_once()
    
    def test_alert_history_limit(self, mock_logger):
        """Test alert history size limit."""
        manager = AlertManager(mock_logger)
        manager.max_history = 5
        
        # Send more alerts than the limit
        for i in range(10):
            manager.send_alert(f"Alert {i}")
        
        assert len(manager.alert_history) == 5
        # Should have the last 5 alerts
        assert manager.alert_history[-1]['message'] == "Alert 9"
    
    def test_get_recent_alerts(self, mock_logger):
        """Test getting recent alerts."""
        manager = AlertManager(mock_logger)
        
        for i in range(20):
            manager.send_alert(f"Alert {i}")
        
        recent = manager.get_recent_alerts(count=5)
        
        assert len(recent) == 5
        assert recent[-1]['message'] == "Alert 19"


class TestServiceRestarter:
    """Test ServiceRestarter class."""
    
    def test_disabled_by_default(self, mock_logger):
        """Test that restarter is disabled by default."""
        restarter = ServiceRestarter(mock_logger, enabled=False)
        
        assert restarter.can_restart('test_service') == False
    
    def test_enabled_restarter(self, mock_logger):
        """Test enabled restarter."""
        restarter = ServiceRestarter(mock_logger, enabled=True)
        
        assert restarter.can_restart('test_service') == True
    
    def test_cooldown_period(self, mock_logger):
        """Test restart cooldown period."""
        restarter = ServiceRestarter(mock_logger, enabled=True)
        restarter.restart_cooldown = 1  # 1 second for testing
        
        # First restart should be allowed
        assert restarter.can_restart('test_service') == True
        
        # Record a restart
        restarter.last_restart['test_service'] = time.time()
        
        # Immediate restart should be blocked
        assert restarter.can_restart('test_service') == False
        
        # Wait for cooldown
        time.sleep(1.1)
        
        # Should be allowed now
        assert restarter.can_restart('test_service') == True
    
    def test_restart_service_no_command(self, mock_logger):
        """Test restart attempt for service with no command."""
        restarter = ServiceRestarter(mock_logger, enabled=True)
        restarter.restart_commands = {}
        
        result = restarter.restart_service('unknown_service')
        
        assert result == False
        mock_logger.warning.assert_called()
    
    @patch('health_monitor.subprocess.run')
    def test_restart_service_success(self, mock_run, mock_logger):
        """Test successful service restart."""
        mock_run.return_value = Mock()
        
        restarter = ServiceRestarter(mock_logger, enabled=True)
        restarter.restart_commands = {'test_service': ['echo', 'restart']}
        
        result = restarter.restart_service('test_service')
        
        assert result == True
        assert 'test_service' in restarter.last_restart
        mock_logger.info.assert_called()
    
    @patch('health_monitor.subprocess.run')
    def test_restart_service_failure(self, mock_run, mock_logger):
        """Test failed service restart."""
        mock_run.side_effect = subprocess.SubprocessError("Failed")
        
        restarter = ServiceRestarter(mock_logger, enabled=True)
        restarter.restart_commands = {'test_service': ['echo', 'restart']}
        
        result = restarter.restart_service('test_service')
        
        assert result == False
        mock_logger.error.assert_called()


class TestHealthMonitor:
    """Test HealthMonitor class."""
    
    def test_initialization(self, temp_project):
        """Test health monitor initialization."""
        monitor = HealthMonitor(
            project_root=temp_project,
            check_interval=60,
            verbose=False
        )
        
        assert monitor.project_root == temp_project
        assert monitor.check_interval == 60
        assert monitor.running == False
    
    def test_pid_file_creation(self, temp_project):
        """Test PID file is created on start."""
        pid_file = temp_project / 'logs' / 'health_monitor.pid'
        
        # Create a simple PID file
        pid_file.write_text(str(os.getpid()))
        
        assert pid_file.exists()
        
        with open(pid_file) as f:
            pid = int(f.read().strip())
        
        assert pid == os.getpid()
    
    @patch('health_monitor.psutil.pid_exists')
    def test_get_status_not_running(self, mock_pid_exists, temp_project):
        """Test getting status when not running."""
        mock_pid_exists.return_value = False
        
        monitor = HealthMonitor(temp_project)
        status = monitor.get_status()
        
        assert status['running'] == False
    
    @patch('health_monitor.psutil.pid_exists')
    def test_get_status_running(self, mock_pid_exists, temp_project):
        """Test getting status when running."""
        mock_pid_exists.return_value = True
        
        # Create PID file
        pid_file = temp_project / 'logs' / 'health_monitor.pid'
        pid_file.write_text(str(12345))
        
        monitor = HealthMonitor(temp_project)
        status = monitor.get_status()
        
        assert status['running'] == True
        assert status['pid'] == 12345
    
    def test_perform_health_check(self, temp_project):
        """Test performing a health check."""
        with patch('health_monitor.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            monitor = HealthMonitor(temp_project, verbose=False)
            report = monitor._perform_health_check()
            
            assert isinstance(report, HealthReport)
            assert report.overall_status in ['healthy', 'degraded', 'critical']
            assert isinstance(report.system, SystemMetrics)
            assert isinstance(report.services, list)
    
    def test_save_metrics(self, temp_project):
        """Test saving metrics to file."""
        metrics = SystemMetrics(
            timestamp="2024-01-01T00:00:00",
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_available_mb=1024.0,
            disk_percent=70.0,
            disk_available_gb=50.0
        )
        
        report = HealthReport(
            timestamp="2024-01-01T00:00:00",
            system=metrics,
            services=[],
            overall_status="healthy"
        )
        
        monitor = HealthMonitor(temp_project, verbose=False)
        monitor._save_metrics(report)
        
        metrics_file = temp_project / 'logs' / 'health_metrics.json'
        assert metrics_file.exists()
        
        with open(metrics_file) as f:
            saved_metrics = json.load(f)
        
        assert len(saved_metrics) == 1
        assert saved_metrics[0]['overall_status'] == 'healthy'
    
    def test_metrics_history_limit(self, temp_project):
        """Test metrics history is limited."""
        metrics = SystemMetrics(
            timestamp="2024-01-01T00:00:00",
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_available_mb=1024.0,
            disk_percent=70.0,
            disk_available_gb=50.0
        )
        
        report = HealthReport(
            timestamp="2024-01-01T00:00:00",
            system=metrics,
            services=[],
            overall_status="healthy"
        )
        
        monitor = HealthMonitor(temp_project, verbose=False)
        
        # Save many metrics
        for i in range(1200):
            monitor._save_metrics(report)
        
        metrics_file = temp_project / 'logs' / 'health_metrics.json'
        with open(metrics_file) as f:
            saved_metrics = json.load(f)
        
        # Should be limited to 1000
        assert len(saved_metrics) == 1000


class TestColorOutput:
    """Test ColorOutput class."""
    
    def test_color_codes_defined(self):
        """Test that color codes are defined."""
        assert ColorOutput.GREEN != ''
        assert ColorOutput.RED != ''
        assert ColorOutput.YELLOW != ''
        assert ColorOutput.RESET != ''
    
    def test_disable_colors(self):
        """Test disabling colors."""
        # Save original values
        original_green = ColorOutput.GREEN
        
        ColorOutput.disable()
        
        assert ColorOutput.GREEN == ''
        assert ColorOutput.RED == ''
        assert ColorOutput.RESET == ''
        
        # Restore
        ColorOutput.GREEN = original_green


def test_stop_monitor_not_running(temp_project):
    """Test stopping monitor when not running."""
    from health_monitor import stop_monitor
    
    result = stop_monitor(temp_project)
    
    assert result == False


@patch('health_monitor.psutil.pid_exists')
@patch('health_monitor.os.kill')
def test_stop_monitor_running(mock_kill, mock_pid_exists, temp_project):
    """Test stopping running monitor."""
    from health_monitor import stop_monitor
    
    # Setup PID file
    pid_file = temp_project / 'logs' / 'health_monitor.pid'
    pid_file.write_text('12345')
    
    # Mock process exists initially, then doesn't
    mock_pid_exists.side_effect = [True, False]
    
    result = stop_monitor(temp_project)
    
    assert result == True
    mock_kill.assert_called_once_with(12345, signal.SIGTERM)


def test_show_status(temp_project, capsys):
    """Test showing monitor status."""
    from health_monitor import show_status
    
    show_status(temp_project)
    
    captured = capsys.readouterr()
    assert 'not running' in captured.out.lower() or 'running' in captured.out.lower()


def test_cli_help():
    """Test CLI help output."""
    import subprocess
    
    result = subprocess.run(
        [sys.executable, 'tools/health_monitor.py', '--help'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert 'daemon' in result.stdout.lower()
    assert 'stop' in result.stdout.lower()
    assert 'status' in result.stdout.lower()


def test_cli_status():
    """Test CLI status command."""
    import subprocess
    
    result = subprocess.run(
        [sys.executable, 'tools/health_monitor.py', '--status'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    assert result.returncode == 0
    # Should show status (running or not)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
