# Settings Panel - Visual Layout

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           SETTINGS PANEL                                    │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ ⚡ LIVE STATUS BANNER (Auto-refresh every 5 seconds)                       │
├────────────────────────────────────────────────────────────────────────────┤
│  🤖 Active Model: gemini    🌐 Ngrok URL: ✓ xyz.ngrok.io   ❤️ Health: ✓   │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ 🤖 AI MODEL CONFIGURATION                                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Select AI Model Provider                                                  │
│  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐                              │
│  │   ✨  │  │   ☁️  │  │   🦙  │  │   🎯  │                              │
│  │Gemini │  │Vertex │  │Ollama │  │ Auto  │                              │
│  │ ◉ Selected│ Enterprise│ Local │ Smart │                              │
│  └───────┘  └───────┘  └───────┘  └───────┘                              │
│                                                                             │
│  ✓ Successfully switched to gemini                                         │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │           🔄 Reload Environment Variables                             │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ✓ Environment reloaded successfully                                       │
│    • ACTIVE_MODEL changed from auto to gemini                             │
│                                                                             │
│  ┌──────────────────────┬──────────────────────┬──────────────────────┐  │
│  │  Test Gemini         │  Test Vertex         │  Test Ollama         │  │
│  └──────────────────────┴──────────────────────┴──────────────────────┘  │
│                                                                             │
│  ✓ Gemini connection successful                                           │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ 🌐 NGROK TUNNEL                                         🔄 Refresh         │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Status:                                                                   │
│  ● Active                                                                  │
│                                                                             │
│  Public URL:                                                               │
│  ┌──────────────────────────────────────────────────────────┬──────────┐ │
│  │ https://xyz.ngrok.io                                     │ 📋 Copy  │ │
│  └──────────────────────────────────────────────────────────┴──────────┘ │
│                                                                             │
│  WebSocket URL:                                                            │
│  ┌──────────────────────────────────────────────────────────┬──────────┐ │
│  │ wss://xyz.ngrok.io/ws                                    │ 📋 Copy  │ │
│  └──────────────────────────────────────────────────────────┴──────────┘ │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ 🔑 API KEYS MANAGEMENT                                                     │
├────────────────────────────────────────────────────────────────────────────┤
│  ... (existing content) ...                                                │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ 🔌 MCP SERVER MANAGER                                      🔄 Refresh      │
├────────────────────────────────────────────────────────────────────────────┤
│  ... (existing content) ...                                                │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ SERVER CONFIGURATION                                                    │
├────────────────────────────────────────────────────────────────────────────┤
│  ... (existing content) ...                                                │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ 📝 ENVIRONMENT VARIABLES                                   🔄 Reload       │
├────────────────────────────────────────────────────────────────────────────┤
│  ... (existing content) ...                                                │
└────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                              INTERACTION FLOW
═══════════════════════════════════════════════════════════════════════════════

User Opens Settings Tab
         │
         ├──> Load Settings (loadSettings())
         │    ├──> Load Active Model (loadActiveModel())
         │    │    └──> Set radio button to match active model
         │    │
         │    ├──> Start Live Status Refresh (startLiveStatusRefresh())
         │    │    └──> Updates every 5 seconds
         │    │        ├──> Active Model
         │    │        ├──> Ngrok URL
         │    │        └──> Backend Health
         │    │
         │    └──> Refresh Ngrok Status (refreshNgrokStatus())
         │         └──> Display public URL if active
         │
         ▼
User Selects Model (Gemini/Vertex/Ollama/Auto)
         │
         ├──> selectModel(value)
         │    ├──> POST /settings/models?model_id={value}
         │    ├──> Show success/error message
         │    └──> Update live status banner
         │
         ▼
User Clicks "Reload Environment"
         │
         ├──> reloadEnvironment()
         │    ├──> POST /settings/reload-env
         │    ├──> Show what changed
         │    │    └──> "ACTIVE_MODEL changed from X to Y"
         │    ├──> Update all UI elements
         │    └──> Reload active model display
         │
         ▼
User Clicks "Refresh" on Ngrok Section
         │
         ├──> refreshNgrokStatus()
         │    ├──> GET /ngrok/status
         │    ├──> Update status badge
         │    └──> Show/hide URLs based on status
         │
         ▼
User Clicks "Copy" Button
         │
         ├──> copyToClipboard(inputId)
         │    ├──> Select text in input
         │    ├──> Copy to clipboard
         │    └──> Show success message
         │
         ▼
User Switches to Another Tab
         │
         └──> stopLiveStatusRefresh()
              └──> Stop 5-second interval
         
User Returns to Settings Tab
         │
         └──> startLiveStatusRefresh()
              └──> Resume 5-second interval


═══════════════════════════════════════════════════════════════════════════════
                            STATE MANAGEMENT
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────┐
│  Settings Loaded    │ ──> Boolean flag (settingsLoaded)
└─────────────────────┘

┌─────────────────────┐
│  Refresh Interval   │ ──> Interval ID (liveStatusInterval)
└─────────────────────┘      Started: On Settings tab open
                             Stopped: On tab switch away
                             Frequency: 5 seconds

┌─────────────────────┐
│  Active Model       │ ──> Radio button state
└─────────────────────┘      Updated: On load, on change

┌─────────────────────┐
│  Ngrok Status       │ ──> Active/Inactive
└─────────────────────┘      Updated: On load, on refresh


═══════════════════════════════════════════════════════════════════════════════
                         RESPONSIVE BEHAVIOR
═══════════════════════════════════════════════════════════════════════════════

Desktop (> 768px):
┌────────┬────────┬────────┬────────┐
│ Gemini │ Vertex │ Ollama │  Auto  │
└────────┴────────┴────────┴────────┘

Tablet (480px - 768px):
┌────────┬────────┐
│ Gemini │ Vertex │
├────────┼────────┤
│ Ollama │  Auto  │
└────────┴────────┘

Mobile (< 480px):
┌────────┐
│ Gemini │
├────────┤
│ Vertex │
├────────┤
│ Ollama │
├────────┤
│  Auto  │
└────────┘


═══════════════════════════════════════════════════════════════════════════════
                         COLOR CODING
═══════════════════════════════════════════════════════════════════════════════

Status Colors:
  ● Green  (--success: #34d399)    - Active, Healthy, Success
  ● Red    (--error: #f87171)      - Inactive, Error, Failed
  ● Yellow (--warning: #fbbf24)    - Warning, Checking, Pending

Theme Colors:
  ● Blue   (--accent-blue: #3b82f6)   - Primary actions, borders
  ● Purple (--accent-purple: #8b5cf6) - Gradients, highlights
  ● Gray   (--text-muted: #64748b)    - Secondary text, labels


═══════════════════════════════════════════════════════════════════════════════
                         KEY FEATURES SUMMARY
═══════════════════════════════════════════════════════════════════════════════

✅ Live Status Banner
   - Real-time updates every 5 seconds
   - Shows active model, ngrok URL, health status
   - Pauses when not viewing settings

✅ Model Selection UI
   - Visual radio button cards
   - 4 options: Gemini, Vertex AI, Ollama, Auto
   - Instant switching with feedback
   - Active model highlighted

✅ Reload Environment
   - Full-width prominent button
   - Shows what changed after reload
   - Refreshes all dependent UI elements
   - Clear success/error feedback

✅ Ngrok Tunnel Status
   - Real-time tunnel status
   - Public URL with copy button
   - WebSocket URL with copy button
   - Manual refresh capability
   - Conditional display (shows URLs only when active)

