# Security Guide

This document outlines the security features and best practices for the Antigravity Workspace Template.

## Table of Contents
- [Security Features](#security-features)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Vulnerability Reporting](#vulnerability-reporting)

## Security Features

### 1. Input Validation

All user inputs are validated to prevent common vulnerabilities:

#### File Upload Security
- **File size limits**: Configurable via `MAX_FILE_SIZE` (default: 10MB)
- **Extension whitelist**: Only specific file types allowed (.py, .js, .md, .txt, .json, .yaml, .yml, .sh, .html, .css)
- **Filename sanitization**: Prevents path traversal attacks (e.g., `../../etc/passwd`)
- **Path verification**: Ensures files are written only within designated directories

#### Message Validation
- **Length limits**: Configurable via `MAX_MESSAGE_LENGTH` (default: 10,000 characters)
- **Empty message prevention**: Rejects empty or whitespace-only messages
- **WebSocket input validation**: All WebSocket messages are validated before processing

### 2. Rate Limiting

Rate limiting prevents abuse and DoS attacks:

- **Default limit**: 100 requests per minute per IP address
- **Upload endpoint**: Stricter limit of 20 requests per minute
- **Automatic responses**: Returns HTTP 429 when limits exceeded
- **Per-IP tracking**: Uses client IP address for rate limiting

Configure rate limits in `.env`:
```env
RATE_LIMIT=100/minute
```

### 3. CORS (Cross-Origin Resource Sharing)

CORS is properly configured to prevent unauthorized cross-origin requests:

- **Whitelist-based**: Only specified origins are allowed
- **Environment configuration**: Configure via `ALLOWED_ORIGINS` in `.env`
- **Default for development**: Includes localhost origins
- **Production ready**: Set specific domains for production

Example configuration:
```env
# Development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Production
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 4. Logging and Monitoring

Comprehensive logging helps detect and respond to security incidents:

- **Structured logging**: All security events are logged
- **Error tracking**: Failed validations, rate limit hits, and errors are logged
- **Audit trail**: File uploads and critical operations are logged
- **Log levels**: Configurable via `LOG_LEVEL` environment variable

### 5. Environment Variable Validation

Required environment variables are checked on startup:

- **Missing variables**: Warnings logged for optional missing variables
- **Secure defaults**: Safe defaults used when variables not set
- **Startup validation**: App validates configuration before accepting requests

## Configuration

### Required Environment Variables

None are strictly required, but these are recommended:

```env
# Security Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
MAX_FILE_SIZE=10485760
MAX_MESSAGE_LENGTH=10000
LOG_LEVEL=INFO
```

### Optional Environment Variables

```env
# AI Services (optional, local-only mode available)
GEMINI_API_KEY=your_api_key_here

# GitHub Integration (optional)
COPILOT_MCP_GITHUB_TOKEN=your_token_here
```

### Security Configuration Steps

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Set allowed origins**:
   ```env
   # For development
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
   
   # For production - use your actual domains
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

3. **Configure file limits** (optional):
   ```env
   MAX_FILE_SIZE=10485760  # 10MB in bytes
   MAX_MESSAGE_LENGTH=10000  # 10000 characters
   ```

4. **Set log level**:
   ```env
   LOG_LEVEL=INFO  # Use DEBUG only for development
   ```

## Best Practices

### For Developers

1. **Never commit secrets**:
   - Always use `.env` file (which is gitignored)
   - Never hardcode API keys or passwords
   - Use environment variables for all sensitive data

2. **Validate all inputs**:
   - Use provided validation functions in `backend/security.py`
   - Add validation for any new user inputs
   - Fail securely (deny by default)

3. **Follow principle of least privilege**:
   - API keys should have minimum required permissions
   - File operations limited to designated directories
   - Rate limits protect against abuse

4. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

5. **Use HTTPS in production**:
   - Always use HTTPS for production deployments
   - Set secure cookie flags
   - Enable HSTS headers

### For Deployment

1. **Production checklist**:
   - [ ] Set `ALLOWED_ORIGINS` to production domains only
   - [ ] Use strong, unique values for all API keys
   - [ ] Enable HTTPS/TLS
   - [ ] Set `LOG_LEVEL=INFO` (not DEBUG)
   - [ ] Configure rate limits appropriate for your use case
   - [ ] Set up monitoring and alerting
   - [ ] Regular security updates

2. **Docker deployment**:
   - Use `.env` file (not included in image)
   - Don't expose unnecessary ports
   - Run as non-root user
   - Keep base images updated

3. **Monitoring**:
   - Monitor rate limit hits
   - Watch for repeated validation failures
   - Track unusual file upload patterns
   - Set up alerts for security events

## Security Features Implemented

✅ **Input Validation**
- File upload validation (size, type, path)
- Message length validation
- Filename sanitization
- Path traversal prevention

✅ **Rate Limiting**
- Per-IP rate limiting
- Configurable limits
- Stricter limits for sensitive endpoints

✅ **CORS Protection**
- Whitelist-based origins
- Environment-configurable
- Secure defaults

✅ **Error Handling**
- Specific exception handling
- No information leakage in errors
- Proper logging of security events

✅ **Logging**
- Structured logging
- Security event tracking
- Audit trail for operations

## Known Limitations

1. **Authentication**: No authentication is implemented by default. For production use, consider adding:
   - JWT token authentication
   - OAuth2 integration
   - API key authentication

2. **Encryption**: Data is not encrypted at rest. For sensitive data, implement:
   - Database encryption
   - File encryption
   - Encrypted backups

3. **Session Management**: No session management for multi-user scenarios

## Vulnerability Reporting

If you discover a security vulnerability:

1. **Do not** open a public GitHub issue
2. Email security concerns to: [Your security contact email]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We aim to respond within 48 hours and will keep you updated on the fix.

## Security Roadmap

Future security enhancements planned:

- [ ] JWT authentication system
- [ ] API key authentication
- [ ] Enhanced session management
- [ ] Database encryption
- [ ] Security headers (CSP, X-Frame-Options, etc.)
- [ ] Automated security scanning in CI/CD
- [ ] Penetration testing

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

---

**Last Updated**: 2024-02-06
**Version**: 2.0.0
