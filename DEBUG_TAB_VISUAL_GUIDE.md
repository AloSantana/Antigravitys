# 🐛 Debug Tab - Visual Guide

## Before & After

### BEFORE (Original Tabs)
```
┌─────────────────────────────┐
│ Sidebar                     │
├─────────────────────────────┤
│ 💬 Chat                     │
│ 📝 Editor                   │
│ ⚡ Terminal                 │
│ 📊 Performance              │
│ ⚙️ Settings                 │
└─────────────────────────────┘
```

### AFTER (With Debug Tab)
```
┌─────────────────────────────┐
│ Sidebar                     │
├─────────────────────────────┤
│ 💬 Chat                     │
│ 📝 Editor                   │
│ ⚡ Terminal                 │
│ 📊 Performance              │
│ ⚙️ Settings                 │
│ 🐛 Debug          ← NEW!    │
└─────────────────────────────┘
```

---

## Debug Panel Layout

```
╔═══════════════════════════════════════════════════════════╗
║  🐛 Debug Panel                                           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ 📜 Real-time Log Stream          [✓] Auto-scroll    │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │ Filters:  [Severity ▼]  [Model ▼]  [🔄 Refresh]    │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │ ┌───────────────────────────────────────────────┐   │ ║
║  │ │ 10:30:45  INFO   Request processed            │   │ ║
║  │ │           {"model":"gemini","duration":123}   │   │ ║
║  │ │                                                │   │ ║
║  │ │ 10:30:46  WARN   Slow response detected       │   │ ║
║  │ │           {"model":"vertex","duration":2340}  │   │ ║
║  │ │                                                │   │ ║
║  │ │ 10:30:47  ERROR  Connection timeout           │   │ ║
║  │ │           {"model":"ollama","error":"..."}    │   │ ║
║  │ │                                                │   │ ║
║  │ │ ... (scrollable)                              │   │ ║
║  │ └───────────────────────────────────────────────┘   │ ║
║  │        [← Previous]  Page 1 of 10  [Next →]         │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ ⚡ Quick Actions                                     │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │  [📥 Export]  [⚠️ Failed]  [📊 Missing]  [🗑️ Clear] │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ ▶ ⚠️ Failed Requests (3 items)                      │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ ▶ 📊 Missing RAG Context (0 items)                  │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## Log Entry Examples

### INFO Log (Green)
```
┌────────────────────────────────────────────────┐
│ 10:30:45  INFO   Request processed successfully│
│   {"model":"gemini","duration_ms":123}         │
└────────────────────────────────────────────────┘
   └─ Click to view full details in modal
```

### WARN Log (Yellow)
```
┌────────────────────────────────────────────────┐
│ 10:30:46  WARN   Response time exceeded 2s     │
│   {"model":"vertex","duration_ms":2340}        │
└────────────────────────────────────────────────┘
```

### ERROR Log (Red)
```
┌────────────────────────────────────────────────┐
│ 10:30:47  ERROR  Connection timeout            │
│   {"model":"ollama","error":"Timeout after 30s"}│
└────────────────────────────────────────────────┘
```

### DEBUG Log (Gray)
```
┌────────────────────────────────────────────────┐
│ 10:30:48  DEBUG  Processing RAG query          │
│   {"query":"What is the project structure?"}   │
└────────────────────────────────────────────────┘
```

---

## Filter Controls

```
┌──────────────────────────────────────────────────┐
│ Filters:                                         │
│                                                  │
│  Severity:  ┌──────────────┐   Model:  ┌──────┐│
│            │ All Levels ▼ │          │ ALL ▼ ││
│            └──────────────┘          └────────┘│
│                                      [🔄 Refresh]│
└──────────────────────────────────────────────────┘
```

### Severity Options
- All Levels
- Debug
- Info
- Warning
- Error

### Model Options
- All Models
- Gemini
- Vertex AI
- Ollama

---

## Action Buttons

```
┌───────────────────────────────────────────────────────┐
│  ⚡ Quick Actions                                     │
├───────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │ 📥 Export   │  │ ⚠️ Failed    │  │ 📊 Missing   │ │
│  │ Logs        │  │ Requests    │  │ Data         │ │
│  └─────────────┘  └─────────────┘  └──────────────┘ │
│                                                       │
│  ┌─────────────┐                                     │
│  │ 🗑️ Clear    │                                     │
│  │ All Logs   │                                     │
│  └─────────────┘                                     │
└───────────────────────────────────────────────────────┘
```

### Button Actions
- **Export Logs**: Download as JSON
- **Failed Requests**: Show diagnostic panel
- **Missing Data**: Show missing context
- **Clear All Logs**: Clear backend (with confirm)

---

## Collapsible Panels

### Collapsed State
```
┌────────────────────────────────────────────┐
│ ▶ ⚠️ Failed Requests (3 items)            │
└────────────────────────────────────────────┘
```

### Expanded State
```
┌────────────────────────────────────────────┐
│ ▼ ⚠️ Failed Requests (3 items)            │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ 10:28:15               gemini        │ │
│  │ Request: Generate authentication     │ │
│  │ Error: Connection timeout            │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ 10:25:30               vertex        │ │
│  │ Request: Code completion             │ │
│  │ Error: Rate limit exceeded           │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ 10:20:45               ollama        │ │
│  │ Request: Refactor code               │ │
│  │ Error: Model not available           │ │
│  └──────────────────────────────────────┘ │
│                                            │
└────────────────────────────────────────────┘
```

---

## Detail Modal

### When clicking a log entry:

```
┌─────────────────────────────────────────────────────┐
│                    BACKDROP (BLUR)                  │
│                                                     │
│   ┌───────────────────────────────────────────┐   │
│   │ Log Entry - INFO                      [×] │   │
│   ├───────────────────────────────────────────┤   │
│   │                                           │   │
│   │  {                                        │   │
│   │    "timestamp": "2024-01-15T10:30:45Z",  │   │
│   │    "level": "INFO",                       │   │
│   │    "message": "Request processed",        │   │
│   │    "metadata": {                          │   │
│   │      "model": "gemini",                   │   │
│   │      "duration_ms": 123,                  │   │
│   │      "tokens": 450,                       │   │
│   │      "cost": 0.0023                       │   │
│   │    }                                      │   │
│   │  }                                        │   │
│   │                                           │   │
│   │  (scrollable if large)                   │   │
│   │                                           │   │
│   └───────────────────────────────────────────┘   │
│                                                     │
│   Click outside or [×] to close                    │
└─────────────────────────────────────────────────────┘
```

---

## Color Palette

### Log Level Colors

| Level | Color | Hex | Visual |
|-------|-------|-----|--------|
| INFO | Green | #10b981 | 🟢 |
| WARN | Yellow | #fbbf24 | 🟡 |
| ERROR | Red | #f87171 | 🔴 |
| DEBUG | Gray | #64748b | ⚪ |

### Background Colors

| Element | Color | Hex |
|---------|-------|-----|
| Primary BG | Dark Blue | #0f172a |
| Secondary BG | Lighter Blue | #1e293b |
| Tertiary BG | Medium Blue | #334155 |
| Glass BG | Transparent Blue | rgba(30,41,59,0.8) |

### Text Colors

| Type | Color | Hex |
|------|-------|-----|
| Primary Text | White | #f8fafc |
| Secondary Text | Gray | #94a3b8 |
| Muted Text | Dim Gray | #64748b |

---

## Responsive Behavior

### Desktop (>1024px)
```
┌──────────┬────────────────────┬──────────┐
│ Sidebar  │   Main Content     │ Right    │
│          │   (Debug Panel)    │ Panel    │
│          │                    │          │
│ [Tabs]   │  [Logs Stream]     │ [Agents] │
│          │  [Filters]         │          │
│          │  [Actions]         │          │
└──────────┴────────────────────┴──────────┘
```

### Mobile (<1024px)
```
┌─────────────────────────┐
│    Header               │
├─────────────────────────┤
│                         │
│   Main Content          │
│   (Debug Panel)         │
│                         │
│   [Full Width]          │
│                         │
└─────────────────────────┘
```

---

## State Indicators

### Loading State
```
┌─────────────────────────────┐
│  ⏳ Loading logs...          │
└─────────────────────────────┘
```

### Empty State
```
┌─────────────────────────────┐
│      📝                      │
│  No logs to display          │
└─────────────────────────────┘
```

### Error State
```
┌─────────────────────────────┐
│      ⚠️                      │
│  Failed to load logs         │
│  Check backend connection    │
└─────────────────────────────┘
```

---

## Interaction Flow

### 1. Opening Debug Tab
```
User clicks "🐛 Debug"
        ↓
Tab becomes active
        ↓
startDebugMonitoring() called
        ↓
Fetch logs from API
        ↓
Display in UI
        ↓
Start auto-refresh (3s)
```

### 2. Filtering Logs
```
User selects filter
        ↓
applyLogFilters() called
        ↓
Filter logs client-side
        ↓
Update display instantly
        ↓
(No server call needed)
```

### 3. Viewing Details
```
User clicks log entry
        ↓
showLogDetails() called
        ↓
Format as JSON
        ↓
Show in modal
        ↓
User clicks × or outside
        ↓
Modal closes
```

### 4. Exporting Logs
```
User clicks "Export"
        ↓
exportLogs() called
        ↓
Fetch /debug/export
        ↓
Create blob
        ↓
Trigger download
        ↓
File saved
```

---

## Auto-Refresh Behavior

```
Tab Active:
  ┌─────────────┐
  │ Fetch Logs  │
  └─────┬───────┘
        │
        ├─── 3 seconds ────┐
        │                  │
        ↓                  ↓
  ┌─────────────┐    ┌─────────────┐
  │ Fetch Logs  │    │ Fetch Logs  │
  └─────┬───────┘    └─────┬───────┘
        │                  │
        └─── continues ────┘

Tab Inactive:
  ┌─────────────┐
  │ Stop Refresh│
  └─────────────┘
        ↓
   (No API calls)
```

---

## Pagination Flow

```
┌──────────────────────────────────┐
│  [← Prev]  Page 1 of 5  [Next →] │
└──────────────────────────────────┘
      ↑                        ↑
      │                        │
   Disabled                 Enabled
   (first page)          (more pages)

After clicking Next:
┌──────────────────────────────────┐
│  [← Prev]  Page 2 of 5  [Next →] │
└──────────────────────────────────┘
      ↑                        ↑
      │                        │
   Enabled                  Enabled
   (can go back)         (more pages)
```

---

## Keyboard Shortcuts (Future Enhancement)

```
Potential shortcuts:
  r     - Refresh logs
  f     - Focus filter
  c     - Clear display
  e     - Export logs
  Esc   - Close modal
  ↑↓    - Navigate logs
```

---

## Mobile View

```
┌───────────────────────────┐
│ 📜 Real-time Log Stream   │
│ [Auto-scroll ✓]           │
├───────────────────────────┤
│ [Severity ▼] [Model ▼]    │
│ [�� Refresh]              │
├───────────────────────────┤
│ ┌───────────────────────┐ │
│ │ 10:30:45  INFO        │ │
│ │ Request processed     │ │
│ │ {metadata}            │ │
│ └───────────────────────┘ │
│ (scrollable)              │
├───────────────────────────┤
│ [← Prev] Page 1 [Next →]  │
├───────────────────────────┤
│ ⚡ Quick Actions           │
│ [Export] [Failed]         │
│ [Missing] [Clear]         │
└───────────────────────────┘
```

---

## Summary

The Debug tab provides a **comprehensive, visually appealing** interface for:

✅ Real-time log monitoring
✅ Advanced filtering
✅ Diagnostic tools
✅ Export capabilities
✅ Detailed log inspection
✅ Responsive design
✅ Consistent UI/UX

All with a **dark theme**, **glass morphism** effects, and **smooth animations**!

---

**Visual Design**: ⭐⭐⭐⭐⭐  
**User Experience**: ⭐⭐⭐⭐⭐  
**Functionality**: ⭐⭐⭐⭐⭐
