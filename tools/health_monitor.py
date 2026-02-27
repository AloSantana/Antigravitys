#!/usr/bin/env python3
"""
Health Monitor Daemon

A background monitoring daemon that continuously monitors system health,
service availability, and performance metrics.

Usage:
    python tools/health_monitor.py --daemon
    python tools/health_monitor.py --stop
    python tools/health_monitor.py --status
"""

import argparse
import json
import logging
import os
import psutil
import requests
import signal
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import threading
from logging.handlers import RotatingFileHandler


@dataclass
class SystemMetrics:
    """System resource metrics."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_percent: float
    disk_available_gb: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ServiceStatus:
    """Service availability status."""
    name: str
    status: str  # 'up', 'down', 'degraded'
    response_time_ms: Optional[float]
    last_check: str
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class HealthReport:
    """Complete health report."""
    timestamp: str
    system: SystemMetrics
    services: List[ServiceStatus]
    alerts: List[str] = field(default_factory=list)
    overall_status: str = "healthy"  # 'healthy', 'degraded', 'critical'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'system': self.system.to_dict(),
            'services': [s.to_dict() for s in self.services],
            'alerts': self.alerts,
            'overall_status': self.overall_status
        }


class ColorOutput:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    @classmethod
    def disable(cls) -> None:
        """Disable color output."""
        cls.GREEN = ''
        cls.YELLOW = ''
        cls.RED = ''
        cls.BLUE = ''
        cls.CYAN = ''
        cls.BOLD = ''
        cls.RESET = ''


class SystemMonitor:
    """Monitors system resources."""
    
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = thresholds or {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0
        }
    
    def get_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=memory.percent,
            memory_available_mb=memory.available / (1024 * 1024),
            disk_percent=disk.percent,
            disk_available_gb=disk.free / (1024 * 1024 * 1024)
        )
    
    def check_thresholds(self, metrics: SystemMetrics) -> List[str]:
        """Check if metrics exceed thresholds."""
        alerts = []
        
        if metrics.cpu_percent > self.thresholds['cpu_percent']:
            alerts.append(
                f"High CPU usage: {metrics.cpu_percent:.1f}% "
                f"(threshold: {self.thresholds['cpu_percent']:.1f}%)"
            )
        
        if metrics.memory_percent > self.thresholds['memory_percent']:
            alerts.append(
                f"High memory usage: {metrics.memory_percent:.1f}% "
                f"(threshold: {self.thresholds['memory_percent']:.1f}%)"
            )
        
        if metrics.disk_percent > self.thresholds['disk_percent']:
            alerts.append(
                f"Low disk space: {metrics.disk_percent:.1f}% used "
                f"(threshold: {self.thresholds['disk_percent']:.1f}%)"
            )
        
        return alerts


class ServiceMonitor:
    """Monitors service availability."""
    
    def __init__(self, services: Optional[Dict[str, str]] = None):
        self.services = services or {
            'backend_api': 'http://localhost:8000/health',
            'frontend': 'http://localhost:3000',
        }
        self.timeout = 5  # seconds
    
    def check_service(self, name: str, url: str) -> ServiceStatus:
        """Check if a service is available."""
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                status = 'up'
                error = None
            else:
                status = 'degraded'
                error = f"HTTP {response.status_code}"
            
            return ServiceStatus(
                name=name,
                status=status,
                response_time_ms=response_time,
                last_check=datetime.now().isoformat(),
                error=error
            )
            
        except requests.exceptions.Timeout:
            return ServiceStatus(
                name=name,
                status='down',
                response_time_ms=None,
                last_check=datetime.now().isoformat(),
                error='Timeout'
            )
        except requests.exceptions.ConnectionError:
            return ServiceStatus(
                name=name,
                status='down',
                response_time_ms=None,
                last_check=datetime.now().isoformat(),
                error='Connection refused'
            )
        except Exception as e:
            return ServiceStatus(
                name=name,
                status='down',
                response_time_ms=None,
                last_check=datetime.now().isoformat(),
                error=str(e)
            )
    
    def check_all_services(self) -> List[ServiceStatus]:
        """Check all configured services."""
        statuses = []
        
        for name, url in self.services.items():
            status = self.check_service(name, url)
            statuses.append(status)
        
        return statuses


class AlertManager:
    """Manages alerts and notifications."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.alert_history: List[Dict[str, Any]] = []
        self.max_history = 100
    
    def send_alert(self, alert: str, level: str = 'warning') -> None:
        """Send an alert."""
        alert_record = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': alert
        }
        
        self.alert_history.append(alert_record)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)
        
        # Log the alert
        if level == 'critical':
            self.logger.critical(alert)
        elif level == 'error':
            self.logger.error(alert)
        elif level == 'warning':
            self.logger.warning(alert)
        else:
            self.logger.info(alert)
        
        # In a real implementation, this could also:
        # - Send emails
        # - Post to Slack/Discord
        # - Trigger webhooks
        # - Send SMS alerts
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        return self.alert_history[-count:]


class ServiceRestarter:
    """Automatically restarts failed services."""
    
    def __init__(self, logger: logging.Logger, enabled: bool = False):
        self.logger = logger
        self.enabled = enabled
        self.restart_cooldown = 300  # 5 minutes
        self.last_restart: Dict[str, float] = {}
        self.restart_commands = {
            'backend_api': ['./start.sh'],
            # Add more services as needed
        }
    
    def can_restart(self, service_name: str) -> bool:
        """Check if service can be restarted (cooldown check)."""
        if not self.enabled:
            return False
        
        last_restart_time = self.last_restart.get(service_name, 0)
        return time.time() - last_restart_time > self.restart_cooldown
    
    def restart_service(self, service_name: str) -> bool:
        """Attempt to restart a service."""
        if not self.can_restart(service_name):
            self.logger.info(f"Service {service_name} restart skipped (cooldown)")
            return False
        
        command = self.restart_commands.get(service_name)
        if not command:
            self.logger.warning(f"No restart command for service {service_name}")
            return False
        
        try:
            self.logger.info(f"Attempting to restart {service_name}...")
            subprocess.run(command, check=True, timeout=60)
            self.last_restart[service_name] = time.time()
            self.logger.info(f"Successfully restarted {service_name}")
            return True
        except subprocess.SubprocessError as e:
            self.logger.error(f"Failed to restart {service_name}: {e}")
            return False


class HealthMonitor:
    """Main health monitoring daemon."""
    
    def __init__(
        self,
        project_root: Path,
        check_interval: int = 60,
        log_file: Optional[Path] = None,
        auto_restart: bool = False,
        verbose: bool = False
    ):
        self.project_root = project_root
        self.check_interval = check_interval
        self.auto_restart = auto_restart
        self.verbose = verbose
        self.running = False
        self.pid_file = project_root / 'logs' / 'health_monitor.pid'
        self.metrics_file = project_root / 'logs' / 'health_metrics.json'
        
        # Setup logging
        self.logger = self._setup_logging(log_file or project_root / 'logs' / 'health_monitor.log')
        
        # Initialize components
        self.system_monitor = SystemMonitor()
        self.service_monitor = ServiceMonitor()
        self.alert_manager = AlertManager(self.logger)
        self.service_restarter = ServiceRestarter(self.logger, auto_restart)
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _setup_logging(self, log_file: Path) -> logging.Logger:
        """Setup logging configuration."""
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger('health_monitor')
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        if self.verbose:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter('%(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self) -> None:
        """Start the health monitoring daemon."""
        # Check if already running
        if self.pid_file.exists():
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if psutil.pid_exists(pid):
                print(f"Health monitor already running with PID {pid}")
                return
        
        # Write PID file
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        self.running = True
        self.logger.info("Health monitor started")
        print(f"{ColorOutput.GREEN}✓{ColorOutput.RESET} Health monitor started (PID: {os.getpid()})")
        print(f"  Log file: {self.logger.handlers[0].baseFilename}")
        print(f"  Check interval: {self.check_interval}s")
        
        try:
            self._monitor_loop()
        finally:
            self._cleanup()
    
    def stop(self) -> None:
        """Stop the health monitoring daemon."""
        self.running = False
        self.logger.info("Health monitor stopped")
    
    def _cleanup(self) -> None:
        """Cleanup resources on shutdown."""
        if self.pid_file.exists():
            self.pid_file.unlink()
        self.logger.info("Health monitor cleanup complete")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        while self.running:
            try:
                # Perform health check
                report = self._perform_health_check()
                
                # Display status
                self._display_status(report)
                
                # Save metrics
                self._save_metrics(report)
                
                # Handle alerts
                if report.alerts:
                    for alert in report.alerts:
                        self.alert_manager.send_alert(alert, 'warning')
                
                # Handle service failures
                for service in report.services:
                    if service.status == 'down':
                        if self.auto_restart:
                            self.service_restarter.restart_service(service.name)
                        else:
                            self.alert_manager.send_alert(
                                f"Service {service.name} is down: {service.error}",
                                'error'
                            )
                
                consecutive_errors = 0
                
            except Exception as e:
                consecutive_errors += 1
                self.logger.error(f"Error in monitor loop: {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    self.logger.critical(
                        f"Too many consecutive errors ({consecutive_errors}), stopping monitor"
                    )
                    self.stop()
                    break
            
            # Sleep until next check
            if self.running:
                time.sleep(self.check_interval)
    
    def _perform_health_check(self) -> HealthReport:
        """Perform a complete health check."""
        # Get system metrics
        system_metrics = self.system_monitor.get_metrics()
        
        # Check services
        service_statuses = self.service_monitor.check_all_services()
        
        # Check for alerts
        alerts = self.system_monitor.check_thresholds(system_metrics)
        
        # Determine overall status
        overall_status = 'healthy'
        
        down_services = sum(1 for s in service_statuses if s.status == 'down')
        degraded_services = sum(1 for s in service_statuses if s.status == 'degraded')
        
        if down_services > 0 or len(alerts) > 2:
            overall_status = 'critical'
        elif degraded_services > 0 or len(alerts) > 0:
            overall_status = 'degraded'
        
        return HealthReport(
            timestamp=datetime.now().isoformat(),
            system=system_metrics,
            services=service_statuses,
            alerts=alerts,
            overall_status=overall_status
        )
    
    def _display_status(self, report: HealthReport) -> None:
        """Display health status to console."""
        if not self.verbose:
            return
        
        # Status indicator
        if report.overall_status == 'healthy':
            status_color = ColorOutput.GREEN
            status_symbol = '✓'
        elif report.overall_status == 'degraded':
            status_color = ColorOutput.YELLOW
            status_symbol = '⚠'
        else:
            status_color = ColorOutput.RED
            status_symbol = '✗'
        
        print(f"\n{status_color}{status_symbol} {report.overall_status.upper()}{ColorOutput.RESET} - {report.timestamp}")
        
        # System metrics
        print(f"  CPU: {report.system.cpu_percent:.1f}%  "
              f"Memory: {report.system.memory_percent:.1f}%  "
              f"Disk: {report.system.disk_percent:.1f}%")
        
        # Services
        for service in report.services:
            if service.status == 'up':
                print(f"  {ColorOutput.GREEN}●{ColorOutput.RESET} {service.name}: "
                      f"{service.response_time_ms:.0f}ms")
            elif service.status == 'degraded':
                print(f"  {ColorOutput.YELLOW}●{ColorOutput.RESET} {service.name}: "
                      f"{service.error}")
            else:
                print(f"  {ColorOutput.RED}●{ColorOutput.RESET} {service.name}: "
                      f"{service.error}")
        
        # Alerts
        if report.alerts:
            print(f"  {ColorOutput.YELLOW}Alerts:{ColorOutput.RESET}")
            for alert in report.alerts:
                print(f"    - {alert}")
    
    def _save_metrics(self, report: HealthReport) -> None:
        """Save metrics to JSON file."""
        try:
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing metrics
            metrics = []
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    try:
                        metrics = json.load(f)
                    except json.JSONDecodeError:
                        metrics = []
            
            # Add new report
            metrics.append(report.to_dict())
            
            # Keep only last 1000 entries
            if len(metrics) > 1000:
                metrics = metrics[-1000:]
            
            # Save metrics
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitor status."""
        if not self.pid_file.exists():
            return {
                'running': False,
                'pid': None,
                'message': 'Health monitor is not running'
            }
        
        with open(self.pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        if not psutil.pid_exists(pid):
            return {
                'running': False,
                'pid': pid,
                'message': f'Health monitor PID {pid} not found (stale PID file)'
            }
        
        # Get latest metrics
        latest_report = None
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    metrics = json.load(f)
                    if metrics:
                        latest_report = metrics[-1]
            except Exception:
                pass
        
        return {
            'running': True,
            'pid': pid,
            'message': 'Health monitor is running',
            'latest_report': latest_report
        }


def stop_monitor(project_root: Path) -> bool:
    """Stop the health monitor daemon."""
    pid_file = project_root / 'logs' / 'health_monitor.pid'
    
    if not pid_file.exists():
        print(f"{ColorOutput.YELLOW}⚠{ColorOutput.RESET} Health monitor is not running")
        return False
    
    with open(pid_file, 'r') as f:
        pid = int(f.read().strip())
    
    if not psutil.pid_exists(pid):
        print(f"{ColorOutput.YELLOW}⚠{ColorOutput.RESET} PID {pid} not found (removing stale PID file)")
        pid_file.unlink()
        return False
    
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"{ColorOutput.GREEN}✓{ColorOutput.RESET} Sent stop signal to health monitor (PID: {pid})")
        
        # Wait for process to stop
        for _ in range(10):
            time.sleep(0.5)
            if not psutil.pid_exists(pid):
                print(f"{ColorOutput.GREEN}✓{ColorOutput.RESET} Health monitor stopped")
                return True
        
        print(f"{ColorOutput.YELLOW}⚠{ColorOutput.RESET} Health monitor did not stop gracefully, forcing...")
        os.kill(pid, signal.SIGKILL)
        time.sleep(1)
        
        if not psutil.pid_exists(pid):
            print(f"{ColorOutput.GREEN}✓{ColorOutput.RESET} Health monitor stopped (forced)")
            return True
        else:
            print(f"{ColorOutput.RED}✗{ColorOutput.RESET} Failed to stop health monitor")
            return False
            
    except ProcessLookupError:
        print(f"{ColorOutput.YELLOW}⚠{ColorOutput.RESET} Process already terminated")
        pid_file.unlink()
        return True
    except Exception as e:
        print(f"{ColorOutput.RED}✗{ColorOutput.RESET} Error stopping health monitor: {e}")
        return False


def show_status(project_root: Path) -> None:
    """Show health monitor status."""
    monitor = HealthMonitor(project_root)
    status = monitor.get_status()
    
    if status['running']:
        print(f"{ColorOutput.GREEN}●{ColorOutput.RESET} {status['message']} (PID: {status['pid']})")
        
        if status.get('latest_report'):
            report = status['latest_report']
            print(f"\nLatest Health Report:")
            print(f"  Timestamp: {report['timestamp']}")
            print(f"  Overall Status: {report['overall_status']}")
            print(f"  System: CPU {report['system']['cpu_percent']:.1f}%, "
                  f"Memory {report['system']['memory_percent']:.1f}%, "
                  f"Disk {report['system']['disk_percent']:.1f}%")
            print(f"  Services:")
            for service in report['services']:
                status_symbol = '●'
                if service['status'] == 'up':
                    status_color = ColorOutput.GREEN
                elif service['status'] == 'degraded':
                    status_color = ColorOutput.YELLOW
                else:
                    status_color = ColorOutput.RED
                print(f"    {status_color}{status_symbol}{ColorOutput.RESET} "
                      f"{service['name']}: {service['status']}")
            
            if report['alerts']:
                print(f"  Alerts:")
                for alert in report['alerts']:
                    print(f"    - {alert}")
    else:
        print(f"{ColorOutput.YELLOW}○{ColorOutput.RESET} {status['message']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Health Monitor Daemon - Continuous system and service monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Start health monitor in daemon mode'
    )
    
    parser.add_argument(
        '--stop',
        action='store_true',
        help='Stop the health monitor daemon'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show health monitor status'
    )
    
    parser.add_argument(
        '--check-interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--auto-restart',
        action='store_true',
        help='Automatically restart failed services'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--project-root',
        type=str,
        default='.',
        help='Project root directory (default: current directory)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Log file path (default: logs/health_monitor.log)'
    )
    
    args = parser.parse_args()
    
    if args.no_color:
        ColorOutput.disable()
    
    project_root = Path(args.project_root).resolve()
    
    # Handle commands
    if args.stop:
        return 0 if stop_monitor(project_root) else 1
    
    if args.status:
        show_status(project_root)
        return 0
    
    if args.daemon:
        log_file = Path(args.log_file) if args.log_file else None
        
        monitor = HealthMonitor(
            project_root=project_root,
            check_interval=args.check_interval,
            log_file=log_file,
            auto_restart=args.auto_restart,
            verbose=args.verbose
        )
        
        monitor.start()
        return 0
    
    # Default: show status
    show_status(project_root)
    return 0


if __name__ == '__main__':
    sys.exit(main())
