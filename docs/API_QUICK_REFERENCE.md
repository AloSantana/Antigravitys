# Quick Reference: New Backend Endpoints

## 🚀 Quick Start
All new endpoints have been added to `/backend/main.py` and are ready to use.

## 📡 Ngrok Integration

### Status Endpoint
```bash
GET /ngrok/status
```
**Rate Limit:** 30/minute

**Response:**
```json
{
  "enabled": true,
  "active": true,
  "public_url": "https://xxxxx.ngrok.io",
  "websocket_url": "wss://xxxxx.ngrok.io/ws"
}
```

**Usage:**
```bash
curl http://localhost:8000/ngrok/status
```

## ⚙️ Settings Management

### Reload Environment
```bash
POST /settings/reload-env
```
**Rate Limit:** 10/minute

**Response:**
```json
{
  "success": true,
  "environment_reload": {...},
  "orchestrator_reinitialized": true,
  "message": "Environment reloaded and orchestrator reinitialized successfully"
}
```

**Usage:**
```bash
curl -X POST http://localhost:8000/settings/reload-env
```

**Use Case:** After modifying `.env` file, call this endpoint to reload configuration without restarting the server.

## 🐛 Debug Logging API

### 1. Get Debug Logs (Paginated)
```bash
GET /debug/logs
```
**Rate Limit:** 20/minute

**Parameters:**
- `page` (int, default: 1) - Page number
- `per_page` (int, default: 50) - Items per page
- `severity` (string, optional) - Filter by log level (DEBUG, INFO, WARNING, ERROR)
- `model` (string, optional) - Filter by model name
- `start_date` (string, optional) - Filter by start date (ISO format)
- `end_date` (string, optional) - Filter by end date (ISO format)

**Response:**
```json
{
  "logs": [...],
  "page": 1,
  "per_page": 50,
  "total": 150
}
```

**Examples:**
```bash
# Get first page
curl "http://localhost:8000/debug/logs?page=1&per_page=10"

# Filter by severity
curl "http://localhost:8000/debug/logs?severity=ERROR"

# Filter by model
curl "http://localhost:8000/debug/logs?model=gpt-4"

# Combine filters
curl "http://localhost:8000/debug/logs?severity=ERROR&model=gpt-4&page=1"
```

### 2. Export Debug Logs
```bash
GET /debug/export
```
**Rate Limit:** 5/minute

**Parameters:**
- `format` (string, default: "json") - Export format: "json" or "csv"
- `severity` (string, optional) - Filter by log level
- `model` (string, optional) - Filter by model name
- `start_date` (string, optional) - Filter by start date
- `end_date` (string, optional) - Filter by end date

**Response:** File download (JSON or CSV)

**Examples:**
```bash
# Export as JSON
curl "http://localhost:8000/debug/export?format=json" > debug_logs.json

# Export as CSV
curl "http://localhost:8000/debug/export?format=csv" > debug_logs.csv

# Export errors only
curl "http://localhost:8000/debug/export?format=json&severity=ERROR" > errors.json
```

### 3. Get Failed Requests
```bash
GET /debug/failed
```
**Rate Limit:** 20/minute

**Response:**
```json
{
  "failed_requests": [
    {
      "timestamp": "2024-01-01T12:00:00",
      "model": "gpt-4",
      "error": "API timeout",
      "request": {...}
    }
  ],
  "count": 5
}
```

**Usage:**
```bash
curl http://localhost:8000/debug/failed
```

**Use Case:** Quickly identify all requests that resulted in errors.

### 4. Get Missing Data Requests
```bash
GET /debug/missing-data
```
**Rate Limit:** 20/minute

**Response:**
```json
{
  "missing_data_requests": [
    {
      "timestamp": "2024-01-01T12:00:00",
      "issue": "RAG context missing",
      "request": {...}
    }
  ],
  "count": 3
}
```

**Usage:**
```bash
curl http://localhost:8000/debug/missing-data
```

**Use Case:** Identify requests where RAG context was missing or embeddings failed.

### 5. Clear Debug Logs
```bash
POST /debug/clear
```
**Rate Limit:** 2/minute

**Response:**
```json
{
  "success": true,
  "message": "Debug logs cleared successfully"
}
```

**Usage:**
```bash
curl -X POST http://localhost:8000/debug/clear
```

**Note:** Creates a backup before clearing.

## 🎯 Common Workflows

### Troubleshooting Failed Requests
```bash
# 1. Get all failed requests
curl http://localhost:8000/debug/failed

# 2. Export for analysis
curl "http://localhost:8000/debug/export?format=csv&severity=ERROR" > errors.csv

# 3. Check for missing data issues
curl http://localhost:8000/debug/missing-data
```

### Daily Log Review
```bash
# 1. Check ngrok status
curl http://localhost:8000/ngrok/status

# 2. Get recent errors
curl "http://localhost:8000/debug/logs?severity=ERROR&page=1&per_page=20"

# 3. Export for reporting
curl "http://localhost:8000/debug/export?format=json" > daily_logs_$(date +%Y%m%d).json
```

### Configuration Updates
```bash
# 1. Edit .env file
nano .env

# 2. Reload without restart
curl -X POST http://localhost:8000/settings/reload-env

# 3. Verify new settings are active
curl http://localhost:8000/settings
```

### Log Maintenance
```bash
# 1. Export current logs
curl "http://localhost:8000/debug/export?format=json" > backup_$(date +%Y%m%d).json

# 2. Clear logs
curl -X POST http://localhost:8000/debug/clear

# 3. Verify cleared
curl "http://localhost:8000/debug/logs?page=1"
```

## 🔧 Integration Examples

### Python
```python
import requests

# Get debug logs
response = requests.get(
    "http://localhost:8000/debug/logs",
    params={"severity": "ERROR", "per_page": 10}
)
logs = response.json()

# Export logs
response = requests.get(
    "http://localhost:8000/debug/export",
    params={"format": "json", "severity": "ERROR"}
)
with open("errors.json", "wb") as f:
    f.write(response.content)

# Reload environment
response = requests.post("http://localhost:8000/settings/reload-env")
result = response.json()
print(result["message"])
```

### JavaScript/Node.js
```javascript
// Get ngrok status
const response = await fetch('http://localhost:8000/ngrok/status');
const status = await response.json();
console.log('Ngrok URL:', status.public_url);

// Get failed requests
const failed = await fetch('http://localhost:8000/debug/failed');
const data = await failed.json();
console.log(`Found ${data.count} failed requests`);
```

### cURL Scripts
```bash
#!/bin/bash
# monitor.sh - Monitor debug logs

echo "=== Ngrok Status ==="
curl -s http://localhost:8000/ngrok/status | jq

echo -e "\n=== Recent Errors ==="
curl -s "http://localhost:8000/debug/logs?severity=ERROR&per_page=5" | jq

echo -e "\n=== Failed Requests ==="
curl -s http://localhost:8000/debug/failed | jq '.count'
```

## 📊 Rate Limits Summary

| Endpoint | Rate Limit | Use Case |
|----------|-----------|----------|
| `/ngrok/status` | 30/min | Status checks |
| `/settings/reload-env` | 10/min | Config updates |
| `/debug/logs` | 20/min | Log browsing |
| `/debug/export` | 5/min | Log exports |
| `/debug/failed` | 20/min | Error monitoring |
| `/debug/missing-data` | 20/min | Data issue tracking |
| `/debug/clear` | 2/min | Maintenance |

## ⚠️ Important Notes

1. **Ngrok**: Only active when `NGROK_ENABLED=true` in `.env`
2. **Debug Logs**: Automatically backed up before clearing
3. **Settings Reload**: Reinitializes orchestrator (may briefly interrupt operations)
4. **Rate Limiting**: All endpoints have rate limits to prevent abuse
5. **Platform Detection**: Logged automatically on startup

## 🆘 Error Handling

All endpoints return standard HTTP status codes:
- `200` - Success
- `400` - Bad request (invalid parameters)
- `404` - Not found
- `429` - Rate limit exceeded
- `500` - Internal server error

Error response format:
```json
{
  "detail": "Error message here"
}
```

## 📚 Related Documentation
- `MAIN_PY_MODIFICATIONS.md` - Detailed code changes
- `MAIN_PY_TESTING_CHECKLIST.md` - Testing guidelines
- Backend API docs: http://localhost:8000/docs (when running)
