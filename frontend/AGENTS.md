# FRONTEND — Vanilla JS SPA

## OVERVIEW

Single-page application. NO framework, NO build step. Pure HTML + CSS + JS served via nginx.

## STRUCTURE

```
frontend/
├── index.html              # Main SPA — 1222 lines, all HTML structure inline
├── index-enhanced.html     # Enhanced version (alternate)
├── index-original.html     # Original version backup
├── js/
│   └── app.js              # ALL frontend logic — 2914 lines, single file
├── css/
│   ├── style.css           # Primary styles
│   └── legacy.css          # Legacy/fallback styles
└── static/                 # Static assets
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add UI component | `index.html` | Raw HTML, no components/templates |
| Add frontend logic | `js/app.js` | Search by function name or feature keyword |
| WebSocket client | `js/app.js` | Search `WebSocket`, `WS_BASE`. Reconnection with backoff |
| Settings UI | `js/app.js` | Search `settings`, `Settings` |
| Debug tab | `js/app.js` | Search `debug`, `Debug` |
| Styling | `css/style.css` | CSS custom properties for theming (`--bg-*`, `--text-*`, `--border-*`) |
| API calls | `js/app.js` | Search `fetch(`, `API_BASE`. Auto-discovers backend config |

## CONVENTIONS

- **No build step** — files are served directly by nginx
- **No framework** — vanilla JS with DOM manipulation
- CSS custom properties for theming (dark UI by default)
- Backend config auto-discovery: `fetchBackendConfig()` tries ports 8000, 3000
- CDN dependencies: Inter font, JetBrains Mono font, CodeMirror (code editing)

## ANTI-PATTERNS

- **DO NOT** add npm/package.json — project intentionally avoids frontend build tools
- **DO NOT** add React/Vue/Svelte — vanilla JS is the chosen approach
- **DO NOT** create separate JS module files — all logic in single `app.js`
- **DO NOT** inline styles — use CSS custom properties in `style.css`

## NOTES

- Connection status badge updates via WebSocket heartbeat
- `app.js` starts with config detection — must connect to backend before most features work
- `legacy.css` loaded before `style.css` — cascading override pattern
- Frontend served as read-only nginx volume in Docker: `./frontend:/usr/share/nginx/html:ro`
