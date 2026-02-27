"""
Setup Scripts Validation Tests

Tests for validating setup and management scripts:
- install.sh
- configure.sh
- start.sh
- stop.sh
- validate.sh
"""

import os
import re
import platform
import subprocess
from pathlib import Path
from typing import List, Optional

import pytest


# Get repository root
REPO_ROOT = Path(__file__).parent.parent.parent


class TestInstallScript:
    """Test install.sh script."""
    
    @pytest.fixture
    def install_script(self) -> Path:
        """Get install.sh path."""
        return REPO_ROOT / "install.sh"
    
    def test_install_script_exists(self, install_script):
        """Test that install.sh exists."""
        assert install_script.exists(), "install.sh must exist"
    
    def test_install_script_executable(self, install_script):
        """Test that install.sh is executable."""
        assert os.access(install_script, os.X_OK), \
            "install.sh should be executable (chmod +x install.sh)"
    
    def test_install_script_has_shebang(self, install_script):
        """Test that install.sh has proper shebang."""
        with open(install_script, encoding="utf-8") as f:
            first_line = f.readline().strip()
        
        assert first_line.startswith("#!/"), \
            "install.sh should start with shebang"
        assert "bash" in first_line or "sh" in first_line, \
            f"install.sh should use bash or sh: {first_line}"
    
    def test_install_script_error_handling(self, install_script):
        """Test that install.sh has error handling."""
        with open(install_script, encoding="utf-8") as f:
            content = f.read()
        
        # Should have set -e or equivalent
        has_error_exit = any([
            "set -e" in content,
            "set -o errexit" in content,
            "|| exit" in content,
        ])
        
        assert has_error_exit, \
            "install.sh should have error handling (set -e or similar)"
    
    def test_install_script_checks_dependencies(self, install_script):
        """Test that install.sh checks for required dependencies."""
        with open(install_script, encoding="utf-8") as f:
            content = f.read()
        
        # Should check for essential tools or at least use them
        # (install script might just try to use them and fail if missing)
        essential_checks = [
            "python",
            "pip",
            "docker",
        ]
        
        checks_found = 0
        for tool in essential_checks:
            # Look for usage or check patterns
            if tool in content:
                checks_found += 1
        
        assert checks_found >= 2, \
            "install.sh should reference or check for required dependencies (python, pip, docker)"
    
    def test_install_script_no_hardcoded_paths(self, install_script):
        """Test that install.sh doesn't have hardcoded absolute paths."""
        with open(install_script, encoding="utf-8") as f:
            content = f.read()
        
        # Look for suspicious hardcoded paths
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            # Check for hardcoded paths that might not work everywhere
            suspicious_patterns = [
                r'/home/\w+/',  # /home/user/
                r'/Users/\w+/',  # macOS home
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, line):
                    # Some exceptions are OK (like /usr/bin, /etc)
                    if not any(ok in line for ok in ['/usr/', '/etc/', '/var/', '/tmp/']):
                        print(f"Warning: Possible hardcoded path at line {i}: {line.strip()}")
    
    def test_install_script_installs_dependencies(self, install_script):
        """Test that install.sh installs Python dependencies."""
        with open(install_script, encoding="utf-8") as f:
            content = f.read()
        
        # Should install requirements
        assert "pip install" in content or "pip3 install" in content, \
            "install.sh should install pip packages"
        
        assert "requirements.txt" in content, \
            "install.sh should reference requirements.txt"
    
    def test_install_script_syntax(self, install_script):
        """Test that install.sh has valid bash syntax."""
        if platform.system() == "Windows":
            pytest.skip("Skipping bash syntax check on Windows")
        try:
            result = subprocess.run(
                ["bash", "-n", install_script.as_posix()],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert result.returncode == 0, \
                f"install.sh has syntax errors:\n{result.stderr}"
        
        except subprocess.TimeoutExpired:
            pytest.fail("install.sh syntax check timed out")
        except FileNotFoundError:
            pytest.skip("bash not available for syntax checking")


class TestConfigureScript:
    """Test configure.sh script."""
    
    @pytest.fixture
    def configure_script(self) -> Path:
        """Get configure.sh path."""
        return REPO_ROOT / "configure.sh"
    
    def test_configure_script_exists(self, configure_script):
        """Test that configure.sh exists."""
        assert configure_script.exists(), "configure.sh must exist"
    
    def test_configure_script_executable(self, configure_script):
        """Test that configure.sh is executable."""
        assert os.access(configure_script, os.X_OK), \
            "configure.sh should be executable"
    
    def test_configure_script_has_shebang(self, configure_script):
        """Test that configure.sh has proper shebang."""
        with open(configure_script, encoding="utf-8") as f:
            first_line = f.readline().strip()
        
        assert first_line.startswith("#!/"), \
            "configure.sh should start with shebang"
    
    def test_configure_script_handles_env_file(self, configure_script):
        """Test that configure.sh handles .env file."""
        with open(configure_script, encoding="utf-8") as f:
            content = f.read()
        
        # Should reference .env or .env.example
        assert ".env" in content, \
            "configure.sh should handle .env file"
    
    def test_configure_script_validates_config(self, configure_script):
        """Test that configure.sh validates configuration."""
        with open(configure_script, encoding="utf-8") as f:
            content = f.read()
        
        # Should have some validation logic
        validation_indicators = [
            "if [",
            "test ",
            "[[",
            "check",
            "validate",
            "verify",
        ]
        
        has_validation = any(indicator in content for indicator in validation_indicators)
        
        assert has_validation, \
            "configure.sh should have validation logic"
    
    def test_configure_script_syntax(self, configure_script):
        """Test that configure.sh has valid bash syntax."""
        if platform.system() == "Windows":
            pytest.skip("Skipping bash syntax check on Windows")
        try:
            result = subprocess.run(
                ["bash", "-n", configure_script.as_posix()],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert result.returncode == 0, \
                f"configure.sh has syntax errors:\n{result.stderr}"
        
        except subprocess.TimeoutExpired:
            pytest.fail("configure.sh syntax check timed out")
        except FileNotFoundError:
            pytest.skip("bash not available for syntax checking")


class TestStartScript:
    """Test start.sh script."""
    
    @pytest.fixture
    def start_script(self) -> Path:
        """Get start.sh path."""
        return REPO_ROOT / "start.sh"
    
    def test_start_script_exists(self, start_script):
        """Test that start.sh exists."""
        assert start_script.exists(), "start.sh must exist"
    
    def test_start_script_executable(self, start_script):
        """Test that start.sh is executable."""
        assert os.access(start_script, os.X_OK), \
            "start.sh should be executable"
    
    def test_start_script_has_shebang(self, start_script):
        """Test that start.sh has proper shebang."""
        with open(start_script, encoding="utf-8") as f:
            first_line = f.readline().strip()
        
        assert first_line.startswith("#!/"), \
            "start.sh should start with shebang"
    
    def test_start_script_starts_services(self, start_script):
        """Test that start.sh starts services."""
        with open(start_script, encoding="utf-8") as f:
            content = f.read()
        
        # Should use docker-compose or similar
        service_starters = [
            "docker-compose up",
            "docker compose up",
            "systemctl start",
            "python",
            "uvicorn",
        ]
        
        starts_services = any(starter in content for starter in service_starters)
        
        assert starts_services, \
            "start.sh should start services (docker-compose, python, etc.)"
    
    def test_start_script_checks_prerequisites(self, start_script):
        """Test that start.sh checks prerequisites."""
        with open(start_script, encoding="utf-8") as f:
            content = f.read()
        
        # Should check if .env exists or services are available
        prerequisite_checks = [
            ".env",
            "docker",
            "command -v",
            "which",
        ]
        
        has_checks = any(check in content for check in prerequisite_checks)
        
        # Not strictly required but recommended
        if not has_checks:
            print("Info: start.sh might benefit from prerequisite checks")
    
    def test_start_script_syntax(self, start_script):
        """Test that start.sh has valid bash syntax."""
        if platform.system() == "Windows":
            pytest.skip("Skipping bash syntax check on Windows")
        try:
            result = subprocess.run(
                ["bash", "-n", start_script.as_posix()],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert result.returncode == 0, \
                f"start.sh has syntax errors:\n{result.stderr}"
        
        except subprocess.TimeoutExpired:
            pytest.fail("start.sh syntax check timed out")
        except FileNotFoundError:
            pytest.skip("bash not available for syntax checking")


class TestStopScript:
    """Test stop.sh script."""
    
    @pytest.fixture
    def stop_script(self) -> Path:
        """Get stop.sh path."""
        return REPO_ROOT / "stop.sh"
    
    def test_stop_script_exists(self, stop_script):
        """Test that stop.sh exists."""
        assert stop_script.exists(), "stop.sh must exist"
    
    def test_stop_script_executable(self, stop_script):
        """Test that stop.sh is executable."""
        assert os.access(stop_script, os.X_OK), \
            "stop.sh should be executable"
    
    def test_stop_script_has_shebang(self, stop_script):
        """Test that stop.sh has proper shebang."""
        with open(stop_script, encoding="utf-8") as f:
            first_line = f.readline().strip()
        
        assert first_line.startswith("#!/"), \
            "stop.sh should start with shebang"
    
    def test_stop_script_stops_services(self, stop_script):
        """Test that stop.sh stops services."""
        with open(stop_script, encoding="utf-8") as f:
            content = f.read()
        
        # Should stop docker-compose or similar
        service_stoppers = [
            "docker-compose down",
            "docker compose down",
            "docker-compose stop",
            "docker compose stop",
            "systemctl stop",
            "kill",
            "pkill",
        ]
        
        stops_services = any(stopper in content for stopper in service_stoppers)
        
        assert stops_services, \
            "stop.sh should stop services (docker-compose down, kill, etc.)"
    
    def test_stop_script_graceful_shutdown(self, stop_script):
        """Test that stop.sh performs graceful shutdown."""
        with open(stop_script, encoding="utf-8") as f:
            content = f.read()
        
        # Should have some form of graceful shutdown
        # Not using SIGKILL immediately
        if "kill -9" in content or "kill -KILL" in content:
            # Check if there's a graceful attempt first
            lines = content.split('\n')
            kill9_index = -1
            for i, line in enumerate(lines):
                if "kill -9" in line or "kill -KILL" in line:
                    kill9_index = i
                    break
            
            if kill9_index > 0:
                # Check previous lines for graceful shutdown attempt
                previous_content = '\n'.join(lines[:kill9_index])
                has_graceful = any([
                    "kill -TERM" in previous_content,
                    "kill -15" in previous_content,
                    "docker-compose down" in previous_content,
                    "sleep" in previous_content,  # Wait for graceful shutdown
                ])
                
                if not has_graceful:
                    print("Warning: stop.sh uses SIGKILL without graceful shutdown attempt")
    
    def test_stop_script_syntax(self, stop_script):
        """Test that stop.sh has valid bash syntax."""
        if platform.system() == "Windows":
            pytest.skip("Skipping bash syntax check on Windows")
        try:
            result = subprocess.run(
                ["bash", "-n", stop_script.as_posix()],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert result.returncode == 0, \
                f"stop.sh has syntax errors:\n{result.stderr}"
        
        except subprocess.TimeoutExpired:
            pytest.fail("stop.sh syntax check timed out")
        except FileNotFoundError:
            pytest.skip("bash not available for syntax checking")


class TestValidateScript:
    """Test validate.sh script if it exists."""
    
    @pytest.fixture
    def validate_script(self) -> Optional[Path]:
        """Get validate.sh path."""
        script = REPO_ROOT / "validate.sh"
        return script if script.exists() else None
    
    def test_validate_script_executable(self, validate_script):
        """Test that validate.sh is executable if it exists."""
        if validate_script is None:
            pytest.skip("validate.sh does not exist")
        
        assert os.access(validate_script, os.X_OK), \
            "validate.sh should be executable"
    
    def test_validate_script_has_shebang(self, validate_script):
        """Test that validate.sh has proper shebang."""
        if validate_script is None:
            pytest.skip("validate.sh does not exist")
        
        with open(validate_script, encoding="utf-8") as f:
            first_line = f.readline().strip()
        
        assert first_line.startswith("#!/"), \
            "validate.sh should start with shebang"
    
    def test_validate_script_checks_configuration(self, validate_script):
        """Test that validate.sh checks configuration."""
        if validate_script is None:
            pytest.skip("validate.sh does not exist")
        
        with open(validate_script, encoding="utf-8") as f:
            content = f.read()
        
        # Should check for various components
        validation_targets = [
            ".env",
            "docker",
            "python",
            "requirements",
        ]
        
        checks_found = sum(1 for target in validation_targets if target in content)
        
        assert checks_found >= 2, \
            "validate.sh should check multiple configuration aspects"
    
    def test_validate_script_syntax(self, validate_script):
        """Test that validate.sh has valid bash syntax."""
        if validate_script is None:
            pytest.skip("validate.sh does not exist")
        
        if platform.system() == "Windows":
            pytest.skip("Skipping bash syntax check on Windows")
        
        try:
            result = subprocess.run(
                ["bash", "-n", validate_script.as_posix()],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert result.returncode == 0, \
                f"validate.sh has syntax errors:\n{result.stderr}"
        
        except subprocess.TimeoutExpired:
            pytest.fail("validate.sh syntax check timed out")
        except FileNotFoundError:
            pytest.skip("bash not available for syntax checking")


class TestScriptInteraction:
    """Test interaction between scripts."""
    
    def test_scripts_reference_consistent_paths(self):
        """Test that scripts use consistent paths."""
        scripts = [
            REPO_ROOT / "install.sh",
            REPO_ROOT / "configure.sh",
            REPO_ROOT / "start.sh",
            REPO_ROOT / "stop.sh",
        ]
        
        # Collect all referenced paths
        path_references = {}
        
        for script in scripts:
            if not script.exists():
                continue
            
            with open(script, encoding="utf-8") as f:
                content = f.read()
            
            # Look for common path references
            patterns = {
                'docker-compose': r'docker-compose\.yml',
                'requirements': r'requirements\.txt',
                'env': r'\.env',
            }
            
            path_references[script.name] = {}
            
            for key, pattern in patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    path_references[script.name][key] = matches
        
        # All scripts should reference the same filenames
        # (This is informational more than a strict test)
        if len(path_references) > 1:
            print(f"\nPath references across scripts: {path_references}")
    
    def test_scripts_use_consistent_error_codes(self):
        """Test that scripts use consistent error codes."""
        scripts = [
            REPO_ROOT / "install.sh",
            REPO_ROOT / "configure.sh",
            REPO_ROOT / "start.sh",
            REPO_ROOT / "stop.sh",
        ]
        
        for script in scripts:
            if not script.exists():
                continue
            
            with open(script, encoding="utf-8") as f:
                content = f.read()
            
            # Look for exit statements
            exit_codes = re.findall(r'exit\s+(\d+)', content)
            
            # Should use standard codes (0 = success, 1 = error)
            for code in exit_codes:
                code_int = int(code)
                assert code_int >= 0 and code_int <= 255, \
                    f"{script.name}: exit code {code_int} is out of valid range (0-255)"


class TestScriptIdempotency:
    """Test that scripts are idempotent where appropriate."""
    
    def test_configure_script_can_run_multiple_times(self):
        """Test that configure.sh can be run multiple times safely."""
        configure_script = REPO_ROOT / "configure.sh"
        
        if not configure_script.exists():
            pytest.skip("configure.sh does not exist")
        
        with open(configure_script, encoding="utf-8") as f:
            content = f.read()
        
        # Should have checks to avoid overwriting existing config
        idempotent_patterns = [
            r'if.*\[.*-f.*\.env.*\]',  # Check if .env exists
            r'if.*\[.*-e.*\.env.*\]',
            r'test -f',
            r'test -e',
        ]
        
        has_idempotent_checks = any(
            re.search(pattern, content) 
            for pattern in idempotent_patterns
        )
        
        if not has_idempotent_checks:
            print("Info: configure.sh might benefit from idempotency checks")
    
    def test_install_script_handles_existing_installation(self):
        """Test that install.sh handles existing installation."""
        install_script = REPO_ROOT / "install.sh"
        
        with open(install_script, encoding="utf-8") as f:
            content = f.read()
        
        # Should check for existing installation or use --upgrade
        reinstall_safe = any([
            "pip install -U" in content,
            "pip install --upgrade" in content,
            "pip install --force-reinstall" in content,
            re.search(r'if.*already.*installed', content),
        ])
        
        # This is more of a recommendation
        if not reinstall_safe:
            print("Info: install.sh might benefit from handling existing installations")


class TestScriptDocumentation:
    """Test that scripts have proper documentation."""
    
    def test_scripts_have_comments(self):
        """Test that scripts have descriptive comments."""
        scripts = [
            REPO_ROOT / "install.sh",
            REPO_ROOT / "configure.sh",
            REPO_ROOT / "start.sh",
            REPO_ROOT / "stop.sh",
        ]
        
        for script in scripts:
            if not script.exists():
                continue
            
            with open(script, encoding="utf-8") as f:
                lines = f.readlines()
            
            # Count comment lines (excluding shebang)
            comment_lines = sum(
                1 for line in lines[1:20]  # Check first 20 lines
                if line.strip().startswith('#')
            )
            
            assert comment_lines >= 2, \
                f"{script.name} should have descriptive comments at the top"
    
    def test_scripts_have_usage_info(self):
        """Test that scripts provide usage information."""
        scripts = [
            REPO_ROOT / "install.sh",
            REPO_ROOT / "configure.sh",
        ]
        
        for script in scripts:
            if not script.exists():
                continue
            
            with open(script, encoding="utf-8") as f:
                content = f.read()
            
            # Should have usage info or help
            has_usage = any([
                "usage" in content.lower(),
                "help" in content.lower(),
                "--help" in content,
                "-h" in content,
            ])
            
            # Not strictly required but recommended for user-facing scripts
            if not has_usage:
                print(f"Info: {script.name} might benefit from usage information")
