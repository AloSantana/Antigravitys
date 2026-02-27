"""
Cross-platform utilities for detecting OS and normalizing paths.

Provides utilities for:
- OS detection (Windows/Linux/macOS)
- Path normalization across platforms
- Service management detection
- Firewall management helpers
- Virtual environment activation commands
"""

import sys
import platform
import subprocess
import logging
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)

PlatformType = Literal['windows', 'linux', 'macos', 'unknown']
ServiceManagerType = Literal['systemctl', 'sc', 'launchctl', 'none']


def get_platform() -> PlatformType:
    """
    Detect the current platform.
    
    Returns:
        Platform type: 'windows', 'linux', 'macos', or 'unknown'
    """
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    elif system == 'darwin':
        return 'macos'
    else:
        logger.warning(f"Unknown platform: {system}")
        return 'unknown'


def normalize_path(path: str) -> str:
    """
    Normalize path to use OS-appropriate separators.
    
    Args:
        path: Path with any separator style
        
    Returns:
        Path with OS-appropriate separators
    """
    # Use pathlib for cross-platform path handling
    return str(Path(path))


def get_service_manager() -> ServiceManagerType:
    """
    Detect the service manager for the current platform.
    
    Returns:
        Service manager type: 'systemctl', 'sc', 'launchctl', or 'none'
    """
    platform_type = get_platform()
    
    if platform_type == 'linux':
        # Check if systemd is available
        try:
            subprocess.run(['systemctl', '--version'], 
                         capture_output=True, 
                         check=True, 
                         timeout=5)
            return 'systemctl'
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("systemctl not available on Linux")
            return 'none'
    elif platform_type == 'windows':
        return 'sc'
    elif platform_type == 'macos':
        return 'launchctl'
    else:
        return 'none'


def open_firewall_port(port: int, protocol: str = 'tcp') -> bool:
    """
    Open a firewall port using platform-appropriate commands.
    
    Args:
        port: Port number to open
        protocol: Protocol type ('tcp' or 'udp')
        
    Returns:
        True if successful, False otherwise
    """
    platform_type = get_platform()
    
    try:
        if platform_type == 'linux':
            # Try ufw first (Ubuntu/Debian)
            try:
                subprocess.run(['ufw', 'allow', f'{port}/{protocol}'], 
                             capture_output=True, 
                             check=True, 
                             timeout=10)
                logger.info(f"Opened port {port}/{protocol} using ufw")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Try firewall-cmd (CentOS/RHEL/Fedora)
                try:
                    subprocess.run(['firewall-cmd', '--permanent', 
                                  f'--add-port={port}/{protocol}'], 
                                 capture_output=True, 
                                 check=True, 
                                 timeout=10)
                    subprocess.run(['firewall-cmd', '--reload'], 
                                 capture_output=True, 
                                 check=True, 
                                 timeout=10)
                    logger.info(f"Opened port {port}/{protocol} using firewall-cmd")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    logger.warning(f"Could not open port {port}/{protocol}: no firewall tool found")
                    return False
        
        elif platform_type == 'windows':
            # Use netsh advfirewall on Windows
            rule_name = f"Antigravity_{port}_{protocol}"
            cmd = [
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                f'name={rule_name}',
                'dir=in',
                'action=allow',
                f'protocol={protocol}',
                f'localport={port}'
            ]
            subprocess.run(cmd, capture_output=True, check=True, timeout=10)
            logger.info(f"Opened port {port}/{protocol} using netsh")
            return True
        
        elif platform_type == 'macos':
            logger.warning("Firewall management on macOS requires manual configuration")
            return False
        
        else:
            logger.warning(f"Firewall management not supported on {platform_type}")
            return False
    
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout opening port {port}/{protocol}")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to open port {port}/{protocol}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error opening port {port}/{protocol}: {e}")
        return False


def get_venv_activate_cmd() -> str:
    """
    Get the command to activate the virtual environment for the current platform.
    
    Returns:
        Activation command string
    """
    platform_type = get_platform()
    
    if platform_type == 'windows':
        return 'venv\\Scripts\\activate'
    else:
        return 'source venv/bin/activate'


def is_port_in_use(port: int) -> bool:
    """
    Check if a port is already in use.
    
    Args:
        port: Port number to check
        
    Returns:
        True if port is in use, False otherwise
    """
    import socket
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('', port))
            return False
        except OSError:
            return True


def get_python_executable() -> str:
    """
    Get the current Python executable path.
    
    Returns:
        Path to Python executable
    """
    return sys.executable


def get_pip_executable() -> str:
    """
    Get the pip executable path.
    
    Returns:
        Path to pip executable
    """
    platform_type = get_platform()
    
    if platform_type == 'windows':
        # On Windows, pip is in Scripts directory
        venv_pip = Path(sys.prefix) / 'Scripts' / 'pip.exe'
    else:
        # On Unix-like systems, pip is in bin directory
        venv_pip = Path(sys.prefix) / 'bin' / 'pip'
    
    if venv_pip.exists():
        return str(venv_pip)
    else:
        # Fallback to system pip
        return 'pip'


def get_platform_info() -> dict:
    """
    Get comprehensive platform information.
    
    Returns:
        Dictionary with platform details
    """
    return {
        'platform': get_platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_executable': get_python_executable(),
        'service_manager': get_service_manager(),
        'venv_activate': get_venv_activate_cmd(),
    }


if __name__ == '__main__':
    # Test platform detection
    info = get_platform_info()
    print("Platform Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
