"""
Comprehensive tests for auto_issue_finder.py

Tests all diagnostic functions including:
- Static analysis
- Shell script linting
- Configuration validation
- Dependency checking
- Runtime health checks
- Docker validation
- Auto-fix capabilities
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from auto_issue_finder import (
    StaticAnalyzer,
    ShellScriptLinter,
    ConfigValidator,
    DependencyChecker,
    RuntimeHealthChecker,
    DockerValidator,
    AutoFixer,
    AutoIssueFinder,
    Severity,
    CheckType,
    Issue,
    DiagnosticReport,
    ReportGenerator
)


@pytest.fixture
def temp_project():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir)
    
    # Create basic structure
    (project_path / 'src').mkdir()
    (project_path / 'tests').mkdir()
    (project_path / 'scripts').mkdir()
    
    yield project_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestStaticAnalyzer:
    """Test static analysis functionality."""
    
    def test_find_syntax_error(self, temp_project):
        """Test detection of syntax errors."""
        # Create file with syntax error
        bad_file = temp_project / 'src' / 'bad_syntax.py'
        bad_file.write_text("def foo(\n    print('missing closing paren')")
        
        analyzer = StaticAnalyzer(temp_project)
        issues = analyzer.analyze()
        
        # Should find syntax error
        syntax_issues = [i for i in issues if 'syntax' in i.message.lower()]
        assert len(syntax_issues) > 0
        assert syntax_issues[0].severity == Severity.CRITICAL
    
    def test_find_bare_except(self, temp_project):
        """Test detection of bare except clauses."""
        code_file = temp_project / 'src' / 'exceptions.py'
        code_file.write_text("""
def risky_function():
    try:
        dangerous_operation()
    except:
        pass
""")
        
        analyzer = StaticAnalyzer(temp_project)
        issues = analyzer.analyze()
        
        # Should find bare except
        except_issues = [i for i in issues if 'bare except' in i.message.lower()]
        assert len(except_issues) > 0
        assert except_issues[0].severity == Severity.MEDIUM
    
    def test_find_star_import(self, temp_project):
        """Test detection of star imports."""
        code_file = temp_project / 'src' / 'imports.py'
        code_file.write_text("from os import *\n")
        
        analyzer = StaticAnalyzer(temp_project)
        issues = analyzer.analyze()
        
        # Should find star import
        import_issues = [i for i in issues if 'star import' in i.message.lower()]
        assert len(import_issues) > 0
        assert import_issues[0].severity == Severity.LOW
    
    def test_find_hardcoded_password(self, temp_project):
        """Test detection of hardcoded secrets."""
        code_file = temp_project / 'src' / 'config.py'
        code_file.write_text('password = "supersecret123"\n')
        
        analyzer = StaticAnalyzer(temp_project)
        issues = analyzer.analyze()
        
        # Should find hardcoded password
        security_issues = [i for i in issues if 'password' in i.message.lower()]
        assert len(security_issues) > 0
        assert security_issues[0].severity == Severity.HIGH
    
    def test_find_eval_usage(self, temp_project):
        """Test detection of dangerous eval usage."""
        code_file = temp_project / 'src' / 'dangerous.py'
        code_file.write_text("""
def execute_code(code):
    return eval(code)
""")
        
        analyzer = StaticAnalyzer(temp_project)
        issues = analyzer.analyze()
        
        # Should find eval usage
        eval_issues = [i for i in issues if 'eval' in i.message.lower()]
        assert len(eval_issues) > 0
        assert eval_issues[0].severity == Severity.HIGH
    
    def test_find_missing_docstrings(self, temp_project):
        """Test detection of missing docstrings."""
        code_file = temp_project / 'src' / 'nodocs.py'
        code_file.write_text("""
def public_function():
    return True

class PublicClass:
    def public_method(self):
        pass
""")
        
        analyzer = StaticAnalyzer(temp_project)
        issues = analyzer.analyze()
        
        # Should find missing docstrings
        doc_issues = [i for i in issues if 'docstring' in i.message.lower()]
        assert len(doc_issues) >= 2  # Function and class
        assert all(i.severity == Severity.INFO for i in doc_issues)
    
    def test_ignore_private_functions(self, temp_project):
        """Test that private functions without docstrings are ignored."""
        code_file = temp_project / 'src' / 'private.py'
        code_file.write_text("""
def _private_function():
    return True

def __very_private():
    return False
""")
        
        analyzer = StaticAnalyzer(temp_project)
        issues = analyzer.analyze()
        
        # Should not complain about private functions
        doc_issues = [i for i in issues if 'docstring' in i.message.lower()]
        assert len(doc_issues) == 0
    
    def test_valid_code(self, temp_project):
        """Test that valid code produces no issues."""
        code_file = temp_project / 'src' / 'clean.py'
        code_file.write_text("""
\"\"\"A clean module.\"\"\"

def clean_function():
    \"\"\"A properly documented function.\"\"\"
    return True
""")
        
        analyzer = StaticAnalyzer(temp_project)
        issues = analyzer.analyze()
        
        # Should have no issues (or only INFO level)
        critical_issues = [i for i in issues if i.severity in (Severity.CRITICAL, Severity.HIGH)]
        assert len(critical_issues) == 0


class TestShellScriptLinter:
    """Test shell script linting functionality."""
    
    def test_missing_shebang(self, temp_project):
        """Test detection of missing shebang."""
        script = temp_project / 'scripts' / 'test.sh'
        script.write_text('echo "Hello World"\n')
        
        linter = ShellScriptLinter(temp_project)
        issues = linter.analyze()
        
        # Should find missing shebang
        shebang_issues = [i for i in issues if 'shebang' in i.message.lower()]
        assert len(shebang_issues) > 0
        assert shebang_issues[0].auto_fixable == True
    
    def test_unquoted_variable(self, temp_project):
        """Test detection of unquoted variables."""
        script = temp_project / 'scripts' / 'vars.sh'
        script.write_text("""#!/bin/bash
echo $MY_VAR
""")
        
        linter = ShellScriptLinter(temp_project)
        issues = linter.analyze()
        
        # Should find unquoted variable
        quote_issues = [i for i in issues if 'unquoted' in i.message.lower()]
        assert len(quote_issues) > 0
    
    def test_dangerous_command(self, temp_project):
        """Test detection of dangerous commands."""
        script = temp_project / 'scripts' / 'danger.sh'
        script.write_text("""#!/bin/bash
rm -rf /
""")
        
        linter = ShellScriptLinter(temp_project)
        issues = linter.analyze()
        
        # Should find dangerous command
        danger_issues = [i for i in issues if 'dangerous' in i.message.lower()]
        assert len(danger_issues) > 0
        assert danger_issues[0].severity == Severity.CRITICAL
    
    def test_valid_script(self, temp_project):
        """Test that valid scripts produce no critical issues."""
        script = temp_project / 'scripts' / 'good.sh'
        script.write_text("""#!/bin/bash
set -e

MY_VAR="test"
echo "$MY_VAR"
""")
        
        linter = ShellScriptLinter(temp_project)
        issues = linter.analyze()
        
        # Should have no critical issues
        critical_issues = [i for i in issues if i.severity == Severity.CRITICAL]
        assert len(critical_issues) == 0


class TestConfigValidator:
    """Test configuration validation functionality."""
    
    def test_missing_env_example(self, temp_project):
        """Test detection of missing .env.example."""
        validator = ConfigValidator(temp_project)
        issues = validator.analyze()
        
        # Should find missing .env.example
        env_issues = [i for i in issues if '.env.example' in i.file_path]
        assert len(env_issues) > 0
        assert env_issues[0].severity == Severity.HIGH
    
    def test_missing_mcp_json(self, temp_project):
        """Test detection of missing mcp.json."""
        validator = ConfigValidator(temp_project)
        issues = validator.analyze()
        
        # Should find missing mcp.json
        mcp_issues = [i for i in issues if 'mcp.json' in i.file_path]
        assert len(mcp_issues) > 0
    
    def test_invalid_json(self, temp_project):
        """Test detection of invalid JSON."""
        mcp_file = temp_project / 'mcp.json'
        mcp_file.write_text('{ invalid json }')
        
        validator = ConfigValidator(temp_project)
        issues = validator.analyze()
        
        # Should find invalid JSON
        json_issues = [i for i in issues if 'invalid json' in i.message.lower()]
        assert len(json_issues) > 0
        assert json_issues[0].severity == Severity.HIGH
    
    def test_missing_requirements(self, temp_project):
        """Test detection of missing requirements.txt."""
        validator = ConfigValidator(temp_project)
        issues = validator.analyze()
        
        # Should find missing requirements.txt
        req_issues = [i for i in issues if 'requirements.txt' in i.file_path]
        assert len(req_issues) > 0
    
    def test_unpinned_requirements(self, temp_project):
        """Test detection of unpinned package versions."""
        req_file = temp_project / 'requirements.txt'
        req_file.write_text('requests\nflask\n')
        
        validator = ConfigValidator(temp_project)
        issues = validator.analyze()
        
        # Should find unpinned packages
        pin_issues = [i for i in issues if 'not version-pinned' in i.message.lower()]
        assert len(pin_issues) == 2  # Both packages


class TestDependencyChecker:
    """Test dependency checking functionality."""
    
    def test_invalid_requirement_format(self, temp_project):
        """Test detection of invalid requirement format."""
        req_file = temp_project / 'requirements.txt'
        req_file.write_text('package name with spaces\n')
        
        checker = DependencyChecker(temp_project)
        issues = checker.analyze()
        
        # Should find invalid format
        format_issues = [i for i in issues if 'invalid requirement' in i.message.lower()]
        assert len(format_issues) > 0


class TestRuntimeHealthChecker:
    """Test runtime health checking functionality."""
    
    def test_non_executable_script(self, temp_project):
        """Test detection of non-executable scripts."""
        import sys
        if sys.platform == "win32":
            pytest.skip("Windows does not use POSIX executable bits in the same way")
        script = temp_project / 'test.sh'
        script.write_text('#!/bin/bash\necho "test"\n')
        # Don't make it executable
        
        checker = RuntimeHealthChecker(temp_project)
        issues = checker.analyze()
        
        # Should find non-executable script
        exec_issues = [i for i in issues if 'not executable' in i.message.lower()]
        assert len(exec_issues) > 0
        assert exec_issues[0].auto_fixable == True
    
    def test_missing_directory(self, temp_project):
        """Test detection of missing directories."""
        checker = RuntimeHealthChecker(temp_project)
        issues = checker.analyze()
        
        # Should find missing standard directories
        dir_issues = [i for i in issues if 'directory' in i.message.lower() and 'does not exist' in i.message.lower()]
        assert len(dir_issues) > 0


class TestDockerValidator:
    """Test Docker validation functionality."""
    
    def test_missing_dockerfile(self, temp_project):
        """Test detection of missing Dockerfile."""
        validator = DockerValidator(temp_project)
        issues = validator.analyze()
        
        # Should find missing Dockerfile
        docker_issues = [i for i in issues if 'dockerfile' in i.file_path.lower()]
        assert len(docker_issues) > 0
    
    def test_missing_from_statement(self, temp_project):
        """Test detection of missing FROM statement."""
        dockerfile = temp_project / 'Dockerfile'
        dockerfile.write_text('RUN echo "no FROM"\n')
        
        validator = DockerValidator(temp_project)
        issues = validator.analyze()
        
        # Should find missing FROM
        from_issues = [i for i in issues if 'from' in i.message.lower()]
        assert len(from_issues) > 0
    
    def test_root_user_warning(self, temp_project):
        """Test warning about running as root."""
        dockerfile = temp_project / 'Dockerfile'
        dockerfile.write_text('FROM python:3.10\nRUN pip install requests\n')
        
        validator = DockerValidator(temp_project)
        issues = validator.analyze()
        
        # Should warn about root user
        user_issues = [i for i in issues if 'root' in i.message.lower()]
        assert len(user_issues) > 0
    
    def test_missing_dockerignore(self, temp_project):
        """Test detection of missing .dockerignore."""
        validator = DockerValidator(temp_project)
        issues = validator.analyze()
        
        # Should find missing .dockerignore
        ignore_issues = [i for i in issues if '.dockerignore' in i.file_path]
        assert len(ignore_issues) > 0
        assert ignore_issues[0].auto_fixable == True


class TestAutoFixer:
    """Test auto-fix functionality."""
    
    def test_add_shebang(self, temp_project):
        """Test auto-fix for missing shebang."""
        script = temp_project / 'test.sh'
        script.write_text('echo "test"\n')
        
        issue = Issue(
            severity=Severity.MEDIUM,
            check_type=CheckType.SHELL,
            file_path='test.sh',
            line_number=1,
            message="Missing shebang",
            auto_fixable=True
        )
        
        fixer = AutoFixer(temp_project)
        fixed = fixer._fix_issue(issue)
        
        assert fixed == True
        assert script.read_text().startswith('#!/usr/bin/env bash')
    
    def test_make_executable(self, temp_project):
        """Test auto-fix for executable permissions."""
        script = temp_project / 'test.sh'
        script.write_text('#!/bin/bash\necho "test"\n')
        
        issue = Issue(
            severity=Severity.MEDIUM,
            check_type=CheckType.RUNTIME,
            file_path='test.sh',
            line_number=None,
            message="Script not executable",
            auto_fixable=True
        )
        
        fixer = AutoFixer(temp_project)
        fixed = fixer._fix_issue(issue)
        
        assert fixed == True
        assert os.access(script, os.X_OK)
    
    def test_create_directory(self, temp_project):
        """Test auto-fix for missing directories."""
        issue = Issue(
            severity=Severity.INFO,
            check_type=CheckType.RUNTIME,
            file_path='logs',
            line_number=None,
            message="Directory 'logs' does not exist",
            auto_fixable=True
        )
        
        fixer = AutoFixer(temp_project)
        fixed = fixer._fix_issue(issue)
        
        assert fixed == True
        assert (temp_project / 'logs').exists()
    
    def test_create_dockerignore(self, temp_project):
        """Test auto-fix for missing .dockerignore."""
        issue = Issue(
            severity=Severity.LOW,
            check_type=CheckType.DOCKER,
            file_path='.dockerignore',
            line_number=None,
            message=".dockerignore file is missing",
            auto_fixable=True
        )
        
        fixer = AutoFixer(temp_project)
        fixed = fixer._fix_issue(issue)
        
        assert fixed == True
        assert (temp_project / '.dockerignore').exists()


class TestDiagnosticReport:
    """Test diagnostic report functionality."""
    
    def test_add_issue(self):
        """Test adding issues to report."""
        report = DiagnosticReport()
        
        issue = Issue(
            severity=Severity.HIGH,
            check_type=CheckType.STATIC,
            file_path='test.py',
            line_number=10,
            message="Test issue"
        )
        
        report.add_issue(issue)
        
        assert len(report.issues) == 1
        assert report.issues[0] == issue
    
    def test_get_summary(self):
        """Test summary generation."""
        report = DiagnosticReport()
        
        # Add issues of different severities
        report.add_issue(Issue(Severity.CRITICAL, CheckType.STATIC, 'a.py', 1, "Critical"))
        report.add_issue(Issue(Severity.HIGH, CheckType.STATIC, 'b.py', 2, "High"))
        report.add_issue(Issue(Severity.MEDIUM, CheckType.STATIC, 'c.py', 3, "Medium"))
        report.add_issue(Issue(Severity.LOW, CheckType.STATIC, 'd.py', 4, "Low"))
        report.add_issue(Issue(Severity.INFO, CheckType.STATIC, 'e.py', 5, "Info"))
        
        summary = report.get_summary()
        
        assert summary['total'] == 5
        assert summary['critical'] == 1
        assert summary['high'] == 1
        assert summary['medium'] == 1
        assert summary['low'] == 1
        assert summary['info'] == 1
        assert summary['fixed'] == 0
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        report = DiagnosticReport()
        report.timestamp = "2024-01-01T00:00:00"
        report.duration = 1.5
        
        report.add_issue(Issue(Severity.HIGH, CheckType.STATIC, 'test.py', 10, "Test"))
        
        report_dict = report.to_dict()
        
        assert report_dict['timestamp'] == "2024-01-01T00:00:00"
        assert report_dict['duration'] == 1.5
        assert len(report_dict['issues']) == 1
        assert report_dict['summary']['total'] == 1


class TestReportGenerator:
    """Test report generation functionality."""
    
    def test_generate_json(self):
        """Test JSON report generation."""
        report = DiagnosticReport()
        report.timestamp = "2024-01-01T00:00:00"
        report.duration = 1.0
        
        report.add_issue(Issue(Severity.HIGH, CheckType.STATIC, 'test.py', 10, "Test issue"))
        
        json_report = ReportGenerator.generate_json(report)
        
        assert '"timestamp"' in json_report
        assert '"duration"' in json_report
        assert '"issues"' in json_report
        assert 'Test issue' in json_report
    
    def test_generate_markdown(self):
        """Test Markdown report generation."""
        report = DiagnosticReport()
        report.timestamp = "2024-01-01T00:00:00"
        report.duration = 1.0
        
        report.add_issue(Issue(Severity.HIGH, CheckType.STATIC, 'test.py', 10, "Test issue"))
        
        md_report = ReportGenerator.generate_markdown(report)
        
        assert '# Diagnostic Report' in md_report
        assert '## Summary' in md_report
        assert '## Issues' in md_report
        assert 'Test issue' in md_report
    
    def test_generate_terminal(self):
        """Test terminal report generation."""
        report = DiagnosticReport()
        report.timestamp = "2024-01-01T00:00:00"
        report.duration = 1.0
        
        report.add_issue(Issue(Severity.HIGH, CheckType.STATIC, 'test.py', 10, "Test issue"))
        
        terminal_report = ReportGenerator.generate_terminal(report, use_color=False)
        
        assert 'Diagnostic Report' in terminal_report
        assert 'Summary:' in terminal_report
        assert 'Test issue' in terminal_report


class TestAutoIssueFinder:
    """Test main AutoIssueFinder functionality."""
    
    def test_run_all_checks(self, temp_project):
        """Test running all checks."""
        # Create some test files
        (temp_project / 'src' / 'test.py').write_text('def foo():\n    pass\n')
        (temp_project / 'test.sh').write_text('echo test\n')
        
        finder = AutoIssueFinder(temp_project, verbose=False)
        report = finder.run(set(CheckType), auto_fix=False)
        
        assert isinstance(report, DiagnosticReport)
        assert report.timestamp != ""
        assert report.duration > 0
        assert len(report.issues) > 0
    
    def test_run_specific_checks(self, temp_project):
        """Test running specific checks only."""
        (temp_project / 'src' / 'test.py').write_text('def foo():\n    pass\n')
        
        finder = AutoIssueFinder(temp_project, verbose=False)
        report = finder.run({CheckType.STATIC}, auto_fix=False)
        
        # Should only have static analysis issues
        for issue in report.issues:
            assert issue.check_type == CheckType.STATIC
    
    def test_auto_fix_mode(self, temp_project):
        """Test auto-fix mode."""
        # Create fixable issue
        script = temp_project / 'test.sh'
        script.write_text('echo test\n')
        
        finder = AutoIssueFinder(temp_project, verbose=False)
        report = finder.run({CheckType.SHELL, CheckType.RUNTIME}, auto_fix=True)
        
        # Check if any issues were fixed
        fixed_issues = [i for i in report.issues if i.fixed]
        assert len(fixed_issues) > 0


def test_cli_help():
    """Test CLI help output."""
    import subprocess
    
    result = subprocess.run(
        [sys.executable, 'tools/auto_issue_finder.py', '--help'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert 'auto-fix' in result.stdout.lower()
    assert 'checks' in result.stdout.lower()


def test_cli_output_formats():
    """Test different output formats."""
    import subprocess
    
    for output_format in ['terminal', 'json', 'markdown']:
        result = subprocess.run(
            [sys.executable, 'tools/auto_issue_finder.py', '--output', output_format, '--project-root', '.'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should complete without errors
        assert result.returncode in (0, 1, 2, 3)  # Various exit codes based on findings


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
