# 🚀 Deployment Checklist - Error Handling & Reliability Improvements

## Pre-Deployment

### 1. Review Changes
- [ ] Read `ERROR_HANDLING_IMPROVEMENTS.md` for technical details
- [ ] Review `RELIABILITY_IMPROVEMENTS_SUMMARY.md` for overview
- [ ] Check `RELIABILITY_QUICK_REF.md` for quick reference

### 2. Test Locally
```bash
# Run automated tests
python test_reliability.py
# Should see: 6/6 tests passed ✅

# Test syntax
python -m py_compile backend/watcher.py backend/rag/ingest.py backend/main.py

# Optional: Start app locally
cd backend
python main.py
```

### 3. Configuration (Optional - Has Defaults)
```bash
# Add to .env if you want custom values:
RAG_MAX_FILE_SIZE_MB=10        # Default: 10MB
RAG_MAX_CHUNK_SIZE=2000        # Default: 2000
RAG_CHUNK_OVERLAP=200          # Default: 200
RAG_BATCH_SIZE=5               # Default: 5
RAG_MEMORY_WARNING_MB=500      # Default: 500MB
```

## Deployment

### 4. Deploy Application
```bash
# Standard deployment (no special steps needed)
docker-compose up --build
# OR
./start.sh
```

### 5. Verify Deployment
```bash
# Check health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

# Should see status: "healthy" or "ready"
```

### 6. Check Logs
```bash
# Verify logging is working
docker-compose logs -f backend | head -n 20

# Should see structured logs like:
# 2024-XX-XX XX:XX:XX - backend.watcher - INFO - Watcher started on ...
# 2024-XX-XX XX:XX:XX - backend.rag.ingest - INFO - Ingestion Pipeline initialized ...
```

## Post-Deployment

### 7. Monitor Health
```bash
# Set up monitoring for new endpoints
# Liveness: /health/live
# Readiness: /health/ready

# Example with curl in cron:
*/5 * * * * curl -f http://localhost:8000/health/ready || alert-team
```

### 8. Update Alerting
Set alerts for:
- [ ] Health endpoint returns 503
- [ ] "High memory usage" in logs
- [ ] Ingestion failure rate > 10%
- [ ] Disk usage > 90%
- [ ] Shutdown timeout warnings

### 9. Test Error Scenarios (Optional)
```bash
# Test permission error handling
chmod 000 drop_zone/test-folder
# Upload folder, check logs show graceful handling

# Test large file handling
# Create 15MB file, upload, check it's skipped with warning

# Test graceful shutdown
docker-compose kill -s SIGTERM backend
# Check logs show clean shutdown
```

### 10. Documentation Update
- [ ] Update runbooks with new health endpoints
- [ ] Update monitoring dashboards
- [ ] Update Kubernetes manifests if using liveness/readiness probes
- [ ] Inform team of new configuration options

## Rollback Plan (If Needed)

### If Issues Arise:
```bash
# Quick rollback
git revert HEAD~1

# Or restore specific files
git checkout HEAD~1 -- backend/watcher.py backend/rag/ingest.py backend/main.py .env.example

# Rebuild and restart
docker-compose up --build -d
```

**Note**: All new features are backward compatible. App works fine without new env vars (uses defaults).

## Success Criteria

### Verify These Work:
- [x] App starts successfully
- [x] File watcher starts without errors
- [x] Health endpoints return 200
- [x] Logs show structured logging
- [x] No errors during startup
- [x] File uploads still work
- [x] RAG ingestion still works
- [x] Graceful shutdown on SIGTERM

### Monitor These Metrics (First 24h):
- [ ] Uptime: Should be >99%
- [ ] Error rate: Should be <1%
- [ ] Memory usage: Should be stable
- [ ] Health check: Should always return 200
- [ ] Ingestion success rate: Should be >95%

## Troubleshooting

### Common Issues & Solutions:

**Issue**: Health check returns 503
- **Check**: Component status in response
- **Action**: Fix failing component

**Issue**: "High memory usage" warnings
- **Check**: Current memory threshold
- **Action**: Adjust `RAG_MEMORY_WARNING_MB` or reduce batch size

**Issue**: Files being skipped
- **Check**: File size limits
- **Action**: Adjust `RAG_MAX_FILE_SIZE_MB` if needed

**Issue**: Logs show permission errors
- **Check**: Directory permissions
- **Action**: Fix permissions, watcher will continue with other files

**Issue**: App won't start
- **Check**: Syntax errors, import errors
- **Action**: Run `python test_reliability.py` to diagnose

## Support Contacts

### Get Help:
- **Documentation**: ERROR_HANDLING_IMPROVEMENTS.md
- **Quick Ref**: RELIABILITY_QUICK_REF.md
- **Tests**: Run `python test_reliability.py`
- **Logs**: `docker-compose logs backend`

### Useful Commands:
```bash
# Check logs
docker-compose logs backend | grep ERROR

# Check memory
docker stats backend

# Check disk
df -h

# Restart backend
docker-compose restart backend

# Full rebuild
docker-compose up --build -d
```

## Post-Deployment Review (After 1 Week)

### Metrics to Review:
- [ ] Error rate compared to before
- [ ] Memory usage patterns
- [ ] Ingestion success rate
- [ ] Health check response times
- [ ] Shutdown times
- [ ] Any alerts triggered

### Questions to Answer:
- [ ] Did crashes decrease?
- [ ] Is observability better?
- [ ] Are error logs more helpful?
- [ ] Did health checks help catch issues?
- [ ] Any config adjustments needed?

---

## ✅ Checklist Complete

Once all items are checked:
- [ ] Deployment successful
- [ ] Monitoring configured
- [ ] Team informed
- [ ] Documentation updated
- [ ] Success metrics baseline recorded

**Status**: Ready for Production ✅
**Risk Level**: Low
**Rollback Plan**: Available
**Support**: Documented

---

*Last Updated*: Phase 3, Task 3.2 - Error Handling & Reliability Improvements
