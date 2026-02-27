# Model Rotator Tab - Complete Feature Guide

## 🎯 Overview

The **Model Rotator** tab is a comprehensive API key management and monitoring system integrated into the Antigravity Workspace frontend. It provides real-time visibility into API key health, usage statistics, and intelligent key rotation across multiple AI services (Gemini, OpenAI, Vertex AI).

## ✨ What You Get

### 🔑 Complete Key Management
- Add/remove API keys with a simple form
- Enable/disable keys without deleting them
- View real-time health scores (color-coded)
- Monitor success rates and request counts
- Track key status with visual indicators

### 📊 Comprehensive Statistics
- Aggregate metrics across all keys
- Visual usage distribution charts
- Success rate tracking
- Token consumption monitoring
- Export statistics to JSON

### 🔍 Live Monitoring
- Auto-refresh every 5 seconds
- Real-time status updates
- Error counters per key
- Last used timestamps
- Smart polling (stops when tab inactive)

### 💫 Polished User Experience
- Toast notifications for all actions
- Confirmation dialogs for destructive operations
- Loading states for async operations
- Empty states when no data
- Smooth animations and transitions
- Fully responsive design
- Dark theme integration

## 🚀 Getting Started

### 1. Open the Tab
Navigate to your Antigravity Workspace and click the **🔄 Model Rotator** tab (located after the Tools tab).

### 2. Add Your First API Key

```
┌─────────────────────────────────────────────┐
│ Service:   [Gemini ▼]                       │
│ API Key:   [Enter your key...]             │
│ Name:      [My Production Key]  (optional) │
│                                             │
│ [➕ Add Key]                                │
└─────────────────────────────────────────────┘
```

1. Select the service (Gemini, OpenAI, or Vertex AI)
2. Paste your API key (will be masked)
3. Optionally give it a friendly name
4. Click "➕ Add Key"
5. See the success notification!

### 3. Monitor Your Keys

Your key will appear in a card showing:
- **Status**: 🟢 Available, 🟡 Rate Limited, or 🔴 Error/Disabled
- **Health Score**: Visual bar (green=excellent, yellow=good, orange=fair, red=poor)
- **Success Rate**: Percentage of successful requests
- **Request Count**: Total requests made with this key
- **Actions**: Enable/Disable and Remove buttons

### 4. View Statistics

The dashboard shows:
- **Total Requests**: Across all keys
- **Success Rate**: Overall percentage
- **Tokens Used**: Total consumption
- **Active Keys**: Number of enabled keys
- **Usage Chart**: Visual distribution per key

### 5. Export or Reset

- **🔄 Refresh**: Update all data immediately
- **💾 Export**: Download statistics as JSON
- **🗑️ Reset**: Clear all statistics (keeps keys)

## 📋 Features in Detail

### Key Card Example

```
┌─────────────────────────────┐
│ Production Key       🟢     │  ← Status indicator
│ Gemini                      │  ← Service type
├─────────────────────────────┤
│ Success Rate  │  Requests   │
│    95.2%      │     152     │  ← Metrics
├─────────────────────────────┤
│ ▓▓▓▓▓▓▓▓▓▓░░░               │  ← Health bar
│  (Excellent)                │
├─────────────────────────────┤
│ [⏸ Disable]  [🗑️ Remove]   │  ← Actions
└─────────────────────────────┘
```

### Health Score Breakdown

| Score | Color | Status | Meaning |
|-------|-------|--------|---------|
| 90-100% | 🟢 Green | Excellent | Peak performance |
| 70-89% | 🟡 Yellow | Good | Normal operation |
| 50-69% | 🟠 Orange | Fair | Degraded performance |
| 0-49% | 🔴 Red | Poor | Critical issues |

### Status Indicators

| Indicator | Meaning | Action |
|-----------|---------|--------|
| 🟢 Available | Key is healthy and ready | None needed |
| 🟡 Rate Limited | Key is backing off temporarily | Wait for recovery |
| 🔴 Error | Key has errors | Check error counter |
| 🔴 Disabled | Key manually disabled | Re-enable if needed |

## 🎨 User Interface

### Layout Structure

```
╔════════════════════════════════════════════════════╗
║  🔄 Model Rotator                                  ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║  🔑 API Key Management                             ║
║  ┌──────────────────────────────────────────────┐ ║
║  │ Add Key Form                                 │ ║
║  └──────────────────────────────────────────────┘ ║
║  ┌────────┐  ┌────────┐  ┌────────┐             ║
║  │ Key 1  │  │ Key 2  │  │ Key 3  │             ║
║  └────────┘  └────────┘  └────────┘             ║
║                                                    ║
║  📊 Statistics Dashboard                           ║
║  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                ║
║  │ 275 │ │91.2%│ │45.2K│ │  3  │                ║
║  └─────┘ └─────┘ └─────┘ └─────┘                ║
║  Usage Distribution Chart                         ║
║  [████████████] Key 1: 152                        ║
║  [████████] Key 2: 89                             ║
║  [████] Key 3: 34                                 ║
║                                                    ║
║  🔍 Live Monitoring    Auto-refresh every 5s      ║
║  ┌────────────┐ ┌────────────┐ ┌──────────────┐ ║
║  │ Status     │ │ Errors     │ │ Last Used    │ ║
║  └────────────┘ └────────────┘ └──────────────┘ ║
║                                                    ║
╚════════════════════════════════════════════════════╝
```

### Color Scheme

The Model Rotator uses the existing dark theme:
- **Background**: Dark slate (#0f172a, #1e293b, #334155)
- **Accent**: Blue (#3b82f6) and Purple (#8b5cf6) gradients
- **Success**: Green (#34d399)
- **Warning**: Yellow (#fbbf24)
- **Error**: Red (#f87171)
- **Text**: Light gray (#f8fafc, #94a3b8)

## 🔐 Security

### Key Protection
- API keys are **password-masked** in the input form
- Only **key hashes** are displayed, never full keys
- All **destructive actions** require confirmation
- **XSS protection** on all user inputs

### Confirmation Example

```
┌───────────────────────────────────────┐
│  Are you sure you want to remove     │
│  "Production Key"?                    │
│                                       │
│  This action cannot be undone.        │
│                                       │
│  [Cancel]            [Remove]         │
└───────────────────────────────────────┘
```

## ⚡ Performance

### Optimizations
- **Lazy Loading**: Data loads only when tab is active
- **Smart Polling**: Auto-refresh stops when tab is inactive
- **Efficient Updates**: Only changed data triggers re-renders
- **CSS Animations**: GPU-accelerated transforms
- **Debounced Actions**: Prevents rapid-fire API calls

### Auto-Refresh Behavior

```
Tab Active → Start polling (5s interval)
     ↓
Update all data every 5 seconds
     ↓
Tab Inactive → Stop polling (saves resources)
     ↓
Tab Active Again → Resume polling
```

## 📱 Responsive Design

The interface adapts to all screen sizes:

### Desktop (> 1200px)
- 3-column key grid
- Full-width statistics
- Side-by-side monitoring

### Tablet (768-1200px)
- 2-column key grid
- Stacked statistics
- Wrapped monitoring

### Mobile (< 768px)
- 1-column key grid
- Vertical statistics
- Full-width monitoring

## 🔌 API Integration

### Backend Endpoints

All endpoints are relative to `/api/rotator/`:

```javascript
// Add a new API key
POST /keys
Body: {
  service: "gemini" | "openai" | "vertex",
  api_key: "your-api-key",
  name: "My Key Name"  // optional
}

// Remove an API key
DELETE /keys
Body: {
  key_hash: "abc123..."
}

// Enable a disabled key
POST /keys/enable
Body: {
  key_hash: "abc123..."
}

// Disable an active key
POST /keys/disable
Body: {
  key_hash: "abc123..."
}

// Get all statistics
GET /stats
Response: {
  keys: [...],
  stats: {...}
}

// Reset all statistics
POST /stats/reset
```

## 🧪 Testing

### Validation Script

Run the automated validation:

```bash
chmod +x validate-rotator.sh
./validate-rotator.sh
```

Expected output:
```
✅ CSS Styles:        10/10 classes found
✅ HTML Structure:    8/8 elements found
✅ JavaScript:        15/15 functions found
✅ State Management:  1/1 objects found
✅ Features:          7/7 actions working

Result: ⚠️ PASSED WITH WARNINGS
(5 warnings about API_BASE - this is expected)
```

### Manual Testing Checklist

- [ ] Tab appears in navigation
- [ ] Add key form works
- [ ] Keys display correctly
- [ ] Enable/disable toggles work
- [ ] Remove requires confirmation
- [ ] Statistics update
- [ ] Charts render
- [ ] Monitoring auto-refreshes
- [ ] Export downloads JSON
- [ ] Toast notifications show
- [ ] Responsive on mobile
- [ ] Dark theme consistent

## 📚 Documentation

### Available Guides

| Document | Description | Use When |
|----------|-------------|----------|
| **MODEL_ROTATOR_COMPLETE.md** | Quick summary | Need overview |
| **MODEL_ROTATOR_IMPLEMENTATION.md** | Technical details | Development/debugging |
| **MODEL_ROTATOR_QUICK_REFERENCE.md** | Cheat sheet | Daily usage |
| **MODEL_ROTATOR_VISUAL_GUIDE.md** | UI examples | Learning interface |
| **README.md** (this file) | Complete guide | Getting started |

## 🐛 Troubleshooting

### Keys Not Loading?

1. Check backend is running
2. Verify `/api/rotator/stats` endpoint
3. Check browser console for errors
4. Try the refresh button

### Auto-Refresh Not Working?

1. Ensure tab is active (has blue highlight)
2. Check browser console
3. Verify 5-second interval hasn't been stopped
4. Switch to another tab and back

### Statistics Not Updating?

1. Click the 🔄 Refresh button
2. Wait for auto-refresh cycle
3. Check network tab for failed requests
4. Verify backend is responding

### Toast Notifications Not Showing?

1. Check for CSS conflicts
2. Verify z-index (should be 1000)
3. Look for JavaScript errors
4. Try a different browser

## 💡 Tips & Tricks

### Best Practices
1. **Name your keys**: Use descriptive names like "Production Gemini" or "Dev OpenAI"
2. **Monitor health**: Check health scores regularly to catch issues early
3. **Export regularly**: Keep backups of your statistics
4. **Use multiple keys**: Distribute load across different services
5. **Disable, don't delete**: Disable keys for testing instead of removing them

### Power User Features
- **Keyboard shortcuts**: Use Tab to navigate, Enter to submit
- **Quick refresh**: Click 🔄 to update immediately
- **Bulk export**: Download all stats as JSON for external analysis
- **Visual scanning**: Color-coded status makes monitoring fast

## 🎓 Learn More

### Architecture
The Model Rotator uses a three-layer architecture:
1. **CSS Layer**: Styling and animations
2. **HTML Layer**: Structure and layout
3. **JavaScript Layer**: Logic and API integration

### State Management
```javascript
const rotatorState = {
    keys: [],              // Array of key objects
    stats: {},             // Per-service statistics
    refreshInterval: null  // Auto-refresh timer
};
```

All state updates trigger UI re-renders for real-time updates.

## 🎉 Success!

You now have a fully functional Model Rotator tab! 

### Quick Start Recap
1. ✅ Open the 🔄 Model Rotator tab
2. ✅ Add your first API key
3. ✅ Monitor health and statistics
4. ✅ Export or reset as needed
5. ✅ Enjoy intelligent key rotation!

---

## 📞 Support

- **Quick Reference**: See `MODEL_ROTATOR_QUICK_REFERENCE.md`
- **Visual Guide**: See `MODEL_ROTATOR_VISUAL_GUIDE.md`
- **Technical Docs**: See `MODEL_ROTATOR_IMPLEMENTATION.md`
- **Validation**: Run `./validate-rotator.sh`

---

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: 2024  
**Maintained By**: Antigravity Workspace Team
