---
description: Add a new API endpoint to the Antigravity FastAPI backend (monolith pattern)
---

<command-instruction>
Guide for adding a new API endpoint. The backend is a monolith — ALL routes live in `backend/main.py`.

## Template

```python
# 1. Define request/response models (add near top of main.py with other models)
class MyFeatureRequest(BaseModel):
    field1: str
    field2: Optional[int] = None

class MyFeatureResponse(BaseModel):
    result: str
    timestamp: str

# 2. Add route handler (search for similar endpoints in main.py for placement)
@app.post("/api/my-feature", response_model=MyFeatureResponse)
async def my_feature_endpoint(request: MyFeatureRequest):
    """One-line description of what this endpoint does.
    
    Args:
        request: MyFeatureRequest with field1 and field2.
        
    Returns:
        MyFeatureResponse with result and timestamp.
    """
    try:
        # Implementation here
        result = f"processed: {request.field1}"
        return MyFeatureResponse(
            result=result,
            timestamp=datetime.now().isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"my_feature_endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Checklist
- [ ] Pydantic models for request and response
- [ ] `@app.{method}` decorator with path
- [ ] Google-style docstring
- [ ] `try/except` with specific exceptions
- [ ] Proper HTTP status codes (400 for validation, 404 for not found, 500 for server error)
- [ ] Add test in `tests/` matching the endpoint
- [ ] Endpoint appears in `/docs` (FastAPI auto-generates this)

## Finding the Right Place in main.py (2955 lines)
Search for nearby endpoints:
```bash
grep -n "@app\." backend/main.py | grep -i "similar_word"
```

All routes are in `backend/main.py`. Do NOT create new route files.
</command-instruction>
