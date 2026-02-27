# Application Startup Flow & Issue Diagnosis

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION STARTUP FLOW                      │
└─────────────────────────────────────────────────────────────────┘

                            USER STARTS APP
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
            ❌ WRONG WAY                  ✅ CORRECT WAY
                    │                           │
         ┌──────────▼──────────┐    ┌──────────▼──────────┐
         │ python backend/     │    │  ./start.sh         │
         │       main.py       │    │  or                 │
         │ (from project root) │    │  cd backend &&      │
         └──────────┬──────────┘    │  python main.py     │
                    │                └──────────┬──────────┘
                    │                           │
         ┌──────────▼──────────┐    ┌──────────▼──────────┐
         │ Python cwd:         │    │ Python cwd:         │
         │   /project/root     │    │   /project/backend  │
         └──────────┬──────────┘    └──────────┬──────────┘
                    │                           │
         ┌──────────▼──────────┐    ┌──────────▼──────────┐
         │ Import search:      │    │ Import search:      │
         │ • ./agent.py ✓      │    │ • ./agent/ ✓        │
         │ • ./backend/agent/  │    │   (package found!)  │
         │   (shadowed!)       │    └──────────┬──────────┘
         └──────────┬──────────┘               │
                    │                           │
         ┌──────────▼──────────┐    ┌──────────▼──────────┐
         │ ❌ FAIL:            │    │ ✅ SUCCESS:         │
         │ ModuleNotFoundError │    │ All imports work    │
         │ 'agent' is not a    │    └──────────┬──────────┘
         │  package            │               │
         └─────────────────────┘    ┌──────────▼──────────┐
                                    │ Import all modules: │
                                    │ • FastAPI           │
                                    │ • Orchestrator      │
                                    │ • GeminiClient      │
                                    │ • Watcher           │
                                    │ • SettingsManager   │
                                    └──────────┬──────────┘
                                               │
                                    ┌──────────▼──────────┐
                                    │ Initialize:         │
                                    │ • Rate limiter      │
                                    │ • Database          │
                                    │ • File watcher      │
                                    │ • API clients       │
                                    └──────────┬──────────┘
                                               │
                                    ┌──────────▼──────────┐
                                    │ Check API keys:     │
                                    │ GEMINI_API_KEY?     │
                                    └──────────┬──────────┘
                                               │
                                    ┌──────────┴──────────┐
                                    │                     │
                           ┌────────▼────────┐  ┌────────▼────────┐
                           │ ✅ Key Present  │  │ ⚠ Key Missing  │
                           └────────┬────────┘  └────────┬────────┘
                                    │                     │
                           ┌────────▼────────┐  ┌────────▼────────┐
                           │ Initialize      │  │ Warning logged  │
                           │ Gemini client   │  │ client.model =  │
                           │ with API        │  │     None        │
                           └────────┬────────┘  └────────┬────────┘
                                    │                     │
                                    └──────────┬──────────┘
                                               │
                                    ┌──────────▼──────────┐
                                    │ Start uvicorn:      │
                                    │ http://0.0.0.0:8000 │
                                    └──────────┬──────────┘
                                               │
                                    ┌──────────▼──────────┐
                                    │ ✅ SERVER RUNNING   │
                                    │ Ready for requests! │
                                    └─────────────────────┘
```

---

## File Conflict Visualization

```
PROJECT ROOT STRUCTURE:
═══════════════════════════════════════════════════════════

antigravity-workspace-template/
│
├── agent.py ←─────────────────────┐ ⚠ NAME CONFLICT!
│   (CLI wrapper file)             │
│                                   │ Python sees this first
│                                   │ when running from root
└── backend/                        │
    │                               │
    ├── agent/ ←──────────────────┤
    │   │  (actual package)         │
    │   ├── __init__.py             │
    │   ├── orchestrator.py         │
    │   ├── gemini_client.py        │
    │   └── ...                     │
    │                               │
    └── main.py                     │
        │                           │
        └─ from agent.orchestrator  │
                  ↑                 │
                  └─────────────────┘
                     Tries to import but...
                     agent.py file blocks it!

SOLUTION:
═════════
Run from backend/ directory so Python looks in ./agent/
instead of ../agent.py
```

---

## Graceful Fallback Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              GEMINI CLIENT INITIALIZATION FLOW                   │
└─────────────────────────────────────────────────────────────────┘

                    GeminiClient.__init__(api_key)
                                  │
                    ┌─────────────▼─────────────┐
                    │ if not api_key:          │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
              ✅ Has Key                  ⚠ No Key
                    │                           │
         ┌──────────▼──────────┐    ┌──────────▼──────────┐
         │ genai.configure()   │    │ print(Warning)      │
         │ self.model = Model  │    │ self.model = None   │
         │ self.embed_model =  │    │ self.embed_model =  │
         │   "embedding-001"   │    │   None              │
         └──────────┬──────────┘    └──────────┬──────────┘
                    │                           │
                    └──────────┬────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Client initialized  │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┴───────────────────┐
           │                                       │
    User calls                              User calls
    generate()                              embed()
           │                                       │
┌──────────▼──────────┐            ┌──────────────▼──────────┐
│ if not self.model:  │            │ if not self.model:      │
│   return "Error:    │            │   return []             │
│   Not configured"   │            │   (empty embeddings)    │
└──────────┬──────────┘            └──────────┬──────────────┘
           │                                   │
           └──────────┬────────────────────────┘
                      │
           ┌──────────▼──────────┐
           │ No crash!           │
           │ Graceful error msg  │
           └─────────────────────┘
```

---

## Rate Limiter Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                 DEFENSE-IN-DEPTH RATE LIMITING                   │
└─────────────────────────────────────────────────────────────────┘

                        HTTP REQUEST
                             │
                 ┌───────────▼───────────┐
                 │  Layer 1: slowapi     │
                 │  (HTTP middleware)    │
                 │  100/minute default   │
                 │  30/minute for chat   │
                 └───────────┬───────────┘
                             │
                    ✅ Not exceeded
                             │
                 ┌───────────▼───────────┐
                 │  FastAPI Endpoint     │
                 │  @limiter.limit(...)  │
                 └───────────┬───────────┘
                             │
                 ┌───────────▼───────────┐
                 │  Orchestrator         │
                 │  .gemini.generate()   │
                 └───────────┬───────────┘
                             │
                 ┌───────────▼───────────┐
                 │  Layer 2: Internal    │
                 │  GeminiClient         │
                 │  _rate_limit()        │
                 │  100ms between calls  │
                 └───────────┬───────────┘
                             │
                    ✅ Not too fast
                             │
                 ┌───────────▼───────────┐
                 │  Actual API Call      │
                 │  genai.generate()     │
                 └───────────┬───────────┘
                             │
                        RESPONSE

✅ Both layers work independently
✅ No conflicts
✅ Defense-in-depth protection
```

---

## Dependency Check Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPENDENCY VERIFICATION                       │
└─────────────────────────────────────────────────────────────────┘

REQUIRED DEPENDENCIES:
═══════════════════════════════════════
fastapi             ✅ Installed (0.128.8)
uvicorn             ✅ Installed (0.40.0)
pydantic            ✅ Installed (2.12.5)
pydantic-settings   ✅ Installed (2.12.0)
python-dotenv       ✅ Installed
slowapi             ✅ Installed
chromadb            ✅ Installed
httpx               ✅ Installed
google-genai        ✅ Installed (1.63.0)
google-generativeai ✅ Installed (0.8.6) ⚠ Deprecated

OPTIONAL DEPENDENCIES:
═══════════════════════════════════════
pyngrok             ○ Not installed (tunnel feature)
google-cloud-ai     ○ Not installed (Vertex AI)

                        │
        ┌───────────────┴───────────────┐
        │                               │
   REQUIRED                         OPTIONAL
   missing?                         missing?
        │                               │
        NO                              YES (OK!)
        │                               │
        ▼                               ▼
   ✅ CONTINUE                    ⚠ LOG WARNING
   Start app                     Continue anyway
        │                               │
        └───────────────┬───────────────┘
                        │
                        ▼
                ✅ APP STARTS
```

---

## Summary Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                  INVESTIGATION RESULTS                           │
└─────────────────────────────────────────────────────────────────┘

TEST CATEGORIES:                              STATUS
══════════════════════════════════════════════════════════════════

Module Imports (7 tests)                      ✅✅✅✅✅✅✅
Graceful Fallback (4 tests)                   ✅✅✅✅
Rate Limiter Integration (4 tests)            ✅✅✅✅
Circular Import Check (1 test)                ✅
Full Startup Test (9 tests)                   ✅✅✅✅✅✅✅✅✅
Dependency Verification (11 tests)            ✅✅✅✅✅✅✅✅✅✅✅

──────────────────────────────────────────────────────────────────
TOTAL: 35 tests                               35 PASSED, 0 FAILED

╔══════════════════════════════════════════════════════════════════╗
║                    FINAL VERDICT                                 ║
║                                                                  ║
║  ✅ NO CRITICAL BUGS FOUND                                       ║
║  ✅ NO BLOCKING ISSUES                                           ║
║  ✅ APPLICATION IS PRODUCTION-READY                              ║
║                                                                  ║
║  Action Required: Documentation update only                     ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Quick Reference

### ✅ DO THIS:
```bash
./start.sh                    # Automated start (recommended)
cd backend && python main.py  # Manual start
docker-compose up             # Docker start
```

### ❌ DON'T DO THIS:
```bash
python backend/main.py        # Wrong! Import errors!
python -m backend.main        # Wrong! Not a package!
```

### 🔍 DEBUGGING:
```bash
# Test imports
cd backend && python -c "from agent.orchestrator import Orchestrator"

# Check dependencies
pip list | grep -E "(fastapi|gemini|pydantic)"

# View logs
tail -f logs/backend.log
```

---

**Related Documents:**
- Full Report: `STARTUP_INVESTIGATION_REPORT.md`
- Quick Summary: `STARTUP_QUICK_SUMMARY.md`
