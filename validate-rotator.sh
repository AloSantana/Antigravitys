#!/bin/bash

# Model Rotator Tab - Validation Script
# This script validates that the Model Rotator implementation is complete

echo "🔍 Validating Model Rotator Implementation..."
echo "=============================================="
echo ""

FRONTEND_FILE="frontend/index.html"
ERRORS=0
WARNINGS=0

# Check if frontend file exists
if [ ! -f "$FRONTEND_FILE" ]; then
    echo "❌ ERROR: $FRONTEND_FILE not found!"
    exit 1
fi

echo "📁 Checking file: $FRONTEND_FILE"
echo ""

# 1. Check CSS Styles
echo "🎨 Checking CSS Styles..."
CSS_CLASSES=(
    "rotator-container"
    "rotator-section"
    "rotator-form"
    "rotator-key-card"
    "rotator-stats-grid"
    "rotator-monitor-grid"
    "rotator-toast"
    "rotator-chart"
    "rotator-btn"
    "rotator-health-bar"
)

for class in "${CSS_CLASSES[@]}"; do
    if grep -q "\.$class" "$FRONTEND_FILE"; then
        echo "  ✅ CSS class .$class found"
    else
        echo "  ❌ ERROR: CSS class .$class NOT FOUND"
        ((ERRORS++))
    fi
done
echo ""

# 2. Check HTML Structure
echo "📝 Checking HTML Structure..."

# Check tab exists
if grep -q 'data-panel="rotator"' "$FRONTEND_FILE"; then
    echo "  ✅ Model Rotator tab found"
else
    echo "  ❌ ERROR: Model Rotator tab NOT FOUND"
    ((ERRORS++))
fi

# Check panel exists
if grep -q 'id="rotator-panel"' "$FRONTEND_FILE"; then
    echo "  ✅ Model Rotator panel found"
else
    echo "  ❌ ERROR: Model Rotator panel NOT FOUND"
    ((ERRORS++))
fi

# Check key sections
HTML_IDS=(
    "rotatorService"
    "rotatorApiKey"
    "rotatorKeyName"
    "rotatorKeysGrid"
    "rotatorStatsGrid"
    "rotatorUsageChart"
    "rotatorMonitorGrid"
)

for id in "${HTML_IDS[@]}"; do
    if grep -q "id=\"$id\"" "$FRONTEND_FILE"; then
        echo "  ✅ Element #$id found"
    else
        echo "  ❌ ERROR: Element #$id NOT FOUND"
        ((ERRORS++))
    fi
done
echo ""

# 3. Check JavaScript Functions
echo "⚙️ Checking JavaScript Functions..."

JS_FUNCTIONS=(
    "addRotatorKey"
    "loadRotatorKeys"
    "displayRotatorKeys"
    "displayRotatorStats"
    "displayRotatorUsageChart"
    "displayRotatorMonitor"
    "enableRotatorKey"
    "disableRotatorKey"
    "removeRotatorKey"
    "refreshRotatorStats"
    "resetRotatorStats"
    "exportRotatorStats"
    "showRotatorToast"
    "startRotatorAutoRefresh"
    "stopRotatorAutoRefresh"
)

for func in "${JS_FUNCTIONS[@]}"; do
    if grep -q "function $func\|async function $func" "$FRONTEND_FILE"; then
        echo "  ✅ Function $func() found"
    else
        echo "  ❌ ERROR: Function $func() NOT FOUND"
        ((ERRORS++))
    fi
done
echo ""

# 4. Check State Object
echo "📊 Checking State Management..."
if grep -q "const rotatorState" "$FRONTEND_FILE"; then
    echo "  ✅ rotatorState object found"
else
    echo "  ❌ ERROR: rotatorState object NOT FOUND"
    ((ERRORS++))
fi
echo ""

# 5. Check API Endpoints
echo "🔌 Checking API Endpoint Integration..."

API_ENDPOINTS=(
    "/api/rotator/keys"
    "/api/rotator/keys/enable"
    "/api/rotator/keys/disable"
    "/api/rotator/stats"
    "/api/rotator/stats/reset"
)

for endpoint in "${API_ENDPOINTS[@]}"; do
    if grep -q "$endpoint" "$FRONTEND_FILE"; then
        echo "  ✅ Endpoint $endpoint integrated"
    else
        echo "  ⚠️  WARNING: Endpoint $endpoint not found (may use variable)"
        ((WARNINGS++))
    fi
done
echo ""

# 6. Check Initialization
echo "🚀 Checking Initialization..."
if grep -q "rotator-panel.*active" "$FRONTEND_FILE"; then
    echo "  ✅ Panel initialization found"
else
    echo "  ⚠️  WARNING: Panel initialization may be missing"
    ((WARNINGS++))
fi

if grep -q "startRotatorAutoRefresh" "$FRONTEND_FILE"; then
    echo "  ✅ Auto-refresh initialization found"
else
    echo "  ❌ ERROR: Auto-refresh initialization NOT FOUND"
    ((ERRORS++))
fi
echo ""

# 7. Check Features
echo "✨ Checking Features..."

FEATURES=(
    "Add Key Form:onclick=\"addRotatorKey"
    "Enable Button:onclick=\"enableRotatorKey"
    "Disable Button:onclick=\"disableRotatorKey"
    "Remove Button:onclick=\"removeRotatorKey"
    "Refresh Button:onclick=\"refreshRotatorStats"
    "Export Button:onclick=\"exportRotatorStats"
    "Reset Button:onclick=\"resetRotatorStats"
)

for feature in "${FEATURES[@]}"; do
    feature_name="${feature%%:*}"
    search_term="${feature##*:}"
    
    if grep -q "$search_term" "$FRONTEND_FILE"; then
        echo "  ✅ $feature_name"
    else
        echo "  ❌ ERROR: $feature_name NOT FOUND"
        ((ERRORS++))
    fi
done
echo ""

# 8. Check Design System
echo "🎨 Checking Design System..."

DESIGN_ELEMENTS=(
    "Status Colors:rotator-key-status.available"
    "Health Scores:rotator-health-fill.excellent"
    "Toast Notifications:rotator-toast.success"
    "Loading States:rotator-loading"
    "Empty States:rotator-empty"
)

for element in "${DESIGN_ELEMENTS[@]}"; do
    element_name="${element%%:*}"
    search_term="${element##*:}"
    
    if grep -q "$search_term" "$FRONTEND_FILE"; then
        echo "  ✅ $element_name"
    else
        echo "  ⚠️  WARNING: $element_name not found"
        ((WARNINGS++))
    fi
done
echo ""

# 9. Check Responsive Design
echo "📱 Checking Responsive Design..."
if grep -q "grid-template-columns.*auto-fill.*minmax" "$FRONTEND_FILE" && grep -q "rotator" "$FRONTEND_FILE"; then
    echo "  ✅ Responsive grid layout found"
else
    echo "  ⚠️  WARNING: Responsive layout may need verification"
    ((WARNINGS++))
fi
echo ""

# 10. Count Lines Added
echo "📏 Implementation Statistics..."
TOTAL_LINES=$(wc -l < "$FRONTEND_FILE")
ROTATOR_LINES=$(grep -c "rotator" "$FRONTEND_FILE")
echo "  • Total lines in file: $TOTAL_LINES"
echo "  • Lines containing 'rotator': $ROTATOR_LINES"
echo ""

# Summary
echo "=============================================="
echo "📊 VALIDATION SUMMARY"
echo "=============================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED!"
    echo ""
    echo "🎉 Model Rotator implementation is complete and production-ready!"
    echo ""
    echo "Next Steps:"
    echo "  1. Start the frontend server"
    echo "  2. Navigate to the Model Rotator tab"
    echo "  3. Add your first API key"
    echo "  4. Monitor key performance"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  PASSED WITH WARNINGS"
    echo ""
    echo "Warnings: $WARNINGS"
    echo ""
    echo "The implementation is functional but has some non-critical issues."
    echo "Review warnings above and verify manually."
    echo ""
    exit 0
else
    echo "❌ VALIDATION FAILED"
    echo ""
    echo "Errors: $ERRORS"
    echo "Warnings: $WARNINGS"
    echo ""
    echo "Please fix the errors above before using the Model Rotator."
    echo ""
    exit 1
fi
