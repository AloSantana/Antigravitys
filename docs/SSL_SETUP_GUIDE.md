# SSL/HTTPS Setup Guide

This guide covers setting up SSL certificates for secure HTTPS access to your Antigravity Workspace.

## Table of Contents

- [Automatic SSL for seecast.cloud](#automatic-ssl-for-seecastcloud)
- [Manual SSL Setup](#manual-ssl-setup)
- [Troubleshooting SSL](#troubleshooting-ssl)
- [SSL Certificate Management](#ssl-certificate-management)

## Automatic SSL for seecast.cloud

The remote installer automatically detects and configures SSL for `seecast.cloud` domains.

### One-Line Installation with Auto-SSL

```bash
# For seecast.cloud domain
AUTO_SSL_DOMAIN=seecast.cloud AUTO_SSL_EMAIL=admin@seecast.cloud \
  curl -fsSL https://raw.githubusercontent.com/primoscope/antigravity-workspace-template/main/install-remote.sh | bash
```

### What Happens Automatically

1. ✅ Detects seecast.cloud domain
2. ✅ Installs certbot and python3-certbot-nginx
3. ✅ Obtains Let's Encrypt SSL certificate
4. ✅ Configures nginx for HTTPS
5. ✅ Sets up automatic certificate renewal
6. ✅ Updates .env with SSL_ENABLED=true

### Prerequisites for Auto-SSL

- Domain must point to your VPS IP
- Port 80 must be accessible from the internet
- Valid email address for Let's Encrypt notifications

## Manual SSL Setup

### For Any Domain

```bash
# During installation, you'll be prompted:
Do you want to setup SSL with Let's Encrypt? (requires domain name) (y/N): y
Enter your email for Let's Encrypt: your-email@example.com
```

### After Installation

If you skipped SSL during installation, you can set it up later:

```bash
# Install certbot if not already installed
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Certificate will auto-renew
```

### Custom SSL Certificates

If you have your own SSL certificates:

1. **Place certificates on server:**
```bash
# Copy your certificates to a secure location
sudo mkdir -p /etc/ssl/private
sudo cp fullchain.pem /etc/ssl/certs/
sudo cp privkey.pem /etc/ssl/private/
sudo chmod 600 /etc/ssl/private/privkey.pem
```

2. **Update .env:**
```bash
SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/fullchain.pem
SSL_KEY_PATH=/etc/ssl/private/privkey.pem
```

3. **Update nginx configuration:**
```bash
sudo nano /etc/nginx/sites-available/antigravity
```

Add SSL configuration:
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/private/privkey.pem;
    
    # Strong SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # ... rest of your configuration
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}
```

4. **Restart services:**
```bash
sudo nginx -t
sudo systemctl restart nginx
cd ~/antigravity-workspace-template
./stop.sh && ./start.sh
```

## Troubleshooting SSL

### Certificate Installation Failed

**Symptom:** Certbot fails to obtain certificate

**Common Causes:**

1. **Domain doesn't point to server**
   ```bash
   # Check DNS
   dig +short yourdomain.com
   # Should return your VPS IP
   
   # Check from another machine
   nslookup yourdomain.com
   ```

2. **Port 80 blocked**
   ```bash
   # Check if nginx is listening
   sudo netstat -tlnp | grep :80
   
   # Check firewall
   sudo ufw status
   sudo ufw allow 80/tcp
   
   # Test from outside
   curl http://yourdomain.com
   ```

3. **Nginx not running**
   ```bash
   sudo systemctl status nginx
   sudo systemctl start nginx
   ```

4. **Rate limit reached**
   Let's Encrypt has rate limits. Wait and try again later.

### Certificate Renewal Issues

**Check renewal status:**
```bash
sudo certbot certificates
```

**Test renewal:**
```bash
sudo certbot renew --dry-run
```

**Force renewal:**
```bash
sudo certbot renew --force-renewal
```

**Check renewal cron job:**
```bash
sudo crontab -l | grep certbot
```

### Mixed Content Warnings

If you see mixed content warnings after enabling HTTPS:

1. **Update .env:**
```bash
# Ensure ALLOWED_ORIGINS includes https://
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

2. **Check WebSocket connection:**
The frontend should automatically use `wss://` (secure WebSocket) when accessed via HTTPS.

3. **Restart services:**
```bash
./stop.sh && ./start.sh
```

### Certificate Expiration

Let's Encrypt certificates expire after 90 days but auto-renew.

**Check expiration:**
```bash
sudo certbot certificates
```

**Setup auto-renewal (if not configured):**
```bash
# Add to crontab
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

**Test auto-renewal:**
```bash
sudo certbot renew --dry-run
```

## SSL Certificate Management

### View Certificate Details

```bash
# View all certificates
sudo certbot certificates

# Check certificate expiration
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Revoke Certificate

If you need to revoke a certificate:

```bash
sudo certbot revoke --cert-path /etc/letsencrypt/live/yourdomain.com/cert.pem
```

### Delete Certificate

```bash
sudo certbot delete --cert-name yourdomain.com
```

### Add Multiple Domains

```bash
# Add www subdomain
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Add multiple subdomains
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com -d app.yourdomain.com
```

### Check SSL Configuration

Use SSL testing tools:

```bash
# From command line
curl -vI https://yourdomain.com 2>&1 | grep -i ssl

# Online tools
# Visit: https://www.ssllabs.com/ssltest/
# Enter your domain for a comprehensive SSL/TLS test
```

## Best Practices

### 1. Use Strong SSL Settings

In nginx configuration:
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

### 2. Enable HSTS

Add to nginx server block:
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 3. Setup OCSP Stapling

```nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/letsencrypt/live/yourdomain.com/chain.pem;
```

### 4. Regular Monitoring

```bash
# Add to crontab for weekly SSL check
0 0 * * 0 /usr/bin/certbot certificates | mail -s "SSL Certificate Status" admin@yourdomain.com
```

### 5. Backup Certificates

```bash
# Backup Let's Encrypt directory
sudo tar -czf letsencrypt-backup-$(date +%Y%m%d).tar.gz /etc/letsencrypt

# Store backup securely off-site
```

## Quick Reference

### Installation Commands

```bash
# Basic install
curl -fsSL https://raw.githubusercontent.com/primoscope/antigravity-workspace-template/main/install-remote.sh | bash

# With auto-SSL for seecast.cloud
AUTO_SSL_DOMAIN=seecast.cloud AUTO_SSL_EMAIL=admin@seecast.cloud \
  curl -fsSL https://raw.githubusercontent.com/primoscope/antigravity-workspace-template/main/install-remote.sh | bash

# Manual SSL setup later
sudo certbot --nginx -d yourdomain.com
```

### Verification Commands

```bash
# Check certificate
sudo certbot certificates

# Test renewal
sudo certbot renew --dry-run

# Check nginx SSL
sudo nginx -t

# View SSL info
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

### Maintenance Commands

```bash
# Renew all certificates
sudo certbot renew

# Restart nginx
sudo systemctl restart nginx

# View renewal log
sudo cat /var/log/letsencrypt/letsencrypt.log
```

## Support

For issues with SSL setup:

1. Check logs: `/var/log/letsencrypt/letsencrypt.log`
2. Review nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Test DNS: `dig +short yourdomain.com`
4. Verify firewall: `sudo ufw status`

For more help, visit:
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/docs/)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
