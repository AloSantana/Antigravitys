# Model Rotator - Quick Reference

## 🎯 Quick Access

**Location**: Frontend → **🔄 Model Rotator** tab (after Tools tab)

## ⚡ Quick Actions

### Add API Key
```
1. Select service (Gemini/OpenAI/Vertex)
2. Enter API key
3. Optional: Enter friendly name
4. Click "➕ Add Key"
```

### Manage Keys
```
🟢 Green Dot = Available
🟡 Yellow Dot = Rate Limited  
🔴 Red Dot = Error/Disabled

Actions per key:
  ⏸ Disable - Temporarily disable
  ✓ Enable - Re-enable disabled key
  🗑️ Remove - Delete permanently (confirms)
```

### View Statistics
```
Dashboard shows:
  • Total Requests (all keys)
  • Success Rate (%)
  • Tokens Used
  • Active Keys count

Chart shows:
  • Visual usage distribution per key
```

### Monitor Keys
```
Live panel updates every 5 seconds:
  • Current status
  • Error counts
  • Last used time
```

## 🎨 Status Colors

| Color | Meaning | Health Score |
|-------|---------|--------------|
| 🟢 Green | Excellent | 90-100% |
| 🟡 Yellow | Good | 70-89% |
| 🟠 Orange | Fair | 50-69% |
| 🔴 Red | Poor | 0-49% |

## 🔌 API Endpoints

```javascript
// All endpoints relative to: /api/rotator/

POST   /keys              // Add new key
DELETE /keys              // Remove key
POST   /keys/enable       // Enable key
POST   /keys/disable      // Disable key
GET    /stats             // Get all stats
POST   /stats/reset       // Reset statistics
```

## 📊 Dashboard Actions

| Button | Action |
|--------|--------|
| 🔄 Refresh | Update all data |
| 💾 Export | Download JSON |
| 🗑️ Reset Stats | Clear counters |

## 🔔 Notifications

All actions show toast notifications:
- ✅ Success (green border)
- ❌ Error (red border)
- ⚠️ Warning (yellow border)

Auto-dismisses after 3 seconds

## 🚀 Power User Tips

### Keyboard Shortcuts
- `Tab` - Navigate form fields
- `Enter` - Submit add key form
- `Esc` - Close confirmation dialogs

### Auto-Refresh
- Starts when tab opens
- Stops when tab closes
- 5-second interval
- Only updates if visible

### Bulk Export
```javascript
// Data includes:
{
  "timestamp": "ISO date",
  "keys": [...],
  "stats": {...}
}
```

### Security
- Keys are password-masked in form
- Keys stored by hash (not full key)
- All destructive actions require confirmation
- XSS protection on all inputs

## 📱 Responsive Design

| Screen Size | Layout |
|-------------|--------|
| Desktop | 3-column key grid |
| Tablet | 2-column key grid |
| Mobile | 1-column key grid |

## ⚙️ Configuration

No configuration needed! Works out-of-box with:
- Default 5s refresh interval
- Automatic polling control
- Smart loading states
- Progressive enhancement

## 🐛 Common Issues

### Keys Not Loading?
1. Check backend is running
2. Verify API endpoint: `/api/rotator/stats`
3. Check browser console
4. Refresh with 🔄 button

### Stats Not Updating?
1. Click 🔄 Refresh button
2. Check auto-refresh is active
3. Switch to another tab and back

### Toast Not Showing?
1. Check browser console
2. Ensure no CSS conflicts
3. Verify z-index (1000)

## 📋 Checklist - First Time Setup

- [ ] Navigate to Model Rotator tab
- [ ] Add at least one API key
- [ ] Verify key card appears
- [ ] Check status indicator (green)
- [ ] View statistics dashboard
- [ ] Test enable/disable
- [ ] Monitor live updates
- [ ] Export statistics
- [ ] Test remove key

## 🔗 Related Documentation

- **Full Implementation**: `MODEL_ROTATOR_IMPLEMENTATION.md`
- **API Documentation**: Backend API docs
- **Frontend Code**: `frontend/index.html`

## 💡 Pro Tips

1. **Name Your Keys**: Use descriptive names for easy identification
2. **Monitor Health**: Watch health scores to catch issues early
3. **Export Regularly**: Keep backups of statistics
4. **Use Multiple Keys**: Distribute load across services
5. **Disable, Don't Delete**: Disable instead of removing for testing

## 📞 Support

If you encounter issues:
1. Check browser console for errors
2. Verify API endpoints are accessible
3. Review `MODEL_ROTATOR_IMPLEMENTATION.md`
4. Check backend logs

---

**Quick Start**: Select Model Rotator tab → Add API key → Done! 🎉
