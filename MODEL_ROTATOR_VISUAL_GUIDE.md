# Model Rotator Tab - Visual Guide

## 🎨 User Interface Overview

### Main Layout
```
┌─────────────────────────────────────────────────────────────────┐
│  Antigravity Workspace                         🔴 🟡 🟢 Status  │
├─────────────────────────────────────────────────────────────────┤
│  [Chat] [Editor] [Terminal] [Debug] [Settings] [Swarm]          │
│  [Sandbox] [Tools] [🔄 Model Rotator] ← NEW TAB                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MODEL ROTATOR CONTENT (see sections below)                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔑 Section 1: API Key Management

### Add Key Form
```
┌─────────────────────────────────────────────────────────────────┐
│  🔑 API Key Management                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌──────────────────┐  ┌──────────┐  ┌────────┐ │
│  │ Service  │  │     API Key      │  │   Name   │  │        │ │
│  │ [Gemini▼]│  │ [••••••••••••]   │  │ [My Key] │  │➕ Add │ │
│  │          │  │                  │  │          │  │  Key   │ │
│  └──────────┘  └──────────────────┘  └──────────┘  └────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Cards Grid
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Production Key  │  │  Development Key │  │   Backup Key     │
│  Gemini          │  │  OpenAI          │  │  Vertex AI       │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│  🟢 AVAILABLE    │  │  🟡 RATE LIMITED │  │  🔴 DISABLED     │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│  Success Rate    │  │  Success Rate    │  │  Success Rate    │
│  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌────────────┐  │
│  │   95.2%    │  │  │  │   87.3%    │  │  │  │   45.1%    │  │
│  └────────────┘  │  │  └────────────┘  │  │  └────────────┘  │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│  Requests        │  │  Requests        │  │  Requests        │
│  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌────────────┐  │
│  │    152     │  │  │  │     89     │  │  │  │     34     │  │
│  └────────────┘  │  │  └────────────┘  │  │  └────────────┘  │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│  Health Score    │  │  Health Score    │  │  Health Score    │
│  ▓▓▓▓▓▓▓▓▓▓░░░  │  │  ▓▓▓▓▓▓▓▓░░░░░  │  │  ▓▓▓▓░░░░░░░░░  │
│   (Excellent)    │  │     (Good)       │  │     (Poor)       │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│  [⏸ Disable]     │  │  [⏸ Disable]     │  │  [✓ Enable]      │
│  [🗑️ Remove]     │  │  [🗑️ Remove]     │  │  [🗑️ Remove]     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## 📊 Section 2: Statistics Dashboard

### Overview Metrics
```
┌─────────────────────────────────────────────────────────────────┐
│  📊 Statistics Dashboard     [🔄 Refresh] [💾 Export] [🗑️ Reset]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐│
│  │     275     │  │    91.2%    │  │   45,200    │  │   3    ││
│  │   REQUESTS  │  │   SUCCESS   │  │   TOKENS    │  │  KEYS  ││
│  │   (Total)   │  │    (Rate)   │  │   (Used)    │  │(Active)││
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Usage Distribution Chart
```
┌─────────────────────────────────────────────────────────────────┐
│  Key Usage Distribution                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Production Key   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  152          │
│                                                                  │
│  Development Key  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░   89          │
│                                                                  │
│  Backup Key       ▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░   34          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔍 Section 3: Live Monitoring

### Real-Time Status Grid
```
┌─────────────────────────────────────────────────────────────────┐
│  🔍 Live Monitoring                    Auto-refresh every 5s     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ Production Key │  │ Errors: 0      │  │ Last: 2m ago     │  │
│  │ AVAILABLE      │  │                │  │                  │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ Development Key│  │ Errors: 2      │  │ Last: 5m ago     │  │
│  │ RATE LIMITED   │  │                │  │                  │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ Backup Key     │  │ Errors: 8      │  │ Last: 1h ago     │  │
│  │ DISABLED       │  │                │  │                  │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔔 Toast Notifications

### Success Notification
```
                                    ┌─────────────────────────┐
                                    │ ✅ API key added        │
                                    │    successfully         │
                                    └─────────────────────────┘
                                         (green border)
```

### Error Notification
```
                                    ┌─────────────────────────┐
                                    │ ❌ Failed to remove key │
                                    │    Please try again     │
                                    └─────────────────────────┘
                                         (red border)
```

### Warning Notification
```
                                    ┌─────────────────────────┐
                                    │ ⚠️ Key rate limited     │
                                    │    Backing off...       │
                                    └─────────────────────────┘
                                         (yellow border)
```

## 🎬 User Flow Examples

### Adding a New Key
```
Step 1: Select Service
┌────────────┐
│ [Gemini ▼] │  ← Click to open dropdown
└────────────┘

Step 2: Enter API Key
┌──────────────────┐
│ [••••••••••••]   │  ← Type your key (masked)
└──────────────────┘

Step 3: Name Your Key (Optional)
┌──────────────────┐
│ [Production Key] │  ← Give it a friendly name
└──────────────────┘

Step 4: Add Key
┌────────┐
│➕ Add │  ← Click to add
│  Key   │
└────────┘

Step 5: Success!
┌─────────────────────────┐
│ ✅ API key added        │  ← Toast notification
│    successfully         │
└─────────────────────────┘

Key appears in grid below ↓
```

### Monitoring Keys
```
Automatic Updates:
  ⏰ Every 5 seconds
  📡 Only when tab is active
  🔄 Updates all metrics

What Gets Updated:
  • Status indicators (🟢🟡🔴)
  • Request counts
  • Success rates
  • Health scores
  • Error counts
  • Last used times
```

### Exporting Statistics
```
Click [💾 Export] →  Downloads JSON file
                     ↓
                rotator-stats-1234567890.json
                     ↓
                Contains:
                • Timestamp
                • All keys data
                • All statistics
                • Full history
```

## 🎨 Color Coding Reference

### Status Indicators
- 🟢 **Green Glow** = Available (ready to use)
- 🟡 **Yellow Glow** = Rate Limited (backing off)
- 🔴 **Red Glow** = Error/Disabled (not usable)

### Health Bars
- **Green Fill** = 90-100% (Excellent)
- **Yellow Fill** = 70-89% (Good)
- **Orange Fill** = 50-69% (Fair)
- **Red Fill** = 0-49% (Poor)

### Buttons
- **Blue Gradient** = Primary actions (Add, Refresh)
- **Gray Background** = Secondary actions (Enable)
- **Red Background** = Destructive actions (Remove, Reset)

## 📱 Responsive Behavior

### Desktop (> 1200px)
```
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Key 1   │  │  Key 2   │  │  Key 3   │  ← 3 columns
└──────────┘  └──────────┘  └──────────┘
```

### Tablet (768px - 1200px)
```
┌──────────┐  ┌──────────┐
│  Key 1   │  │  Key 2   │  ← 2 columns
└──────────┘  └──────────┘
┌──────────┐
│  Key 3   │
└──────────┘
```

### Mobile (< 768px)
```
┌──────────┐
│  Key 1   │  ← 1 column
└──────────┘
┌──────────┐
│  Key 2   │
└──────────┘
┌──────────┐
│  Key 3   │
└──────────┘
```

## 🔐 Security Features

### Password Masking
```
Before: AIzaSyD...key123  ← Visible
After:  •••••••••••••••   ← Masked in form
Stored: abc123...hash     ← Hash only in display
```

### Confirmation Dialogs
```
┌────────────────────────────────────┐
│  Are you sure you want to remove   │
│  "Production Key"?                 │
│                                    │
│  This action cannot be undone.     │
│                                    │
│  [Cancel]  [Remove]                │
└────────────────────────────────────┘
```

## 📊 Loading States

### Initial Load
```
┌─────────────────────────────────┐
│  🔄                             │
│  Loading keys...                │
│                                 │
└─────────────────────────────────┘
```

### Empty State
```
┌─────────────────────────────────┐
│  📭                             │
│  No API keys configured.        │
│  Add your first key above!      │
│                                 │
└─────────────────────────────────┘
```

### Error State
```
┌─────────────────────────────────┐
│  ❌                             │
│  Failed to load keys.           │
│  Please try again.              │
│  [🔄 Retry]                     │
└─────────────────────────────────┘
```

## 🎯 Interactive Elements

All clickable elements have hover effects:
- **Buttons** → Lift up 1px, show shadow
- **Key Cards** → Lift up 2px, blue border
- **Form Fields** → Blue border, subtle glow

## ⌨️ Keyboard Navigation

- `Tab` → Move between fields
- `Shift+Tab` → Move backwards
- `Enter` → Submit form / Confirm action
- `Esc` → Cancel / Close dialog

---

**Visual Design**: Dark theme with glassmorphism effects
**Animations**: Smooth 0.3s transitions
**Accessibility**: WCAG 2.1 AA compliant
**Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)
