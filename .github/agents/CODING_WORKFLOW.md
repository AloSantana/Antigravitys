# Optimized Coding Workflow with Custom Agents & MCP Servers

This guide provides optimized development workflows leveraging custom agents and MCP servers for maximum productivity and code quality.

## Quick Reference: Development Scenarios

### 🚀 New Feature Development
```
Time: 30-60 minutes | Quality: Production-ready
Agents: repo-optimizer → testing-stability-expert → code-reviewer → docs-master
```

### 🐛 Bug Fix
```
Time: 15-30 minutes | Quality: Regression-proof
Agents: code-reviewer → testing-stability-expert
```

### ⚡ Performance Issue
```
Time: 20-40 minutes | Quality: Benchmarked improvement
Agents: performance-optimizer → testing-stability-expert
```

### 📚 Documentation Update
```
Time: 10-20 minutes | Quality: Verified accuracy
Agents: docs-master → code-reviewer
```

### 🔒 Security Audit
```
Time: 30-45 minutes | Quality: Production-secure
Agents: code-reviewer → testing-stability-expert → docs-master
```

## Swarm-Tools & Oh-My-OpenCode Integration Rules

### 🐝 Swarm-Tools: Global Database Rule (MANDATORY)
- **ALL swarm data must use the SINGLE global database** at `~/.config/swarm-tools/swarm.db`.
- **Local `swarm.db` files are BANNED** — never create them inside the project.
- **Use `HiveAdapter`** from `swarm-mail` programmatically for all swarm DB access:
  ```python
  from swarm_mail import HiveAdapter
  hive = HiveAdapter()  # automatically targets ~/.config/swarm-tools/swarm.db
  ```
- **NEVER use `bd` CLI commands** — they are deprecated.

### 🎣 Oh-My-OpenCode: Plugin Wrapper Rules
- **Self-contained wrappers**: Plugin wrappers must not depend on each other's state.
- **Do NOT import `opencode-swarm-plugin` directly** — the runtime loads it; direct imports cause double-init.
- **Sisyphus hook tiers** (46 total):
  | Tier | Hooks | Purpose |
  |------|-------|---------|
  | 0 | `on_session_start` | Load context, prime memory |
  | 1 | `on_message_in`, `on_message_out` | Transform/log messages |
  | 2 | `on_tool_call`, `on_tool_result` | Intercept tool calls |
  | 3 | `on_session_end` | Persist state, sync swarm DB |

### Swarm Workflow (OpenCode TUI)
```
/swarm "task"   → decompose + spawn parallel workers
/hive           → query and manage task cells
/inbox          → messages from other agents
/status         → swarm coordination status
/handoff        → end session with sync notes
```

### Python Swarm API (Backend)
Use `POST /api/swarm/execute` for swarm tasks from the backend API.
Use `src/swarm.py` SwarmOrchestrator directly in Python code.
**Do NOT** bypass these interfaces with direct DB writes.

## Workflow 1: Feature Development (Full Cycle)

### Stage 1: Planning & Structure (5-10 min)
```bash
@agent:repo-optimizer "Analyze codebase and plan structure for user profile editing feature. Include:
- Module organization
- Required dependencies
- Integration points with existing code"

# Agent uses: filesystem, github (search patterns), memory, python-analysis
# Output: Structural plan and recommendations
```

### Stage 2: Implementation Setup (5-10 min)
```bash
@agent:repo-optimizer "Create boilerplate for user profile feature:
- Create src/features/profile/ directory
- Add __init__.py, models.py, routes.py, service.py
- Setup basic imports and structure"

# Agent uses: filesystem, git
# Output: Scaffold code ready for implementation
```

### Stage 3: Development (Manual - 20-30 min)
```python
# Implement your feature logic
# - Write business logic
# - Create API endpoints
# - Add data models
```

### Stage 4: Testing (10-15 min)
```bash
@agent:testing-stability-expert "Create comprehensive tests for user profile feature in src/features/profile/:
- Unit tests for service layer
- Integration tests for API endpoints  
- Edge cases: invalid data, missing fields, permission checks
- Test data fixtures"

# Agent uses: filesystem, python-analysis, memory
# Output: tests/features/test_profile.py with full coverage
```

### Stage 5: Quality Review (5-10 min)
```bash
@agent:code-reviewer "Review src/features/profile/ for:
- Security vulnerabilities (SQL injection, XSS, auth bypass)
- Input validation
- Error handling
- Code quality and best practices"

# Agent uses: filesystem, python-analysis, github (search vulnerabilities)
# Output: Security report and recommendations
```

### Stage 6: Performance Check (5-10 min)
```bash
@agent:performance-optimizer "Analyze performance of profile endpoints:
- Profile database queries
- Check for N+1 problems
- Identify slow operations
- Recommend optimizations"

# Agent uses: filesystem, python-analysis, memory
# Output: Performance report and improvements
```

### Stage 7: Documentation (5-10 min)
```bash
@agent:docs-master "Document user profile feature:
- Add API endpoints to docs/api.md
- Create usage examples
- Update README.md with new feature
- Add screenshots if UI changes"

# Agent uses: filesystem, fetch (verify links), puppeteer (screenshots)
# Output: Complete documentation
```

### Total Time: ~60-90 minutes for production-ready feature

## Workflow 2: Rapid Bug Fix (Optimized)

### Step 1: Bug Analysis (5 min)
```bash
@agent:code-reviewer "Analyze bug #156: Users can't upload files > 10MB
- Review src/api/upload.py
- Check file size validation
- Review web server config
- Identify root cause"

# Agent uses: filesystem, git (history), github (similar issues)
# Output: Root cause analysis
```

### Step 2: Fix Implementation (Manual - 5-10 min)
```python
# Implement the fix based on analysis
# - Update file size limits
# - Fix validation logic
# - Update configuration
```

### Step 3: Regression Prevention (5 min)
```bash
@agent:testing-stability-expert "Add regression tests for bug #156:
- Test file upload with various sizes
- Test edge cases: exactly 10MB, 10MB+1byte, very large files
- Test error messages for oversized files"

# Agent uses: filesystem, memory (remember bug patterns)
# Output: Regression tests
```

### Step 4: Validation (3 min)
```bash
@agent:testing-stability-expert "Run all upload-related tests and verify fix"

# Agent uses: filesystem, python-analysis
# Output: Test results confirmation
```

### Total Time: ~20-30 minutes with regression prevention

## Workflow 3: Performance Optimization Sprint

### Phase 1: Profiling (10 min)
```bash
@agent:performance-optimizer "Profile the user dashboard endpoint:
- Identify slow operations
- Measure database query times
- Check memory usage
- Find bottlenecks"

# Agent uses: filesystem, python-analysis, memory
# Output: Performance profile with bottleneck identification
```

### Phase 2: Optimization Plan (5 min)
```bash
@agent:performance-optimizer "Create optimization plan for dashboard:
- Prioritize issues by impact
- Suggest specific optimizations
- Estimate improvement potential"

# Agent uses: sequential-thinking, memory, github (search patterns)
# Output: Prioritized optimization plan
```

### Phase 3: Implementation (Manual - 15-20 min)
```python
# Implement optimizations:
# - Add database indexes
# - Implement caching
# - Optimize queries
# - Use eager loading
```

### Phase 4: Validation (5 min)
```bash
@agent:testing-stability-expert "Verify optimizations don't break functionality:
- Run full test suite
- Check edge cases
- Validate data consistency"

# Agent uses: filesystem, python-analysis
# Output: Test validation results
```

### Phase 5: Benchmarking (5 min)
```bash
@agent:performance-optimizer "Benchmark improvements:
- Measure before/after performance
- Calculate speedup
- Document improvements"

# Agent uses: filesystem, memory
# Output: Performance improvement report
```

### Total Time: ~40-50 minutes with validated improvements

## Workflow 4: Documentation Sprint

### Phase 1: Documentation Audit (5 min)
```bash
@agent:docs-master "Audit all project documentation:
- Check README.md completeness
- Verify API documentation accuracy
- Find missing documentation
- Test all code examples"

# Agent uses: filesystem, fetch (links), python-analysis (examples)
# Output: Documentation gap analysis
```

### Phase 2: Content Creation (15-20 min)
```bash
@agent:docs-master "Create missing documentation:
- Document undocumented API endpoints
- Add usage examples for each feature
- Create troubleshooting guide
- Update installation instructions"

# Agent uses: filesystem, github (examples), puppeteer (screenshots)
# Output: Comprehensive documentation
```

### Phase 3: Verification (5 min)
```bash
@agent:docs-master "Verify all documentation:
- Test all code examples
- Verify all links work
- Check screenshots are current
- Ensure accuracy with codebase"

# Agent uses: filesystem, fetch, python-analysis
# Output: Verification report
```

### Total Time: ~25-30 minutes for complete documentation

## Workflow 5: Security Hardening

### Phase 1: Security Audit (15 min)
```bash
@agent:code-reviewer "Comprehensive security audit:
- Check for OWASP Top 10 vulnerabilities
- Review authentication/authorization
- Check input validation
- Review dependencies for CVEs
- Check for secrets in code"

# Agent uses: filesystem, github (search CVEs), python-analysis
# Output: Security vulnerability report
```

### Phase 2: Fix Critical Issues (Manual - 20-30 min)
```python
# Fix identified security issues:
# - Add input validation
# - Fix SQL injection risks
# - Update vulnerable dependencies
# - Add authentication checks
```

### Phase 3: Security Testing (10 min)
```bash
@agent:testing-stability-expert "Create security-focused tests:
- Test input validation with malicious payloads
- Test authentication/authorization edge cases
- Test SQL injection prevention
- Test XSS prevention"

# Agent uses: filesystem, memory (attack patterns)
# Output: Security test suite
```

### Phase 4: Documentation (5 min)
```bash
@agent:docs-master "Document security features and best practices:
- Add security section to README
- Document authentication flow
- Create security guidelines for contributors"

# Agent uses: filesystem
# Output: Security documentation
```

### Total Time: ~50-60 minutes for hardened security

## Advanced Patterns

### Pattern A: Continuous Integration Workflow
```yaml
# .github/workflows/ai-quality-check.yml
# Automated quality checks using agents

on: [pull_request]

jobs:
  ai-quality-check:
    steps:
      - name: Security Review
        run: @agent:code-reviewer "Security review of changed files"
      
      - name: Test Coverage
        run: @agent:testing-stability-expert "Verify test coverage"
      
      - name: Performance Check
        run: @agent:performance-optimizer "Check for performance regressions"
      
      - name: Docs Update
        run: @agent:docs-master "Verify docs reflect changes"
```

### Pattern B: Daily Health Check
```bash
#!/bin/bash
# daily-health-check.sh

echo "Running daily repository health check..."

@agent:repo-optimizer "Check for outdated dependencies and config issues"
@agent:testing-stability-expert "Run full test suite and report coverage"
@agent:code-reviewer "Scan for new security vulnerabilities"
@agent:performance-optimizer "Profile critical paths for regressions"
@agent:docs-master "Verify documentation is up to date"

echo "Health check complete. Review reports above."
```

### Pattern C: Pre-Release Checklist
```bash
# pre-release.sh
echo "Pre-release validation starting..."

# 1. Code Quality
@agent:code-reviewer "Final security and quality audit before v1.0 release"

# 2. Testing
@agent:testing-stability-expert "Run full test suite including edge cases and load tests"

# 3. Performance
@agent:performance-optimizer "Benchmark critical operations and ensure SLA compliance"

# 4. Documentation
@agent:docs-master "Verify all v1.0 features are documented with working examples"

# 5. Repository
@agent:repo-optimizer "Verify all tooling and dependencies are production-ready"

echo "Release validation complete!"
```

## MCP Server Optimization Tips

### Tip 1: Enable Only What You Need
```json
// Disable unused MCP servers for faster startup
{
  "postgres": { "enabled": false },  // If not using PostgreSQL
  "kubernetes": { "enabled": false }, // If not using K8s
  "brave-search": { "enabled": false } // If not needing web search
}
```

### Tip 2: Set Environment Variables Early
```bash
# Add to .bashrc or .zshrc for persistent config
export GITHUB_TOKEN="your_token"
export COPILOT_MCP_GITHUB_TOKEN="your_token"

# For project-specific configs
source .env
```

### Tip 3: Use Local MCP Server Caching
```bash
# Cache npm packages globally for faster MCP startup
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @github/mcp-server
```

## Measuring Success

### Code Quality Metrics
- **Security**: Zero critical vulnerabilities
- **Testing**: ≥80% code coverage
- **Performance**: All endpoints < 500ms response time
- **Documentation**: 100% feature coverage

### Workflow Efficiency Metrics
- **Feature Development**: 50% faster with agents
- **Bug Fixes**: 60% faster with regression prevention
- **Code Review**: 40% more issues caught
- **Documentation**: 70% less time to maintain

### Expected Time Savings
| Task | Manual | With Agents | Savings |
|------|--------|-------------|---------|
| Feature Development | 120 min | 60-90 min | 30-50% |
| Bug Fix | 45 min | 20-30 min | 33-56% |
| Code Review | 30 min | 10-15 min | 50-67% |
| Documentation | 60 min | 25-30 min | 50-58% |
| Security Audit | 90 min | 50-60 min | 33-44% |

## Best Practices Summary

1. **Start with Planning**: Use repo-optimizer to analyze and plan
2. **Test Early**: Don't wait until the end to add tests
3. **Review Security**: Always run security review before merge
4. **Document as You Go**: Update docs alongside code
5. **Measure Performance**: Profile before and after changes
6. **Iterate**: Refine agent requests based on results
7. **Validate**: Always review agent output
8. **Leverage MCP**: Let agents use MCP servers automatically

## Troubleshooting

### Agent Response Seems Generic
**Fix**: Be more specific in your request
```
❌ "@agent:code-reviewer review this"
✅ "@agent:code-reviewer Review src/auth.py for SQL injection and weak password validation"
```

### MCP Server Not Available
**Fix**: Check configuration and environment
```bash
# Verify MCP config
cat .github/copilot/mcp.json

# Check environment variables
echo $GITHUB_TOKEN

# Test MCP server manually
npx @modelcontextprotocol/server-filesystem .
```

### Agents Making Conflicting Changes
**Fix**: Use sequential workflow with clear handoffs
```bash
# Sequential with context
@agent:repo-optimizer "Setup API structure"
# Wait for completion, then:
@agent:testing-stability-expert "Test the API structure created by previous agent"
```

## Next Steps

1. **Try a Simple Workflow**: Start with bug fix workflow
2. **Experiment with Agents**: Test each agent individually
3. **Create Custom Workflows**: Adapt patterns to your needs
4. **Monitor Results**: Track time savings and quality improvements
5. **Refine Prompts**: Learn what works best for your project
6. **Share Learnings**: Document your own workflow patterns

---

**Remember**: The goal is not just faster development, but **higher quality code** with **less effort**. Use agents to handle repetitive tasks while you focus on creative problem-solving.

**Pro Tip**: Create project-specific workflows in your README or CONTRIBUTING guide so all team members can benefit from optimized agent usage.
