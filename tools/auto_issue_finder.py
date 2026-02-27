#!/usr/bin/env python3
"""
Smart Auto-Issue Finder Tool

A comprehensive diagnostic tool that automatically scans the codebase for issues,
validates configurations, checks dependencies, and provides auto-fix capabilities.

Usage:
    python tools/auto_issue_finder.py
    python tools/auto_issue_finder.py --checks static,shell,config
    python tools/auto_issue_finder.py --auto-fix
    python tools/auto_issue_finder.py --output json
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Set


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class CheckType(Enum):
    """Types of checks performed."""
    STATIC = "static"
    SHELL = "shell"
    CONFIG = "config"
    DEPENDENCY = "dependency"
    RUNTIME = "runtime"
    DOCKER = "docker"


@dataclass
class Issue:
    """Represents a detected issue."""
    severity: Severity
    check_type: CheckType
    file_path: str
    line_number: Optional[int]
    message: str
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    fixed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            'severity': self.severity.value,
            'check_type': self.check_type.value,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'message': self.message,
            'suggestion': self.suggestion,
            'auto_fixable': self.auto_fixable,
            'fixed': self.fixed
        }


@dataclass
class DiagnosticReport:
    """Complete diagnostic report."""
    issues: List[Issue] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    timestamp: str = ""
    duration: float = 0.0
    
    def add_issue(self, issue: Issue) -> None:
        """Add an issue to the report."""
        self.issues.append(issue)
        
    def get_summary(self) -> Dict[str, int]:
        """Generate summary statistics."""
        summary = {
            'total': len(self.issues),
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0,
            'fixed': 0
        }
        
        for issue in self.issues:
            severity_key = issue.severity.value.lower()
            summary[severity_key] = summary.get(severity_key, 0) + 1
            if issue.fixed:
                summary['fixed'] += 1
                
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            'timestamp': self.timestamp,
            'duration': self.duration,
            'summary': self.get_summary(),
            'issues': [issue.to_dict() for issue in self.issues]
        }


class ColorOutput:
    """ANSI color codes for terminal output."""
    CRITICAL = '\033[91m'  # Red
    HIGH = '\033[93m'      # Yellow
    MEDIUM = '\033[94m'    # Blue
    LOW = '\033[92m'       # Green
    INFO = '\033[96m'      # Cyan
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    @classmethod
    def disable(cls) -> None:
        """Disable color output."""
        cls.CRITICAL = ''
        cls.HIGH = ''
        cls.MEDIUM = ''
        cls.LOW = ''
        cls.INFO = ''
        cls.BOLD = ''
        cls.RESET = ''


class StaticAnalyzer:
    """Performs static analysis on Python files."""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.issues: List[Issue] = []
        
    def analyze(self) -> List[Issue]:
        """Run all static analysis checks."""
        self.issues = []
        
        python_files = self._find_python_files()
        
        if self.verbose:
            print(f"📊 Analyzing {len(python_files)} Python files...")
        
        for file_path in python_files:
            self._analyze_file(file_path)
            
        return self.issues
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        exclude_dirs = {'.git', '__pycache__', 'venv', 'node_modules', '.venv', 'env'}
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
                    
        return python_files
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check syntax
            try:
                tree = ast.parse(content, filename=str(file_path))
                self._check_ast(tree, file_path, content)
            except SyntaxError as e:
                self.issues.append(Issue(
                    severity=Severity.CRITICAL,
                    check_type=CheckType.STATIC,
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=e.lineno,
                    message=f"Syntax error: {e.msg}",
                    suggestion="Fix the syntax error in the code"
                ))
                return
            
            # Check for common issues
            self._check_imports(content, file_path)
            self._check_security(content, file_path)
            self._check_docstrings(tree, file_path)
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error analyzing {file_path}: {e}")
    
    def _check_ast(self, tree: ast.AST, file_path: Path, content: str) -> None:
        """Check AST for common issues."""
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            # Check for undefined variables (simple heuristic)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                # This is a simple check - a real implementation would need scope analysis
                pass
            
            # Check for bare except clauses
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.issues.append(Issue(
                        severity=Severity.MEDIUM,
                        check_type=CheckType.STATIC,
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=node.lineno,
                        message="Bare except clause found - catches all exceptions",
                        suggestion="Specify exception types: except (ValueError, KeyError):"
                    ))
            
            # Check for dangerous eval/exec usage
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ('eval', 'exec'):
                        self.issues.append(Issue(
                            severity=Severity.HIGH,
                            check_type=CheckType.STATIC,
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=node.lineno,
                            message=f"Dangerous use of {node.func.id}() - security risk",
                            suggestion="Avoid using eval/exec or sanitize input carefully"
                        ))
    
    def _check_imports(self, content: str, file_path: Path) -> None:
        """Check for import issues."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for star imports
            if re.match(r'^\s*from .+ import \*', line):
                self.issues.append(Issue(
                    severity=Severity.LOW,
                    check_type=CheckType.STATIC,
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=i,
                    message="Star import found - pollutes namespace",
                    suggestion="Import specific names instead of using *"
                ))
    
    def _check_security(self, content: str, file_path: Path) -> None:
        """Check for security issues."""
        lines = content.split('\n')
        
        # Check for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Potential hardcoded password'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'Potential hardcoded API key'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'Potential hardcoded secret'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'Potential hardcoded token'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Skip if it's in a comment or is clearly a placeholder
                    if '#' not in line and 'YOUR_' not in line.upper() and 'EXAMPLE' not in line.upper():
                        self.issues.append(Issue(
                            severity=Severity.HIGH,
                            check_type=CheckType.STATIC,
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=i,
                            message=message,
                            suggestion="Use environment variables or secure secret management"
                        ))
            
            # Check for SQL injection risks
            if 'execute(' in line or 'executemany(' in line:
                if '%s' in line or '+' in line:
                    self.issues.append(Issue(
                        severity=Severity.HIGH,
                        check_type=CheckType.STATIC,
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=i,
                        message="Potential SQL injection risk",
                        suggestion="Use parameterized queries instead of string concatenation"
                    ))
    
    def _check_docstrings(self, tree: ast.AST, file_path: Path) -> None:
        """Check for missing docstrings."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)
                if not docstring and not node.name.startswith('_'):
                    # Skip short functions and test files
                    if 'test_' not in str(file_path):
                        self.issues.append(Issue(
                            severity=Severity.INFO,
                            check_type=CheckType.STATIC,
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=node.lineno,
                            message=f"Missing docstring for {node.__class__.__name__.lower().replace('def', '')} '{node.name}'",
                            suggestion="Add a docstring describing the purpose and parameters"
                        ))


class ShellScriptLinter:
    """Lints shell scripts for common issues."""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.issues: List[Issue] = []
        
    def analyze(self) -> List[Issue]:
        """Analyze all shell scripts."""
        self.issues = []
        
        shell_files = self._find_shell_files()
        
        if self.verbose:
            print(f"🐚 Analyzing {len(shell_files)} shell scripts...")
        
        for file_path in shell_files:
            self._analyze_file(file_path)
            
        return self.issues
    
    def _find_shell_files(self) -> List[Path]:
        """Find all shell script files."""
        shell_files = []
        exclude_dirs = {'.git', 'node_modules', 'venv', '.venv'}
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.sh') or file.endswith('.bash'):
                    shell_files.append(Path(root) / file)
                    
        return shell_files
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single shell script."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check shebang
            if not content.startswith('#!'):
                self.issues.append(Issue(
                    severity=Severity.MEDIUM,
                    check_type=CheckType.SHELL,
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=1,
                    message="Missing shebang",
                    suggestion="Add #!/bin/bash or #!/usr/bin/env bash at the top",
                    auto_fixable=True
                ))
            
            # Check for common issues
            for i, line in enumerate(lines, 1):
                self._check_line(line, i, file_path)
            
            # Try shellcheck if available
            self._run_shellcheck(file_path)
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error analyzing {file_path}: {e}")
    
    def _check_line(self, line: str, line_num: int, file_path: Path) -> None:
        """Check a single line for issues."""
        # Skip comments and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            return
        
        # Check for unquoted variables
        if '$' in line and not re.search(r'\$\{[^}]+\}|"[^"]*\$[^"]*"', line):
            if re.search(r'\$[A-Za-z_][A-Za-z0-9_]*(?!\})', line):
                self.issues.append(Issue(
                    severity=Severity.MEDIUM,
                    check_type=CheckType.SHELL,
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=line_num,
                    message="Unquoted variable - may cause word splitting",
                    suggestion='Quote variables: "$VAR" instead of $VAR'
                ))
        
        # Check for dangerous commands
        dangerous_commands = ['rm -rf /', 'dd if=', ':(){ :|:& };:']
        for cmd in dangerous_commands:
            if cmd in line:
                self.issues.append(Issue(
                    severity=Severity.CRITICAL,
                    check_type=CheckType.SHELL,
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=line_num,
                    message=f"Dangerous command found: {cmd}",
                    suggestion="Review this command carefully before execution"
                ))
        
        # Check for set -e usage
        if 'set -e' not in line and line_num < 10 and 'bash' in str(file_path):
            # Only suggest once per file
            pass
    
    def _run_shellcheck(self, file_path: Path) -> None:
        """Run shellcheck if available."""
        try:
            result = subprocess.run(
                ['shellcheck', '-f', 'json', str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                findings = json.loads(result.stdout)
                for finding in findings:
                    severity_map = {
                        'error': Severity.HIGH,
                        'warning': Severity.MEDIUM,
                        'info': Severity.LOW,
                        'style': Severity.INFO
                    }
                    
                    self.issues.append(Issue(
                        severity=severity_map.get(finding.get('level', 'info'), Severity.INFO),
                        check_type=CheckType.SHELL,
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=finding.get('line'),
                        message=finding.get('message', 'ShellCheck issue'),
                        suggestion=None
                    ))
                    
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # shellcheck not available or failed
            pass


class ConfigValidator:
    """Validates configuration files."""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.issues: List[Issue] = []
        
    def analyze(self) -> List[Issue]:
        """Validate all configuration files."""
        self.issues = []
        
        if self.verbose:
            print("⚙️  Validating configuration files...")
        
        self._check_env_example()
        self._check_mcp_json()
        self._check_docker_compose()
        self._check_requirements()
        
        return self.issues
    
    def _check_env_example(self) -> None:
        """Check .env.example file."""
        env_example = self.project_root / '.env.example'
        
        if not env_example.exists():
            self.issues.append(Issue(
                severity=Severity.HIGH,
                check_type=CheckType.CONFIG,
                file_path='.env.example',
                line_number=None,
                message=".env.example file is missing",
                suggestion="Create .env.example with all required environment variables",
                auto_fixable=True
            ))
            return
        
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            
            # Check for common required variables
            required_vars = ['DATABASE_URL', 'SECRET_KEY', 'API_KEY']
            for var in required_vars:
                if var not in content and 'example' in str(env_example).lower():
                    self.issues.append(Issue(
                        severity=Severity.INFO,
                        check_type=CheckType.CONFIG,
                        file_path='.env.example',
                        line_number=None,
                        message=f"Consider adding {var} to .env.example",
                        suggestion=f"Add: {var}=your_{var.lower()}_here"
                    ))
                    
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error checking .env.example: {e}")
    
    def _check_mcp_json(self) -> None:
        """Check mcp.json configuration."""
        mcp_json = self.project_root / 'mcp.json'
        
        if not mcp_json.exists():
            self.issues.append(Issue(
                severity=Severity.MEDIUM,
                check_type=CheckType.CONFIG,
                file_path='mcp.json',
                line_number=None,
                message="mcp.json file is missing",
                suggestion="Create mcp.json with MCP server configuration"
            ))
            return
        
        try:
            with open(mcp_json, 'r') as f:
                config = json.load(f)
            
            # Validate structure
            if not isinstance(config, dict):
                self.issues.append(Issue(
                    severity=Severity.HIGH,
                    check_type=CheckType.CONFIG,
                    file_path='mcp.json',
                    line_number=None,
                    message="mcp.json has invalid structure - must be an object",
                    suggestion="Fix JSON structure"
                ))
                
        except json.JSONDecodeError as e:
            self.issues.append(Issue(
                severity=Severity.HIGH,
                check_type=CheckType.CONFIG,
                file_path='mcp.json',
                line_number=None,
                message=f"Invalid JSON in mcp.json: {e}",
                suggestion="Fix JSON syntax errors"
            ))
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error checking mcp.json: {e}")
    
    def _check_docker_compose(self) -> None:
        """Check docker-compose.yml file."""
        compose_file = self.project_root / 'docker-compose.yml'
        
        if not compose_file.exists():
            self.issues.append(Issue(
                severity=Severity.LOW,
                check_type=CheckType.CONFIG,
                file_path='docker-compose.yml',
                line_number=None,
                message="docker-compose.yml file is missing",
                suggestion="Create docker-compose.yml for container orchestration"
            ))
            return
        
        try:
            import yaml
            with open(compose_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(config, dict):
                self.issues.append(Issue(
                    severity=Severity.HIGH,
                    check_type=CheckType.CONFIG,
                    file_path='docker-compose.yml',
                    line_number=None,
                    message="Invalid docker-compose.yml structure",
                    suggestion="Fix YAML structure"
                ))
                
        except ImportError:
            # PyYAML not installed
            if self.verbose:
                print("⚠️  PyYAML not installed - skipping YAML validation")
        except Exception as e:
            self.issues.append(Issue(
                severity=Severity.HIGH,
                check_type=CheckType.CONFIG,
                file_path='docker-compose.yml',
                line_number=None,
                message=f"Error parsing docker-compose.yml: {e}",
                suggestion="Fix YAML syntax errors"
            ))
    
    def _check_requirements(self) -> None:
        """Check requirements.txt file."""
        req_file = self.project_root / 'requirements.txt'
        
        if not req_file.exists():
            self.issues.append(Issue(
                severity=Severity.HIGH,
                check_type=CheckType.CONFIG,
                file_path='requirements.txt',
                line_number=None,
                message="requirements.txt file is missing",
                suggestion="Create requirements.txt with project dependencies",
                auto_fixable=True
            ))
            return
        
        try:
            with open(req_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Check for version pinning
                    if '==' not in line and '>=' not in line and '~=' not in line:
                        self.issues.append(Issue(
                            severity=Severity.LOW,
                            check_type=CheckType.CONFIG,
                            file_path='requirements.txt',
                            line_number=i,
                            message=f"Package '{line}' not version-pinned",
                            suggestion="Pin package versions for reproducibility: package==1.0.0"
                        ))
                        
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error checking requirements.txt: {e}")


class DependencyChecker:
    """Checks Python dependencies."""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.issues: List[Issue] = []
        
    def analyze(self) -> List[Issue]:
        """Check all dependencies."""
        self.issues = []
        
        if self.verbose:
            print("📦 Checking dependencies...")
        
        self._check_installability()
        self._check_conflicts()
        
        return self.issues
    
    def _check_installability(self) -> None:
        """Check if requirements can be installed."""
        req_file = self.project_root / 'requirements.txt'
        
        if not req_file.exists():
            return
        
        try:
            # Try to parse requirements
            with open(req_file, 'r') as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Basic validation
                        if ' ' in line and '==' not in line:
                            self.issues.append(Issue(
                                severity=Severity.MEDIUM,
                                check_type=CheckType.DEPENDENCY,
                                file_path='requirements.txt',
                                line_number=i,
                                message=f"Invalid requirement format: '{line}'",
                                suggestion="Use format: package==version"
                            ))
                            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error checking dependencies: {e}")
    
    def _check_conflicts(self) -> None:
        """Check for version conflicts."""
        # This would require pip's resolver - simplified for now
        pass


class RuntimeHealthChecker:
    """Performs runtime health checks."""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.issues: List[Issue] = []
        
    def analyze(self) -> List[Issue]:
        """Perform runtime health checks."""
        self.issues = []
        
        if self.verbose:
            print("🏥 Performing runtime health checks...")
        
        self._check_file_permissions()
        self._check_required_directories()
        
        return self.issues
    
    def _check_file_permissions(self) -> None:
        """Check file permissions."""
        # Check if shell scripts are executable
        for script in self.project_root.glob('*.sh'):
            if not os.access(script, os.X_OK):
                self.issues.append(Issue(
                    severity=Severity.MEDIUM,
                    check_type=CheckType.RUNTIME,
                    file_path=str(script.relative_to(self.project_root)),
                    line_number=None,
                    message=f"Script '{script.name}' is not executable",
                    suggestion=f"Run: chmod +x {script.name}",
                    auto_fixable=True
                ))
    
    def _check_required_directories(self) -> None:
        """Check for required directories."""
        required_dirs = ['logs', 'data', 'uploads']
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                self.issues.append(Issue(
                    severity=Severity.INFO,
                    check_type=CheckType.RUNTIME,
                    file_path=dir_name,
                    line_number=None,
                    message=f"Directory '{dir_name}' does not exist",
                    suggestion=f"Create directory: mkdir -p {dir_name}",
                    auto_fixable=True
                ))


class DockerValidator:
    """Validates Docker configuration."""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.issues: List[Issue] = []
        
    def analyze(self) -> List[Issue]:
        """Validate Docker configuration."""
        self.issues = []
        
        if self.verbose:
            print("🐳 Validating Docker configuration...")
        
        self._check_dockerfile()
        self._check_dockerignore()
        
        return self.issues
    
    def _check_dockerfile(self) -> None:
        """Check Dockerfile."""
        dockerfile = self.project_root / 'Dockerfile'
        
        if not dockerfile.exists():
            self.issues.append(Issue(
                severity=Severity.LOW,
                check_type=CheckType.DOCKER,
                file_path='Dockerfile',
                line_number=None,
                message="Dockerfile is missing",
                suggestion="Create Dockerfile for containerization"
            ))
            return
        
        try:
            with open(dockerfile, 'r') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for FROM statement
            if not any(line.strip().startswith('FROM') for line in lines):
                self.issues.append(Issue(
                    severity=Severity.HIGH,
                    check_type=CheckType.DOCKER,
                    file_path='Dockerfile',
                    line_number=1,
                    message="Dockerfile missing FROM statement",
                    suggestion="Add: FROM python:3.10-slim"
                ))
            
            # Check for USER statement (security)
            if not any(line.strip().startswith('USER') for line in lines):
                self.issues.append(Issue(
                    severity=Severity.MEDIUM,
                    check_type=CheckType.DOCKER,
                    file_path='Dockerfile',
                    line_number=None,
                    message="Dockerfile runs as root user",
                    suggestion="Add USER statement to run as non-root user"
                ))
                
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error checking Dockerfile: {e}")
    
    def _check_dockerignore(self) -> None:
        """Check .dockerignore file."""
        dockerignore = self.project_root / '.dockerignore'
        
        if not dockerignore.exists():
            self.issues.append(Issue(
                severity=Severity.LOW,
                check_type=CheckType.DOCKER,
                file_path='.dockerignore',
                line_number=None,
                message=".dockerignore file is missing",
                suggestion="Create .dockerignore to exclude unnecessary files from image",
                auto_fixable=True
            ))


class AutoFixer:
    """Automatically fixes issues when possible."""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        
    def fix_issues(self, issues: List[Issue]) -> List[Issue]:
        """Fix all auto-fixable issues."""
        fixed_issues = []
        
        for issue in issues:
            if issue.auto_fixable:
                if self._fix_issue(issue):
                    issue.fixed = True
                    fixed_issues.append(issue)
                    
        return fixed_issues
    
    def _fix_issue(self, issue: Issue) -> bool:
        """Fix a single issue."""
        try:
            # Fix missing shebang
            if "Missing shebang" in issue.message:
                return self._add_shebang(issue.file_path)
            
            # Fix executable permissions
            if "not executable" in issue.message:
                return self._make_executable(issue.file_path)
            
            # Create missing directories
            if "does not exist" in issue.message and "Directory" in issue.message:
                return self._create_directory(issue.file_path)
            
            # Create missing .dockerignore
            if ".dockerignore" in issue.file_path and "missing" in issue.message:
                return self._create_dockerignore()
            
            return False
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Failed to fix issue: {e}")
            return False
    
    def _add_shebang(self, file_path: str) -> bool:
        """Add shebang to shell script."""
        full_path = self.project_root / file_path
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        with open(full_path, 'w') as f:
            f.write('#!/usr/bin/env bash\n' + content)
        
        if self.verbose:
            print(f"✓ Added shebang to {file_path}")
        
        return True
    
    def _make_executable(self, file_path: str) -> bool:
        """Make file executable."""
        full_path = self.project_root / file_path
        os.chmod(full_path, os.stat(full_path).st_mode | 0o111)
        
        if self.verbose:
            print(f"✓ Made {file_path} executable")
        
        return True
    
    def _create_directory(self, dir_name: str) -> bool:
        """Create missing directory."""
        full_path = self.project_root / dir_name
        full_path.mkdir(parents=True, exist_ok=True)
        
        if self.verbose:
            print(f"✓ Created directory {dir_name}")
        
        return True
    
    def _create_dockerignore(self) -> bool:
        """Create .dockerignore file."""
        dockerignore_content = """# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Environment
.env
.env.local
"""
        
        dockerignore_path = self.project_root / '.dockerignore'
        with open(dockerignore_path, 'w') as f:
            f.write(dockerignore_content)
        
        if self.verbose:
            print("✓ Created .dockerignore")
        
        return True


class ReportGenerator:
    """Generates diagnostic reports."""
    
    @staticmethod
    def generate_json(report: DiagnosticReport) -> str:
        """Generate JSON report."""
        return json.dumps(report.to_dict(), indent=2)
    
    @staticmethod
    def generate_markdown(report: DiagnosticReport) -> str:
        """Generate Markdown report."""
        md = "# Diagnostic Report\n\n"
        md += f"**Timestamp:** {report.timestamp}\n"
        md += f"**Duration:** {report.duration:.2f}s\n\n"
        
        summary = report.get_summary()
        md += "## Summary\n\n"
        md += f"- **Total Issues:** {summary['total']}\n"
        md += f"- **Critical:** {summary.get('critical', 0)}\n"
        md += f"- **High:** {summary.get('high', 0)}\n"
        md += f"- **Medium:** {summary.get('medium', 0)}\n"
        md += f"- **Low:** {summary.get('low', 0)}\n"
        md += f"- **Info:** {summary.get('info', 0)}\n"
        md += f"- **Fixed:** {summary.get('fixed', 0)}\n\n"
        
        if report.issues:
            md += "## Issues\n\n"
            
            # Group by severity
            for severity in Severity:
                issues = [i for i in report.issues if i.severity == severity]
                if issues:
                    md += f"### {severity.value}\n\n"
                    for issue in issues:
                        md += f"**{issue.file_path}"
                        if issue.line_number:
                            md += f":{issue.line_number}"
                        md += "**\n"
                        md += f"- {issue.message}\n"
                        if issue.suggestion:
                            md += f"- *Suggestion:* {issue.suggestion}\n"
                        if issue.fixed:
                            md += "- ✓ *Fixed*\n"
                        md += "\n"
        
        return md
    
    @staticmethod
    def generate_terminal(report: DiagnosticReport, use_color: bool = True) -> str:
        """Generate terminal-friendly report."""
        if not use_color:
            ColorOutput.disable()
        
        output = []
        output.append(f"\n{ColorOutput.BOLD}=== Diagnostic Report ==={ColorOutput.RESET}\n")
        output.append(f"Timestamp: {report.timestamp}")
        output.append(f"Duration: {report.duration:.2f}s\n")
        
        summary = report.get_summary()
        output.append(f"{ColorOutput.BOLD}Summary:{ColorOutput.RESET}")
        output.append(f"  Total Issues: {summary['total']}")
        output.append(f"  {ColorOutput.CRITICAL}Critical: {summary.get('critical', 0)}{ColorOutput.RESET}")
        output.append(f"  {ColorOutput.HIGH}High: {summary.get('high', 0)}{ColorOutput.RESET}")
        output.append(f"  {ColorOutput.MEDIUM}Medium: {summary.get('medium', 0)}{ColorOutput.RESET}")
        output.append(f"  {ColorOutput.LOW}Low: {summary.get('low', 0)}{ColorOutput.RESET}")
        output.append(f"  {ColorOutput.INFO}Info: {summary.get('info', 0)}{ColorOutput.RESET}")
        output.append(f"  Fixed: {summary.get('fixed', 0)}\n")
        
        if report.issues:
            output.append(f"{ColorOutput.BOLD}Issues:{ColorOutput.RESET}\n")
            
            for issue in report.issues:
                color = getattr(ColorOutput, issue.severity.value, ColorOutput.RESET)
                file_info = f"{color}[{issue.severity.value}]{ColorOutput.RESET} {issue.file_path}"
                if issue.line_number:
                    file_info += f":{issue.line_number}"
                output.append(file_info)
                output.append(f"  {issue.message}")
                if issue.suggestion:
                    output.append(f"  💡 {issue.suggestion}")
                if issue.fixed:
                    output.append("  ✓ Fixed")
                output.append("")
        
        return '\n'.join(output)


class AutoIssueFinder:
    """Main auto-issue finder class."""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.report = DiagnosticReport()
        
    def run(self, checks: Set[CheckType], auto_fix: bool = False) -> DiagnosticReport:
        """Run all specified checks."""
        import time
        from datetime import datetime
        
        start_time = time.time()
        self.report.timestamp = datetime.now().isoformat()
        
        # Run checks
        if CheckType.STATIC in checks:
            analyzer = StaticAnalyzer(self.project_root, self.verbose)
            for issue in analyzer.analyze():
                self.report.add_issue(issue)
        
        if CheckType.SHELL in checks:
            linter = ShellScriptLinter(self.project_root, self.verbose)
            for issue in linter.analyze():
                self.report.add_issue(issue)
        
        if CheckType.CONFIG in checks:
            validator = ConfigValidator(self.project_root, self.verbose)
            for issue in validator.analyze():
                self.report.add_issue(issue)
        
        if CheckType.DEPENDENCY in checks:
            checker = DependencyChecker(self.project_root, self.verbose)
            for issue in checker.analyze():
                self.report.add_issue(issue)
        
        if CheckType.RUNTIME in checks:
            health_checker = RuntimeHealthChecker(self.project_root, self.verbose)
            for issue in health_checker.analyze():
                self.report.add_issue(issue)
        
        if CheckType.DOCKER in checks:
            docker_validator = DockerValidator(self.project_root, self.verbose)
            for issue in docker_validator.analyze():
                self.report.add_issue(issue)
        
        # Auto-fix if requested
        if auto_fix:
            if self.verbose:
                print("\n🔧 Attempting to auto-fix issues...")
            fixer = AutoFixer(self.project_root, self.verbose)
            fixer.fix_issues(self.report.issues)
        
        self.report.duration = time.time() - start_time
        
        return self.report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Smart Auto-Issue Finder - Comprehensive diagnostic tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--checks',
        type=str,
        default='all',
        help='Comma-separated list of checks to run: static,shell,config,dependency,runtime,docker (default: all)'
    )
    
    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='Automatically fix issues when possible'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        choices=['terminal', 'json', 'markdown'],
        default='terminal',
        help='Output format (default: terminal)'
    )
    
    parser.add_argument(
        '--output-file',
        type=str,
        help='Write output to file'
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
    
    args = parser.parse_args()
    
    # Parse checks
    if args.checks.lower() == 'all':
        checks = set(CheckType)
    else:
        check_names = [c.strip().lower() for c in args.checks.split(',')]
        checks = set()
        for name in check_names:
            try:
                checks.add(CheckType(name))
            except ValueError:
                print(f"⚠️  Unknown check type: {name}")
                return 1
    
    # Run diagnostics
    project_root = Path(args.project_root).resolve()
    
    if args.verbose:
        print(f"🔍 Running diagnostics on {project_root}...")
        print(f"📋 Checks: {', '.join(c.value for c in checks)}\n")
    
    finder = AutoIssueFinder(project_root, args.verbose)
    report = finder.run(checks, args.auto_fix)
    
    # Generate output
    if args.output == 'json':
        output = ReportGenerator.generate_json(report)
    elif args.output == 'markdown':
        output = ReportGenerator.generate_markdown(report)
    else:
        output = ReportGenerator.generate_terminal(report, not args.no_color)
    
    # Write output
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(output)
        print(f"✓ Report written to {args.output_file}")
    else:
        # Force UTF-8 output for Windows
        if sys.platform == 'win32':
            sys.stdout.reconfigure(encoding='utf-8')
        print(output)
    
    # Determine exit code
    summary = report.get_summary()
    if summary.get('critical', 0) > 0:
        return 3
    elif summary.get('high', 0) > 0:
        return 2
    elif summary.get('medium', 0) > 0 or summary.get('low', 0) > 0:
        return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
