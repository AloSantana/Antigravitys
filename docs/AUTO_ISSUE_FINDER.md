# 🔍 Auto-Issue Finder - Complete Guide

**Smart diagnostic tool with automated fixing capabilities**

The Auto-Issue Finder is a comprehensive diagnostic tool that scans your codebase for issues across 8 categories and can automatically fix many common problems.

---

## ✨ Features

### 8 Check Categories

1. **Static Analysis** - Python AST-based code analysis
2. **Security Scanning** - Detect secrets, SQL injection, unsafe operations
3. **Shell Script Linting** - Syntax, quoting, dangerous commands
4. **Configuration Validation** - .env, JSON, YAML, Docker files
5. **Dependency Checking** - Format validation, version pinning
6. **Runtime Health** - Permissions, directories, services
7. **Docker Validation** - Dockerfile, .dockerignore, best practices
8. **Auto-Fix Mode** - Automatically fix common issues

### Output Formats

- **Terminal**: Colored, human-readable output
- **JSON**: Machine-readable for CI/CD integration
- **Markdown**: Formatted reports for documentation

---

## 🚀 Quick Start

### Basic Usage

```bash
# Run all checks
python tools/auto_issue_finder.py

# Run specific checks
python tools/auto_issue_finder.py --checks static,security

# Auto-fix issues
python tools/auto_issue_finder.py --auto-fix

# Generate markdown report
python tools/auto_issue_finder.py --output markdown --output-file report.md

# Verbose output
python tools/auto_issue_finder.py --verbose
```

### Example Output

```
🔍 Antigravity Auto-Issue Finder
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 DIAGNOSTIC REPORT

✓ Static Analysis: 15 issues found
  └─ backend/main.py:45: Missing docstring for function 'process_request'
  └─ backend/utils.py:23: Unused import 'sys'
  └─ backend/api.py:67: Bare except clause (catches all exceptions)

✓ Security Scan: 2 issues found
  └─ backend/config.py:12: Possible hardcoded secret 'password = "secret123"'
  └─ backend/db.py:89: Possible SQL injection vulnerability

✓ Configuration: 1 issue found
  └─ .dockerignore missing (auto-fixable)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 SUMMARY

Total Issues: 18
  Critical: 0
  High: 2
  Medium: 10
  Low: 6
  Info: 0

Auto-Fixable: 3 issues
Exit Code: 2 (issues found, non-critical)

Run with --auto-fix to fix issues automatically
```

---

## 📋 Check Categories

### 1. Static Analysis

**Python AST-based code analysis**

Checks for:
- Missing docstrings
- Unused imports
- Undefined variables
- Bare except clauses
- Too many arguments
- Complex functions (cyclomatic complexity)
- Magic numbers
- TODO comments

**Example:**
```bash
python tools/auto_issue_finder.py --checks static --verbose
```

### 2. Security Scanning

**Detect security vulnerabilities**

Checks for:
- Hardcoded secrets (API keys, passwords)
- SQL injection vulnerabilities
- Unsafe exec/eval usage
- Shell command injection
- Pickle usage (unsafe deserialization)
- Debug mode in production
- Weak cryptography

**Example:**
```bash
python tools/auto_issue_finder.py --checks security
```

### 3. Shell Script Linting

**Validate shell scripts**

Checks for:
- Missing shebang
- Unquoted variables
- Dangerous commands (rm -rf /)
- Missing error handling (set -e)
- Deprecated syntax
- ShellCheck integration

**Example:**
```bash
python tools/auto_issue_finder.py --checks shell
```

### 4. Configuration Validation

**Verify config files**

Checks:
- .env file syntax
- JSON validity (mcp.json, package.json)
- YAML syntax (docker-compose.yml)
- requirements.txt format
- Dockerfile syntax

**Example:**
```bash
python tools/auto_issue_finder.py --checks config
```

### 5. Dependency Checking

**Validate dependencies**

Checks:
- Package name format
- Version pinning
- Duplicates
- Known vulnerabilities (if database available)

**Example:**
```bash
python tools/auto_issue_finder.py --checks deps
```

### 6. Runtime Health

**Check runtime environment**

Checks:
- File permissions
- Directory existence
- Service availability
- Disk space
- Port availability

**Example:**
```bash
python tools/auto_issue_finder.py --checks runtime
```

### 7. Docker Validation

**Validate Docker configuration**

Checks:
- Dockerfile best practices
- .dockerignore presence
- Non-root user
- HEALTHCHECK instruction
- Layer optimization
- Security practices

**Example:**
```bash
python tools/auto_issue_finder.py --checks docker
```

---

## 🔧 Auto-Fix Mode

### Supported Fixes

The tool can automatically fix:

1. **Create .dockerignore** - Generate comprehensive .dockerignore
2. **Remove trailing whitespace** - Clean up Python files
3. **Fix shebang** - Add missing #!/bin/bash to shell scripts
4. **Format JSON** - Pretty-print JSON files

### Usage

```bash
# Dry run (show what would be fixed)
python tools/auto_issue_finder.py --auto-fix --verbose

# Actually fix issues
python tools/auto_issue_finder.py --auto-fix
```

### Safety

- Creates backups before modifying files
- Shows exactly what will be changed
- Can be run in dry-run mode
- Atomic operations (all or nothing)

---

## 📊 Output Formats

### Terminal (Default)

Colored, human-readable output for interactive use.

```bash
python tools/auto_issue_finder.py
```

**Features:**
- Color-coded severity levels
- Progress indicators
- Summary statistics
- Actionable suggestions

### JSON

Machine-readable output for automation.

```bash
python tools/auto_issue_finder.py --output json --output-file report.json
```

**Structure:**
```json
{
  "timestamp": "2024-02-07T14:30:00Z",
  "issues": [
    {
      "category": "static",
      "severity": "medium",
      "file": "backend/main.py",
      "line": 45,
      "message": "Missing docstring",
      "suggestion": "Add docstring to document function"
    }
  ],
  "summary": {
    "total": 18,
    "by_severity": {
      "critical": 0,
      "high": 2,
      "medium": 10,
      "low": 6,
      "info": 0
    }
  }
}
```

### Markdown

Formatted reports for documentation.

```bash
python tools/auto_issue_finder.py --output markdown --output-file report.md
```

**Output:**
```markdown
# Diagnostic Report

**Generated:** 2024-02-07 14:30:00

## Summary

- **Total Issues:** 18
- **Critical:** 0
- **High:** 2
- **Medium:** 10
- **Low:** 6

## Issues by Category

### Static Analysis (15 issues)

- `backend/main.py:45` - Missing docstring for function
- `backend/utils.py:23` - Unused import
...
```

---

## 🔌 CLI Reference

### Full Command Syntax

```bash
python tools/auto_issue_finder.py [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--checks CHECKS` | Comma-separated check types | all |
| `--auto-fix` | Enable automatic fixing | false |
| `--output FORMAT` | Output format (terminal/json/markdown) | terminal |
| `--output-file FILE` | Write to file | stdout |
| `--verbose` | Detailed output | false |
| `--no-color` | Disable colors | false |
| `--project-root PATH` | Project directory | current |
| `--help` | Show help message | - |

### Check Types

- `static` - Static code analysis
- `security` - Security scanning
- `shell` - Shell script linting
- `config` - Configuration validation
- `deps` - Dependency checking
- `runtime` - Runtime health checks
- `docker` - Docker validation
- `all` - All checks (default)

### Examples

```bash
# Security scan only
python tools/auto_issue_finder.py --checks security

# Multiple checks
python tools/auto_issue_finder.py --checks static,security,config

# JSON output to file
python tools/auto_issue_finder.py --output json --output-file report.json

# Verbose with auto-fix
python tools/auto_issue_finder.py --auto-fix --verbose

# Specific project directory
python tools/auto_issue_finder.py --project-root /path/to/project

# No color for CI/CD
python tools/auto_issue_finder.py --no-color
```

---

## 🔄 Integration Examples

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

python tools/auto_issue_finder.py --checks static,security --no-color
exit_code=$?

if [ $exit_code -eq 3 ]; then
  echo "Critical issues found! Commit blocked."
  exit 1
fi

exit 0
```

### GitHub Actions

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run Auto-Issue Finder
        run: |
          python tools/auto_issue_finder.py --output json --output-file report.json
          
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: diagnostic-report
          path: report.json
      
      - name: Check for Critical Issues
        run: |
          exit_code=$(python tools/auto_issue_finder.py --checks security)
          if [ $exit_code -eq 3 ]; then
            echo "Critical security issues found!"
            exit 1
          fi
```

### Cron Job

```bash
# Daily diagnostic scan
0 2 * * * cd /opt/antigravity && python tools/auto_issue_finder.py --auto-fix >> /var/log/auto-fix.log 2>&1
```

### GitLab CI

```yaml
# .gitlab-ci.yml
quality_check:
  stage: test
  script:
    - python tools/auto_issue_finder.py --output json --output-file report.json
  artifacts:
    paths:
      - report.json
    expire_in: 1 week
```

---

## 📈 Exit Codes

| Exit Code | Meaning | Action |
|-----------|---------|--------|
| 0 | No issues found | ✅ Continue |
| 1 | Info/Low issues only | ✅ Continue with warning |
| 2 | Medium/High issues | ⚠️ Review recommended |
| 3 | Critical issues | 🛑 Action required |

### Using Exit Codes in Scripts

```bash
python tools/auto_issue_finder.py
exit_code=$?

case $exit_code in
  0)
    echo "✅ All clear!"
    ;;
  1)
    echo "⚠️ Minor issues found"
    ;;
  2)
    echo "⚠️ Issues found, please review"
    ;;
  3)
    echo "🛑 Critical issues! Fix immediately"
    exit 1
    ;;
esac
```

---

## 🔍 Understanding Results

### Severity Levels

| Level | Color | Meaning | Action |
|-------|-------|---------|--------|
| CRITICAL | 🔴 Red | Security vulnerability, data loss risk | Fix immediately |
| HIGH | 🟠 Orange | Serious issue, potential failure | Fix soon |
| MEDIUM | 🟡 Yellow | Code quality, best practices | Fix when convenient |
| LOW | 🔵 Blue | Style, minor improvements | Optional fix |
| INFO | ⚪ White | Informational, no action needed | For awareness |

### Issue Format

```
[SEVERITY] Category: Message
  File: path/to/file.py
  Line: 42
  Suggestion: How to fix this issue
  Auto-fix: Available/Not available
```

### Common Issues

#### Missing Docstrings
```python
# ❌ Bad
def calculate_total(items):
    return sum(item['price'] for item in items)

# ✅ Good
def calculate_total(items):
    """Calculate total price of items.
    
    Args:
        items: List of item dicts with 'price' key
        
    Returns:
        Total price as float
    """
    return sum(item['price'] for item in items)
```

#### Bare Except
```python
# ❌ Bad
try:
    result = risky_operation()
except:
    pass

# ✅ Good
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
```

#### Hardcoded Secrets
```python
# ❌ Bad
API_KEY = "sk_live_1234567890abcdef"

# ✅ Good
import os
API_KEY = os.getenv("API_KEY")
```

---

## 🎓 Best Practices

### Regular Scanning

```bash
# Run before commits
git add .
python tools/auto_issue_finder.py --checks static,security
git commit -m "Your message"

# Run weekly comprehensive scan
python tools/auto_issue_finder.py --verbose --output markdown --output-file weekly-report.md

# Run before releases
python tools/auto_issue_finder.py --checks all --verbose
```

### Team Workflow

1. **Developer runs locally** before commit
2. **Pre-commit hook** catches issues
3. **CI/CD pipeline** runs on PR
4. **Scheduled scans** find accumulated issues
5. **Auto-fix** in maintenance windows

### Configuration

Create `.autoissue.json` for custom rules (future feature):

```json
{
  "ignore_files": ["tests/", "docs/"],
  "severity_overrides": {
    "missing_docstring": "low"
  },
  "custom_checks": []
}
```

---

## 🐛 Troubleshooting

### Tool Won't Run

```bash
# Check Python version
python --version  # Need 3.8+

# Install dependencies
pip install -r requirements.txt

# Check file exists
ls -la tools/auto_issue_finder.py

# Make executable
chmod +x tools/auto_issue_finder.py
```

### No Issues Found (But There Are Issues)

```bash
# Run with verbose
python tools/auto_issue_finder.py --verbose

# Check specific category
python tools/auto_issue_finder.py --checks security --verbose

# Verify project root
python tools/auto_issue_finder.py --project-root /correct/path
```

### Auto-Fix Not Working

```bash
# Check permissions
ls -la .dockerignore
chmod 644 .dockerignore

# Run with verbose
python tools/auto_issue_finder.py --auto-fix --verbose

# Check disk space
df -h
```

---

## 📚 Related Documentation

- **[Troubleshooting Guide](../TROUBLESHOOTING.md)**: General troubleshooting
- **[Phase 3 Report](../PHASE3_FINAL_REPORT.md)**: Implementation details
- **[Health Monitor](../PHASE3_COMPLETE.md)**: Health monitoring daemon

---

<div align="center">

**Keep your code clean and secure!**

Run diagnostics regularly: `python tools/auto_issue_finder.py`

[⬆ Back to Top](#-auto-issue-finder---complete-guide)

</div>
