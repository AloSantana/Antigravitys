"""
Configuration Validation Tests

Tests to ensure all configuration files are valid and complete:
- Environment variables
- MCP server configurations
- Docker Compose setup
- Shell scripts
- Python dependencies
"""

import json
import os
import re
import platform
import subprocess
from pathlib import Path
from typing import List

import pytest
import yaml


# Get repository root
REPO_ROOT = Path(__file__).parent.parent.parent


class TestEnvironmentConfiguration:
    """Test environment variable configuration."""
    
    def test_env_example_exists(self):
        """Test that .env.example file exists."""
        env_example = REPO_ROOT / ".env.example"
        assert env_example.exists(), ".env.example file must exist"
    
    def test_env_example_format(self):
        """Test that .env.example has proper format."""
        env_example = REPO_ROOT / ".env.example"
        
        with open(env_example, encoding="utf-8") as f:
            content = f.read()
        
        # Check for required sections
        assert "# ═══ AI Models ═══" in content or "AI Models" in content, \
            ".env.example should have AI Models section"
        assert "GEMINI_API_KEY" in content, \
            ".env.example should include GEMINI_API_KEY"
        
        # Parse lines
        lines = content.split('\n')
        env_vars = {}
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
        
        # Should have at least some required variables
        required_vars = [
            'GEMINI_API_KEY',
            'HOST',
            'PORT'
        ]
        
        for var in required_vars:
            assert var in env_vars, f"Required variable {var} not found in .env.example"
    
    def test_env_required_variables(self):
        """Test that all required environment variables are defined."""
        env_example = REPO_ROOT / ".env.example"
        
        with open(env_example, encoding="utf-8") as f:
            content = f.read()
        
        # Essential variables that must be present
        essential_vars = [
            'GEMINI_API_KEY',
            'COPILOT_MCP_GITHUB_TOKEN',
            'HOST',
            'PORT',
            'DEBUG_MODE',
            'AGENT_NAME',
            'MAX_ITERATIONS',
            'DB_PATH',
            'LOG_LEVEL'
        ]
        
        for var in essential_vars:
            assert var in content, \
                f"Essential variable {var} must be in .env.example"
    
    def test_env_no_actual_secrets(self):
        """Test that .env.example doesn't contain actual secrets."""
        env_example = REPO_ROOT / ".env.example"
        
        with open(env_example, encoding="utf-8") as f:
            content = f.read()
        
        # Check for patterns that look like real secrets
        suspicious_patterns = [
            r'ghp_[a-zA-Z0-9]{36}',  # GitHub tokens
            r'AIza[a-zA-Z0-9_-]{35}',  # Google API keys
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI keys
            r'xoxb-[a-zA-Z0-9-]+',  # Slack tokens
        ]
        
        for pattern in suspicious_patterns:
            matches = re.findall(pattern, content)
            assert not matches, \
                f"Found potential real secret in .env.example: {pattern}"
    
    def test_referenced_env_vars_in_code_exist_in_example(self):
        """Test that env vars referenced in code are in .env.example."""
        # Read .env.example
        env_example = REPO_ROOT / ".env.example"
        with open(env_example, encoding="utf-8") as f:
            env_content = f.read()
        
        # Extract variables from .env.example
        env_vars = set()
        for line in env_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key = line.split('=')[0].strip()
                env_vars.add(key)
        
        # Find environment variables referenced in Python code
        referenced_vars = set()
        
        # Search in src directory
        src_dir = REPO_ROOT / "src"
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    # Look for os.getenv, os.environ, etc.
                    patterns = [
                        r'os\.getenv\(["\']([A-Z_]+)["\']',
                        r'os\.environ\[["\']([A-Z_]+)["\']\]',
                        r'os\.environ\.get\(["\']([A-Z_]+)["\']',
                        r'getenv\(["\']([A-Z_]+)["\']',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        referenced_vars.update(matches)
        
        # Check backend directory too
        backend_dir = REPO_ROOT / "backend"
        if backend_dir.exists():
            for py_file in backend_dir.rglob("*.py"):
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    for pattern in [
                        r'os\.getenv\(["\']([A-Z_]+)["\']',
                        r'os\.environ\[["\']([A-Z_]+)["\']\]',
                        r'os\.environ\.get\(["\']([A-Z_]+)["\']',
                    ]:
                        matches = re.findall(pattern, content)
                        referenced_vars.update(matches)
        
        # Some variables might be system/standard ones, exclude those
        system_vars = {
            'PATH', 'HOME', 'USER', 'SHELL', 'PWD', 
            'LANG', 'TERM', 'PYTHONPATH', 'VIRTUAL_ENV'
        }
        referenced_vars = referenced_vars - system_vars
        
        # Check that referenced vars are in .env.example
        missing_vars = referenced_vars - env_vars
        
        # Some tolerance for optional vars
        if missing_vars:
            print(f"Warning: Variables referenced in code but not in .env.example: {missing_vars}")
            # Only fail if critical vars are missing
            critical_missing = missing_vars - {'REDIS_PASSWORD', 'ANONYMIZED_TELEMETRY'}
            assert len(critical_missing) == 0, \
                f"Critical variables missing from .env.example: {critical_missing}"


class TestMCPConfiguration:
    """Test MCP server configuration."""
    
    def test_mcp_json_exists(self):
        """Test that mcp.json file exists."""
        mcp_json = REPO_ROOT / ".github" / "copilot" / "mcp.json"
        assert mcp_json.exists(), ".github/copilot/mcp.json must exist"
    
    def test_mcp_json_valid_format(self):
        """Test that mcp.json is valid JSON."""
        mcp_json = REPO_ROOT / ".github" / "copilot" / "mcp.json"
        
        with open(mcp_json, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"mcp.json is not valid JSON: {e}")
        
        assert isinstance(data, dict), "mcp.json root should be an object"
    
    def test_mcp_required_fields(self):
        """Test that mcp.json has all required fields."""
        mcp_json = REPO_ROOT / ".github" / "copilot" / "mcp.json"
        
        with open(mcp_json, encoding="utf-8") as f:
            data = json.load(f)
        
        # Check required top-level fields
        assert "$schema" in data or "mcpServers" in data, \
            "mcp.json should have schema or mcpServers field"
        assert "mcpServers" in data, "mcp.json must have mcpServers field"
        
        assert isinstance(data["mcpServers"], dict), \
            "mcpServers must be an object"
    
    def test_mcp_server_configurations(self):
        """Test that each MCP server is properly configured."""
        mcp_json = REPO_ROOT / ".github" / "copilot" / "mcp.json"
        
        with open(mcp_json, encoding="utf-8") as f:
            data = json.load(f)
        
        servers = data.get("mcpServers", {})
        
        # Filter out comment keys
        servers = {k: v for k, v in servers.items() 
                  if not k.startswith("_comment")}
        
        assert len(servers) > 0, "At least one MCP server should be configured"
        
        for server_name, config in servers.items():
            if not isinstance(config, dict):
                continue  # Skip non-dict entries
            
            # Each server should have type and command
            assert "type" in config, \
                f"Server {server_name} must have 'type' field"
            assert "command" in config, \
                f"Server {server_name} must have 'command' field"
            
            # Type should be stdio
            assert config["type"] == "stdio", \
                f"Server {server_name} should use 'stdio' type"
            
            # If has env vars, they should be properly formatted
            if "env" in config:
                env_vars = config["env"]
                assert isinstance(env_vars, dict), \
                    f"Server {server_name} env should be an object"
                
                # Check for proper env var format
                for var_name, var_value in env_vars.items():
                    assert isinstance(var_value, str), \
                        f"Server {server_name} env var {var_name} should be string"
    
    def test_mcp_environment_variables_match(self):
        """Test that MCP env vars are in .env.example."""
        mcp_json = REPO_ROOT / ".github" / "copilot" / "mcp.json"
        env_example = REPO_ROOT / ".env.example"
        
        with open(mcp_json, encoding="utf-8") as f:
            mcp_data = json.load(f)
        
        with open(env_example, encoding="utf-8") as f:
            env_content = f.read()
        
        servers = mcp_data.get("mcpServers", {})
        
        # Extract env vars from MCP config
        mcp_env_vars = set()
        for server_name, config in servers.items():
            if isinstance(config, dict) and "env" in config:
                for var_name, var_value in config["env"].items():
                    # Extract ${VAR_NAME} format
                    if "${" in var_value:
                        var_match = re.search(r'\$\{([A-Z_]+)\}', var_value)
                        if var_match:
                            mcp_env_vars.add(var_match.group(1))
        
        # Filter out optional/disabled server vars
        # Only check required vars
        required_mcp_vars = {
            'COPILOT_MCP_GITHUB_TOKEN',
            'COPILOT_MCP_BRAVE_API_KEY',
            'COPILOT_MCP_POSTGRES_CONNECTION_STRING'
        }
        
        # Check that required vars are in .env.example
        for var in mcp_env_vars & required_mcp_vars:
            assert var in env_content, \
                f"MCP env var {var} should be in .env.example"
    
    def test_mcp_core_servers_enabled(self):
        """Test that core MCP servers are enabled."""
        mcp_json = REPO_ROOT / ".github" / "copilot" / "mcp.json"
        
        with open(mcp_json, encoding="utf-8") as f:
            data = json.load(f)
        
        servers = data.get("mcpServers", {})
        
        # Core servers that should exist
        core_servers = ["filesystem", "git", "github"]
        
        for server in core_servers:
            assert server in servers, \
                f"Core server '{server}' should be configured"
            
            config = servers[server]
            if isinstance(config, dict):
                # Should not be explicitly disabled
                enabled = config.get("enabled", True)
                assert enabled, \
                    f"Core server '{server}' should be enabled"


class TestDockerConfiguration:
    """Test Docker configuration."""
    
    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists."""
        docker_compose = REPO_ROOT / "docker-compose.yml"
        assert docker_compose.exists(), "docker-compose.yml must exist"
    
    def test_docker_compose_valid_yaml(self):
        """Test that docker-compose.yml is valid YAML."""
        docker_compose = REPO_ROOT / "docker-compose.yml"
        
        with open(docker_compose, encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"docker-compose.yml is not valid YAML: {e}")
        
        assert isinstance(data, dict), \
            "docker-compose.yml root should be an object"
    
    def test_docker_compose_version(self):
        """Test that docker-compose.yml has version specified."""
        docker_compose = REPO_ROOT / "docker-compose.yml"
        
        with open(docker_compose, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        assert "version" in data, "docker-compose.yml should specify version"
        
        # Version should be 3.x (modern)
        version = str(data["version"])
        assert version.startswith("3"), \
            f"docker-compose version should be 3.x, got {version}"
    
    def test_docker_compose_required_services(self):
        """Test that required services are defined."""
        docker_compose = REPO_ROOT / "docker-compose.yml"
        
        with open(docker_compose, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        assert "services" in data, "docker-compose.yml must have services"
        
        services = data["services"]
        
        # Required services
        required_services = ["backend"]
        
        for service in required_services:
            assert service in services, \
                f"Required service '{service}' not found in docker-compose.yml"
    
    def test_docker_compose_service_configuration(self):
        """Test that services are properly configured."""
        docker_compose = REPO_ROOT / "docker-compose.yml"
        
        with open(docker_compose, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        services = data.get("services", {})
        
        for service_name, config in services.items():
            # Each service should have basic configuration
            assert isinstance(config, dict), \
                f"Service {service_name} config should be an object"
            
            # Should have either image or build
            has_image = "image" in config
            has_build = "build" in config
            
            assert has_image or has_build, \
                f"Service {service_name} must have 'image' or 'build'"
    
    def test_docker_compose_environment_variables(self):
        """Test that Docker services use proper env vars."""
        docker_compose = REPO_ROOT / "docker-compose.yml"
        env_example = REPO_ROOT / ".env.example"
        
        with open(docker_compose, encoding="utf-8") as f:
            docker_data = yaml.safe_load(f)
        
        with open(env_example, encoding="utf-8") as f:
            env_content = f.read()
        
        services = docker_data.get("services", {})
        
        # Extract env vars from Docker services
        docker_env_vars = set()
        for service_name, config in services.items():
            if "environment" in config:
                env_list = config["environment"]
                for env_entry in env_list:
                    # Handle both list and dict formats
                    if isinstance(env_entry, str):
                        # Format: KEY=${KEY} or KEY=value
                        if "=${" in env_entry:
                            match = re.search(r'=\$\{([A-Z_]+)', env_entry)
                            if match:
                                docker_env_vars.add(match.group(1))
        
        # Check that important vars are in .env.example
        important_vars = docker_env_vars & {
            'GEMINI_API_KEY', 'COPILOT_MCP_GITHUB_TOKEN', 
            'DEBUG_MODE', 'LOCAL_MODEL'
        }
        
        for var in important_vars:
            assert var in env_content, \
                f"Docker env var {var} should be in .env.example"
    
    def test_dockerfile_exists(self):
        """Test that Dockerfile exists."""
        dockerfile = REPO_ROOT / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile must exist"
    
    def test_dockerfile_format(self):
        """Test that Dockerfile has proper format."""
        dockerfile = REPO_ROOT / "Dockerfile"
        
        with open(dockerfile, encoding="utf-8") as f:
            content = f.read()
        
        # Should start with FROM
        assert content.strip().startswith("FROM") or \
               "FROM" in content[:200], \
            "Dockerfile should start with FROM instruction"
        
        # Should have basic instructions
        assert "WORKDIR" in content or "RUN" in content, \
            "Dockerfile should have WORKDIR or RUN instructions"


class TestShellScripts:
    """Test shell script configuration."""
    
    def get_shell_scripts(self) -> List[Path]:
        """Get all shell scripts in repository root."""
        scripts = []
        for item in REPO_ROOT.glob("*.sh"):
            if item.is_file():
                scripts.append(item)
        return scripts
    
    def test_shell_scripts_exist(self):
        """Test that essential shell scripts exist."""
        required_scripts = [
            "install.sh",
            "configure.sh",
            "start.sh",
            "stop.sh"
        ]
        
        for script_name in required_scripts:
            script_path = REPO_ROOT / script_name
            assert script_path.exists(), \
                f"Required script {script_name} must exist"
    
    def test_shell_scripts_executable(self):
        """Test that shell scripts are executable."""
        scripts = self.get_shell_scripts()
        
        assert len(scripts) > 0, "Should have at least one shell script"
        
        for script in scripts:
            # Check if file is executable
            is_executable = os.access(script, os.X_OK)
            assert is_executable, \
                f"Script {script.name} should be executable (chmod +x)"
    
    def test_shell_scripts_shebang(self):
        """Test that shell scripts have proper shebang."""
        scripts = self.get_shell_scripts()
        
        for script in scripts:
            with open(script, encoding="utf-8") as f:
                first_line = f.readline().strip()
            
            assert first_line.startswith("#!"), \
                f"Script {script.name} should start with shebang (#!)"
            
            # Should be bash or sh
            assert "bash" in first_line or "sh" in first_line, \
                f"Script {script.name} should use bash or sh: {first_line}"
    
    def test_shell_scripts_no_syntax_errors(self):
        """Test that shell scripts have no obvious syntax errors."""
        scripts = self.get_shell_scripts()
        
        for script in scripts:
            if platform.system() == "Windows":
                pytest.skip("Skipping bash syntax check on Windows")
            # Try to parse with bash -n (syntax check only)
            try:
                result = subprocess.run(
                    ["bash", "-n", script.as_posix()],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                assert result.returncode == 0, \
                    f"Script {script.name} has syntax errors:\n{result.stderr}"
            
            except subprocess.TimeoutExpired:
                pytest.fail(f"Script {script.name} syntax check timed out")
            except FileNotFoundError:
                pytest.skip("bash not available for syntax checking")
    
    def test_shell_scripts_error_handling(self):
        """Test that shell scripts have error handling."""
        scripts = self.get_shell_scripts()
        
        for script in scripts:
            with open(script, encoding="utf-8") as f:
                content = f.read()
            
            # Check for basic error handling patterns
            has_error_handling = any([
                "set -e" in content,  # Exit on error
                "set -o errexit" in content,
                "|| exit" in content,
                "trap" in content,  # Error traps
            ])
            
            # Some scripts might not need it, but main ones should
            if script.name in ["install.sh", "configure.sh", "start.sh"]:
                assert has_error_handling, \
                    f"Script {script.name} should have error handling (set -e, trap, etc.)"


class TestPythonDependencies:
    """Test Python dependency configuration."""
    
    def test_requirements_txt_exists(self):
        """Test that requirements.txt exists."""
        requirements = REPO_ROOT / "requirements.txt"
        assert requirements.exists(), "requirements.txt must exist"
    
    def test_requirements_txt_format(self):
        """Test that requirements.txt is properly formatted."""
        requirements = REPO_ROOT / "requirements.txt"
        
        with open(requirements, encoding="utf-8") as f:
            lines = f.readlines()
        
        assert len(lines) > 0, "requirements.txt should not be empty"
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Should not have spaces around operators
            if "==" in line or ">=" in line or "<=" in line:
                assert " = " not in line and " > " not in line, \
                    f"Line {i}: Should not have spaces around operators: {line}"
    
    def test_requirements_txt_parseable(self):
        """Test that requirements.txt can be parsed."""
        requirements = REPO_ROOT / "requirements.txt"
        
        with open(requirements, encoding="utf-8") as f:
            lines = f.readlines()
        
        packages = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                # Extract package name
                package_name = re.split(r'[<>=!]', line)[0].strip()
                packages.append(package_name)
        
        assert len(packages) > 0, \
            "requirements.txt should have at least one package"
        
        # Check for essential packages
        essential_packages = ["pytest"]
        
        for package in essential_packages:
            assert any(package.lower() in p.lower() for p in packages), \
                f"Essential package '{package}' should be in requirements.txt"
    
    def test_no_conflicting_dependencies(self):
        """Test that there are no duplicate or conflicting dependencies."""
        requirements = REPO_ROOT / "requirements.txt"
        
        with open(requirements, encoding="utf-8") as f:
            lines = f.readlines()
        
        packages = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                # Extract package name
                package_name = re.split(r'[<>=!]', line)[0].strip().lower()
                
                if package_name in packages:
                    pytest.fail(
                        f"Duplicate package '{package_name}' in requirements.txt:\n"
                        f"  {packages[package_name]}\n"
                        f"  {line}"
                    )
                
                packages[package_name] = line
    
    def test_pytest_configured(self):
        """Test that pytest is properly configured."""
        pytest_ini = REPO_ROOT / "pytest.ini"
        pyproject_toml = REPO_ROOT / "pyproject.toml"
        setup_cfg = REPO_ROOT / "setup.cfg"
        
        # At least one pytest config should exist
        has_config = any([
            pytest_ini.exists(),
            pyproject_toml.exists(),
            setup_cfg.exists()
        ])
        
        assert has_config, \
            "Should have pytest configuration (pytest.ini, pyproject.toml, or setup.cfg)"
        
        if pytest_ini.exists():
            with open(pytest_ini, encoding="utf-8") as f:
                content = f.read()
            
            assert "[pytest]" in content or "[tool:pytest]" in content, \
                "pytest.ini should have [pytest] section"


class TestGitConfiguration:
    """Test Git configuration."""
    
    def test_gitignore_exists(self):
        """Test that .gitignore exists."""
        gitignore = REPO_ROOT / ".gitignore"
        assert gitignore.exists(), ".gitignore must exist"
    
    def test_gitignore_covers_sensitive_files(self):
        """Test that .gitignore covers sensitive files."""
        gitignore = REPO_ROOT / ".gitignore"
        
        with open(gitignore, encoding="utf-8") as f:
            content = f.read()
        
        # Should ignore sensitive files
        sensitive_patterns = [
            ".env",  # Environment files
            "__pycache__",  # Python cache
            ("*.pyc", "*.py[cod]"),  # Python compiled (either format)
        ]
        
        for pattern in sensitive_patterns:
            if isinstance(pattern, tuple):
                # Check if any of the alternatives exist
                found = any(p in content for p in pattern)
                assert found, \
                    f".gitignore should include one of {pattern}"
            else:
                assert pattern in content, \
                    f".gitignore should include '{pattern}'"
    
    def test_no_env_file_committed(self):
        """Test that .env file is not committed."""
        env_file = REPO_ROOT / ".env"
        
        # .env shouldn't exist in repo (only .env.example)
        if env_file.exists():
            # Check if it's tracked by git
            try:
                result = subprocess.run(
                    ["git", "ls-files", "--error-unmatch", ".env"],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    timeout=5
                )
                
                assert result.returncode != 0, \
                    ".env file should not be tracked by git (add to .gitignore)"
            
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pytest.skip("Git not available for checking")


class TestCIConfiguration:
    """Test CI/CD configuration."""
    
    def test_github_workflows_directory_exists(self):
        """Test that .github/workflows directory exists."""
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        assert workflows_dir.exists(), \
            ".github/workflows directory must exist"
    
    def test_test_workflow_exists(self):
        """Test that test workflow exists."""
        test_workflow = REPO_ROOT / ".github" / "workflows" / "test.yml"
        ci_workflow = REPO_ROOT / ".github" / "workflows" / "ci.yml"
        
        assert test_workflow.exists() or ci_workflow.exists(), \
            "Should have test.yml or ci.yml workflow"
    
    def test_workflow_valid_yaml(self):
        """Test that workflow files are valid YAML."""
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        
        if not workflows_dir.exists():
            pytest.skip("No workflows directory")
        
        workflow_files = list(workflows_dir.glob("*.yml")) + \
                        list(workflows_dir.glob("*.yaml"))
        
        assert len(workflow_files) > 0, "Should have at least one workflow file"
        
        for workflow_file in workflow_files:
            with open(workflow_file, encoding="utf-8") as f:
                try:
                    data = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(
                        f"Workflow {workflow_file.name} is not valid YAML: {e}"
                    )
            
            assert isinstance(data, dict), \
                f"Workflow {workflow_file.name} root should be an object"
    
    def test_workflow_has_required_fields(self):
        """Test that workflows have required fields."""
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        
        if not workflows_dir.exists():
            pytest.skip("No workflows directory")
        
        workflow_files = list(workflows_dir.glob("*.yml")) + \
                        list(workflows_dir.glob("*.yaml"))
        
        for workflow_file in workflow_files:
            with open(workflow_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            # Each workflow should have name, on, jobs
            assert "name" in data, \
                f"Workflow {workflow_file.name} should have 'name'"
            
            # YAML can parse 'on' as boolean True, check for that too
            has_on = "on" in data or True in data
            assert has_on, \
                f"Workflow {workflow_file.name} should have 'on' triggers"
            
            assert "jobs" in data, \
                f"Workflow {workflow_file.name} should have 'jobs'"
            
            # Jobs should be non-empty
            jobs = data.get("jobs", {})
            assert len(jobs) > 0, \
                f"Workflow {workflow_file.name} should have at least one job"
