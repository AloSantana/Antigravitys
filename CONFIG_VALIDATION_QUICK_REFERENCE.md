# Configuration Validation & CI/CD - Quick Reference

## 🚀 Quick Start

### Run Configuration Tests
```bash
# All configuration tests
pytest tests/config/ -v

# Specific category
pytest tests/config/test_configuration_validation.py -v
pytest tests/config/test_setup_scripts.py -v
```

### Validate Configuration Manually
```bash
# YAML files
python -c "import yaml; yaml.safe_load(open('docker-compose.yml'))"
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"

# JSON files
python -m json.tool .github/copilot/mcp.json

# Shell scripts
bash -n install.sh
bash -n configure.sh
bash -n start.sh
```

## 📊 Test Statistics

- **Total Tests**: 72
- **Configuration Validation**: 36 tests
- **Setup Script Validation**: 36 tests
- **Execution Time**: ~0.8 seconds
- **Pass Rate**: 100%

## 🔍 What Gets Tested

### Configuration Files
- ✅ `.env.example` - Environment variables
- ✅ `.github/copilot/mcp.json` - MCP server config
- ✅ `docker-compose.yml` - Docker services
- ✅ `Dockerfile` - Container build
- ✅ `requirements.txt` - Python dependencies
- ✅ `.gitignore` - Git exclusions
- ✅ `pytest.ini` - Test configuration
- ✅ `.github/workflows/*.yml` - CI/CD workflows

### Setup Scripts
- ✅ `install.sh` - Installation script
- ✅ `configure.sh` - Configuration script
- ✅ `start.sh` - Service start script
- ✅ `stop.sh` - Service stop script
- ✅ `validate.sh` - Validation script

## 🎯 CI/CD Workflows

### Main CI Pipeline (`.github/workflows/ci.yml`)
```
Triggers: Push/PR to main/develop
Duration: ~8-12 minutes
Python Versions: 3.8, 3.9, 3.10, 3.11, 3.12

Jobs:
1. validate-config  - Config validation
2. lint            - Code quality (flake8, black, isort, pylint)
3. type-check      - Type checking (mypy)
4. security        - Security scan (bandit, safety, pip-audit)
5. test            - Test suite (all Python versions)
6. coverage-report - Coverage reporting (PR comments)
7. test-summary    - Test aggregation
8. ci-status       - Final status
```

### Security Scanning (`.github/workflows/security.yml`)
```
Triggers: Daily at 2 AM UTC, Push, Manual
Duration: ~15-20 minutes

Jobs:
1. dependency-scan - Safety, pip-audit
2. code-security   - Bandit SAST
3. secret-scan     - detect-secrets
4. container-scan  - Trivy
5. codeql          - GitHub CodeQL
6. semgrep         - Semgrep SAST
7. security-summary - Report aggregation
```

## 🐛 Common Issues & Solutions

### Issue: Tests fail in CI but pass locally
**Solution**: Check Python version compatibility
```bash
# Test with specific Python version
python3.10 -m pytest tests/config/ -v
```

### Issue: Coverage below threshold
**Solution**: Add tests or adjust threshold
```bash
# Check coverage
pytest --cov=src --cov=backend --cov-report=term-missing

# Adjust in .github/workflows/ci.yml
env:
  COVERAGE_THRESHOLD: 70  # Lower if needed
```

### Issue: Workflow YAML syntax error
**Solution**: Validate YAML before committing
```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
```

### Issue: Configuration test failures
**Solution**: Check what's expected
```bash
# Run with verbose output
pytest tests/config/ -v -s

# Run specific failing test
pytest tests/config/test_configuration_validation.py::TestClass::test_name -v
```

## 📈 Coverage Requirements

- **Minimum Coverage**: 70%
- **Recommended**: 80%+
- **Current**: Varies by module

Check coverage:
```bash
pytest --cov=src --cov=backend --cov-report=term-missing
```

## 🔐 Security Scanning

### Run Security Scans Locally
```bash
# Install tools
pip install bandit safety pip-audit

# Run scans
bandit -r . -x ./venv,./.venv
safety check
pip-audit
```

### View Security Results
1. Go to repository **Security** tab
2. Check **Code scanning alerts**
3. Review **Dependabot alerts**
4. Download scan artifacts from Actions

## 📝 Adding New Tests

### Configuration Test Template
```python
# tests/config/test_new_config.py
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).parent.parent.parent

class TestNewConfiguration:
    """Test new configuration aspect."""
    
    def test_config_exists(self):
        """Test that config file exists."""
        config_file = REPO_ROOT / "config.yml"
        assert config_file.exists(), "config.yml must exist"
    
    def test_config_valid(self):
        """Test that config is valid."""
        # Add validation logic
        pass
```

## 🎨 Customization

### Change Coverage Threshold
Edit `.github/workflows/ci.yml`:
```yaml
env:
  COVERAGE_THRESHOLD: 80  # Change from 70
```

### Add Python Version
Edit `.github/workflows/ci.yml`:
```yaml
matrix:
  python-version: ['3.8', '3.9', '3.10', '3.11', '3.12', '3.13']
```

### Skip Slow Tests
```python
@pytest.mark.slow
def test_slow_operation():
    pass

# Run without slow tests
pytest -m "not slow"
```

## 📚 Documentation

- **Full Guide**: `tests/README.md`
- **Test Summary**: `PHASE_2_TASK_2.2_COMPLETE.md`
- **CI/CD Docs**: See workflow files for inline comments

## 🎯 Quick Checks

Before committing:
```bash
# 1. Run config tests
pytest tests/config/ -v

# 2. Check YAML syntax
python -c "import yaml; yaml.safe_load(open('docker-compose.yml'))"

# 3. Check shell scripts
bash -n install.sh

# 4. Run linters
black --check .
flake8 .
```

## 🌟 Best Practices

1. ✅ Keep tests independent
2. ✅ Use descriptive test names
3. ✅ Write clear assertions
4. ✅ Add docstrings to tests
5. ✅ Mock external dependencies
6. ✅ Keep tests fast (<1s each)
7. ✅ Maintain >70% coverage
8. ✅ Update tests when config changes

## 📞 Getting Help

If tests fail:
1. Read the error message carefully
2. Check test documentation in `tests/README.md`
3. Run test locally with `-v -s` flags
4. Check workflow logs in GitHub Actions
5. Review recent configuration changes

## ✅ Success Checklist

- [ ] All 72 configuration tests pass
- [ ] CI workflow validated as correct YAML
- [ ] Security workflow validated as correct YAML
- [ ] Documentation updated
- [ ] Local testing works
- [ ] Coverage meets threshold

---

**Status**: ✅ All systems operational  
**Last Updated**: February 6, 2025  
**Maintainer**: Testing & Stability Expert Agent
