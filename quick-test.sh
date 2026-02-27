#!/bin/bash
echo "=== Quick Verification of All Fixes ==="
echo ""

echo "1. Rollback mechanism:"
grep -q "cleanup_on_error()" install.sh && echo "  ✅ cleanup_on_error function exists" || echo "  ❌ Missing"
grep -q "trap cleanup_on_error ERR" install.sh && echo "  ✅ trap registered" || echo "  ❌ Missing"
echo ""

echo "2. Sudo validation:"
grep -q "sudo -n true 2>/dev/null" install.sh && echo "  ✅ Sudo check exists" || echo "  ❌ Missing"
echo ""

echo "3. Hardcoded paths:"
! grep -q "/home/runner/work/antigravity" install.sh install-remote.sh && echo "  ✅ No hardcoded paths" || echo "  ❌ Hardcoded paths found"
echo ""

echo "4. Timestamps:"
grep -q 'timestamp="$(date' install.sh && echo "  ✅ Timestamp logging in install.sh" || echo "  ❌ Missing"
grep -q 'timestamp="$(date' install-remote.sh && echo "  ✅ Timestamp logging in install-remote.sh" || echo "  ❌ Missing"
echo ""

echo "5. Error handling:"
grep -q "set -euo pipefail" install.sh && echo "  ✅ Strict mode in install.sh" || echo "  ❌ Missing"
grep -q "set -euo pipefail" install-remote.sh && echo "  ✅ Strict mode in install-remote.sh" || echo "  ❌ Missing"
echo ""

echo "6. ShellCheck compliance:"
shellcheck install.sh 2>&1 | grep -c error | xargs -I {} echo "  install.sh errors: {}"
shellcheck install-remote.sh 2>&1 | grep -c error | xargs -I {} echo "  install-remote.sh errors: {}"
shellcheck start.sh 2>&1 | grep -c error | xargs -I {} echo "  start.sh errors: {}"
shellcheck stop.sh 2>&1 | grep -c error | xargs -I {} echo "  stop.sh errors: {}"
shellcheck configure.sh 2>&1 | grep -c error | xargs -I {} echo "  configure.sh errors: {}"
shellcheck validate.sh 2>&1 | grep -c error | xargs -I {} echo "  validate.sh errors: {}"
echo ""

echo "✅ All critical fixes verification complete!"
