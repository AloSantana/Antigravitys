# Phase 3 Quick Reference Guide

## 🚀 Quick Commands

### Auto-Issue Finder

```bash
# Full scan
python tools/auto_issue_finder.py

# Quick security check
python tools/auto_issue_finder.py --checks static

# Auto-fix issues
python tools/auto_issue_finder.py --auto-fix

# CI/CD friendly
python tools/auto_issue_finder.py --no-color --output json
```

### Health Monitor

```bash
# Start monitoring
python tools/health_monitor.py --daemon --verbose

# Check status
python tools/health_monitor.py --status

# Stop
python tools/health_monitor.py --stop
```

## 📊 Check Types

| Check Type | Description | Auto-Fixable |
|-----------|-------------|--------------|
| `static` | Python code analysis | ❌ |
| `shell` | Shell script linting | ✅ (shebangs) |
| `config` | Configuration validation | ✅ (some) |
| `dependency` | Package checking | ❌ |
| `runtime` | Runtime health | ✅ (permissions) |
| `docker` | Docker validation | ✅ (.dockerignore) |

## 🎯 Severity Levels

| Level | Exit Code | Description |
|-------|-----------|-------------|
| CRITICAL | 3 | Must fix immediately |
| HIGH | 2 | Important issues |
| MEDIUM | 1 | Should address |
| LOW | 1 | Minor improvements |
| INFO | 0 | Suggestions |

## 🔧 Common Auto-Fixes

- ✅ Add missing shebangs to shell scripts
- ✅ Fix file permissions (make scripts executable)
- ✅ Create missing directories (logs, data, uploads)
- ✅ Generate .dockerignore file

## 📈 Health Monitor Metrics

### System Metrics
- CPU usage percentage
- Memory usage percentage  
- Disk usage percentage
- Available resources

### Service Status
- `up` - Service responding normally
- `degraded` - Service responding with errors
- `down` - Service not responding

### Default Thresholds
- CPU: 80%
- Memory: 85%
- Disk: 90%

## 🚨 Common Issues & Fixes

### Auto-Issue Finder

**Too many issues?**
```bash
# Run specific checks
python tools/auto_issue_finder.py --checks static,config

# Focus on critical/high only
python tools/auto_issue_finder.py | grep -E "CRITICAL|HIGH"
```

**Need JSON for tools?**
```bash
python tools/auto_issue_finder.py --output json > report.json
```

### Health Monitor

**Not starting?**
```bash
# Check if already running
python tools/health_monitor.py --status

# Clean up
rm logs/health_monitor.pid
python tools/health_monitor.py --daemon
```

**Too many alerts?**
```bash
# Increase check interval
python tools/health_monitor.py --daemon --check-interval 120
```

## 📁 Output Files

### Auto-Issue Finder
- Terminal output (default)
- JSON reports (--output json)
- Markdown reports (--output markdown)

### Health Monitor
- `logs/health_monitor.log` - Main log file
- `logs/health_monitor.pid` - Process ID
- `logs/health_metrics.json` - Metrics history

## 🔄 Integration Examples

### Pre-commit Hook
```bash
#!/bin/bash
python tools/auto_issue_finder.py --checks static --no-color
exit $?
```

### GitHub Actions
```yaml
- name: Code Quality Check
  run: python tools/auto_issue_finder.py --output json
```

### Cron Job
```bash
# Daily scan at 2 AM
0 2 * * * cd /opt/app && python tools/auto_issue_finder.py --auto-fix
```

## 💡 Pro Tips

1. **Use --verbose** to see progress
2. **Run --auto-fix** in safe environments first
3. **Check exit codes** in CI/CD pipelines
4. **Monitor logs** for health monitor issues
5. **Customize thresholds** for your workload
6. **Export metrics** for dashboards

## 📚 Help Commands

```bash
# Auto-Issue Finder help
python tools/auto_issue_finder.py --help

# Health Monitor help
python tools/health_monitor.py --help
```

## 🎯 Exit Codes Reference

| Code | Meaning |
|------|---------|
| 0 | No issues or all good |
| 1 | Warnings found |
| 2 | Errors found |
| 3 | Critical issues |

## ⚡ Performance Tips

### Auto-Issue Finder
- Use specific checks instead of 'all'
- Run in parallel for large projects
- Cache results for unchanged files

### Health Monitor
- Adjust check intervals based on load
- Use --no-color in production
- Rotate logs regularly

## 🔍 Debugging

### Enable Verbose Mode
```bash
# Auto-Issue Finder
python tools/auto_issue_finder.py --verbose

# Health Monitor
python tools/health_monitor.py --daemon --verbose
```

### Check Logs
```bash
# Health monitor logs
tail -f logs/health_monitor.log

# View metrics
cat logs/health_metrics.json | jq .
```

## 📞 Support

For issues or questions:
1. Check logs first
2. Run with --verbose
3. Review this guide
4. Check main documentation

---

**Quick Start:**
```bash
# 1. Run diagnostics
python tools/auto_issue_finder.py --verbose

# 2. Fix auto-fixable issues
python tools/auto_issue_finder.py --auto-fix

# 3. Start health monitoring
python tools/health_monitor.py --daemon --verbose

# 4. Check everything is working
python tools/health_monitor.py --status
```

**You're all set! 🎉**
