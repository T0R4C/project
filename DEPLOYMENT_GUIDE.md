# Deployment Guide for Plagiarism Checker

This document provides comprehensive deployment instructions for the plagiarism checker application across various hosting platforms. AI agents should follow these guidelines to successfully deploy the application to production or staging environments.

## Supported Deployment Platforms

1. **Render** (Recommended for simplicity)
2. **Railway** 
3. **Fly.io**
4. **Heroku** (if still available)
5. **Docker** (for any platform that supports containers)
6. **Traditional VPS** (AWS EC2, DigitalOcean, Linode, etc.)
7. **Local Development** (for testing)

## Prerequisites

Before deploying, ensure you have:
- A working plagiarism checker application locally tested
- Python 3.9+ installed
- Git for version control
- Account on your chosen deployment platform
- Basic command-line proficiency

## 1. Preparing the Application for Deployment

### 1.1. Create Requirements File
Generate a precise `requirements.txt` with pinned versions:

```bash
# From your virtual environment
pip freeze > requirements.txt
```

**Example requirements.txt**:
```
Flask==2.3.3
PyMuPDF==1.23.8
nltk==3.8.1
scikit-learn==1.3.2
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
gunicorn==21.2.0
# Optional caching
Flask-Caching==2.0.2
```

### 1.2. Create Procfile (For Heroku, Render, Railway)
Create a file named `Procfile` in the root directory:
```
web: gunicorn app:app --workers 2 --worker-class sync --bind 0.0.0.0:$PORT --timeout 120
```

### 1.3. Create Runtime.txt (For Heroku, Optional for Others)
```
python-3.9.18
```

### 1.4. Prepare NLTK Data
Since NLTK data needs to be downloaded, include this in your startup script or Dockerfile:

```python
# In your app.py or a separate initialization script
import nltk
nltk.download('punkt', quiet=True)
```

### 1.5. Create .gitignore
Ensure you don't commit sensitive or unnecessary files:
```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Application specific
instance/
.uploads/
.cache/
*.log

# NLTK data (if storing locally)
nltk_data/
```

## 2. Platform-Specific Deployment Instructions

### 2.1. Deploy to Render (Recommended)

#### Step-by-Step Guide:
1. **Create Render Account**: Sign up at https://render.com
2. **New Web Service**: Click "New +" → "Web Service"
3. **Connect Repository**: Connect your GitHub/GitLab repo or use manual deploy
4. **Configure Service**:
   - **Name**: plagiarism-checker (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: main (or your deployment branch)
   - **Root Directory**: Leave blank if at repo root
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT`
5. **Environment Variables** (Under "Environment"):
   - No specific vars needed for basic operation
   - Optional: `PYTHONUNBUFFERED=1` for better logging
6. **Advanced Settings**:
   - **Health Check Path**: `/` (optional)
   - **Auto Deploy**: Enable for automatic deploys on push
7. **Create Web Service**: Click "Create Web Service"

#### Render-Specific Notes:
- Render automatically detects `requirements.txt` and `Procfile`
- Uses the port from `$PORT` environment variable
- Provides automatic HTTPS with Let's Encrypt
- Free tier available (with limitations on monthly hours)
- Logs are accessible in the dashboard
- To scale: Adjust instance type in service settings

### 2.2. Deploy to Railway

#### Step-by-Step Guide:
1. **Create Railway Account**: Sign up at https://railway.app
2. **New Project**: Click "New Project" → "Deploy from Repo"
3. **Connect Repository**: Select your GitHub repo
4. **Configure Service**:
   - Railway usually auto-detects the build process
   - If not, specify:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT`
5. **Variables**: Add any needed environment variables
6. **Deploy**: Railway will build and deploy automatically
7. **Domain**: Railway provides a subdomain (you can add custom domain)

#### Railway-Specific Notes:
- Excellent GitHub integration with preview deployments
- Automatic SSL certificates
- Free tier with generous limits
- Easy to add databases or other services later
- Logs visible in dashboard
- Can deploy from Dockerfile if preferred

### 2.3. Deploy to Fly.io

#### Step-by-Step Guide:
1. **Install Flyctl**: 
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```
2. **Login**: `flyctl auth login`
3. **Initialize App**: 
   ```bash
   flyctl launch
   ```
   - Choose app name, region, etc.
   - When asked "Would you like to set up a Postgresql database now?" → Usually No for this app
   - When asked "Would you like to deploy now?" → Yes
4. **Configure fly.toml** (created by launch):
   ```toml
   app = "plagiarism-checker"

   kill_signal = "SIGINT"
   kill_timeout = 5

   [experimental]
     allowed_public_ports = []
     auto_rollback = true

   [[services]]
     http_checks = []
     internal_port = 8080
     protocol = "tcp"
     script_checks = []
     [services.concurrency]
       hard_limit = 25
       soft_limit = 20
     [[services.ports]]
       force_https = true
       port = 80
     [[services.ports]]
       port = 443
       handlers = ["tls"]
     [[services.udp_ports]]
       port = 0

   [env]
     # Add environment variables here if needed
   ```
5. **Update Dockerfile** (if needed - Fly.io usually generates one):
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   # Download NLTK data during build
   RUN python -c "import nltk; nltk.download('punkt', quiet=True)"
   
   EXPOSE 8080
   
   CMD ["gunicorn", "app:app", "--workers", "2", "--bind", "0.0.0.0:8080"]
   ```
6. **Deploy**: 
   ```bash
   flyctl deploy
   ```
7. **Open**: `flyctl open` to visit your deployed app

#### Fly.io-Specific Notes:
- Excellent performance with global distribution
- Built on Firecracker microVMs for security
- Generous free tier
- CLI-first approach but has dashboard
- Automatic scaling based on load
- Built-in monitoring and logging

### 2.4. Deploy with Docker (Universal)

#### Dockerfile:
```dockerfile
# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download NLTK data during build to avoid runtime delays
RUN python -c "import nltk; nltk.download('punkt', quiet=True)"

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Expose port
EXPOSE 5000

# Environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["gunicorn", "app:app", "--workers", "2", "--bind", "0.0.0.0:5000"]
```

#### docker-compose.yml (Optional):
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - .:/app
      - ~/.cache:/home/appuser/.cache
    restart: unless-stopped
```

#### Deployment Commands:
```bash
# Build image
docker build -t plagiarism-checker .

# Run container
docker run -d -p 5000:5000 --name plagiarism-checker plagiarism-checker

# Or with docker-compose
docker-compose up -d
```

### 2.5. Deploy to Traditional VPS (Ubuntu/Debian Example)

#### Step-by-Step Guide:
1. **Provision Server**: Get a VPS (DigitalOcean droplet, AWS EC2, etc.)
2. **Connect via SSH**: `ssh user@your_server_ip`
3. **Update System**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
4. **Install Dependencies**:
   ```bash
   sudo apt install -y python3-pip python3-venv nginx git
   ```
5. **Clone Repository**:
   ```bash
   git clone https://github.com/yourusername/plagiarism-checker.git
   cd plagiarism-checker
   ```
6. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
7. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
8. **Test Locally**:
   ```bash
   python app.py  # Should run on localhost:5000
   ```
9. **Set up Gunicorn as Service**:
   Create `/etc/systemd/system/plagiarism-checker.service`:
   ```ini
   [Unit]
   Description=Gunicorn instance to serve plagiarism checker
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/plagiarism-checker
   Environment="PATH=/path/to/plagiarism-checker/venv/bin"
   ExecStart=/path/to/plagiarism-checker/venv/bin/gunicorn --workers 2 --bind unix:plagiarism-checker.sock -m 007 app:app

   [Install]
   WantedBy=multi-user.target
   ```
10. **Start and Enable Service**:
    ```bash
    sudo systemctl start plagiarism-checker
    sudo systemctl enable plagiarism-checker
    ```
11. **Configure Nginx** (Reverse Proxy):
    Create `/etc/nginx/sites-available/plagiarism-checker`:
    ```nginx
    server {
        listen 80;
        server_name your_domain_or_IP;

        location / {
            include proxy_params;
            proxy_pass http://unix:/path/to/plagiarism-checker/plagiarism-checker.sock;
        }

        location /static/ {
            alias /path/to/plagiarism-checker/static/;
        }
    }
    ```
    Then:
    ```bash
    sudo ln -s /etc/nginx/sites-available/plagiarism-checker /etc/nginx/sites-enabled
    sudo nginx -t
    sudo systemctl restart nginx
    ```
12. **Set up Firewall** (Optional but recommended):
    ```bash
    sudo ufw allow 'Nginx Full'
    sudo ufw enable
    ```

### 2.6. Environment Variables and Configuration

#### Common Environment Variables:
| Variable | Description | Example |
|----------|-------------|---------|
| `PORT` | Port to listen on (auto-set by PaaS) | `10000` |
| `PYTHONUNBUFFERED` | Ensure logs appear in real-time | `1` |
| `WORKERS` | Number of Gunicorn workers (override default) | `4` |
| `TIMEOUT` | Gunicorn worker timeout in seconds | `120` |
| `MAX_CONTENT_LENGTH` | Max upload size in bytes | `10485760` (10MB) |
| `FLASK_ENV` | Environment (development/production) | `production` |
| `SECRET_KEY` | Flask secret key (needed for sessions) | `your-random-secret-key` |
| `CACHE_TYPE` | If using Flask-Caching | `simple` or `redis` |
| `REDIS_URL` | If using Redis cache | `redis://localhost:6379/0` |

#### Setting Environment Variables:
- **Render/Railway/Fly.io**: Through platform dashboard
- **Docker**: `-e VAR=value` or in `docker-compose.yml`
- **VPS**: In service file or `/etc/environment`
- **Local**: `export VAR=value` or `.env` file with python-dotenv

## 3. Post-Deployment Checklist

### 3.1. Immediate Verification
- [ ] Application loads correctly at the deployed URL
- [ ] Home page shows upload form properly
- [ ] File upload works with a small test PDF
- [ ] Results page displays correctly
- [ ] Bibliography exclusion toggle works
- [ ] Error handling works (try uploading non-PDF)
- [ ] Mobile responsiveness checked
- [ ] Console shows no JavaScript errors

### 3.2. Performance Testing
- [ ] Upload small PDF (<500KB): Response <5s
- [ ] Upload medium PDF (2MB): Response <15s
- [ ] Test concurrent users (if possible)
- [ ] Check memory usage over time
- [ ] Verify no memory leaks during extended use

### 3.3. Security Verification
- [ ] Cannot execute arbitrary code via file upload
- [ ] File size limits enforced (if implemented)
- [ ] No directory traversal possible
- [ ] Error messages don't leak stack traces to users
- [ ] HTTPS enabled (should be automatic on most PaaS)
- [ ] Sensitive config not exposed in client-side code

### 3.4. Monitoring and Maintenance
- [ ] Set up logging (if not automatic)
- [ ] Check error rates in logs
- [ ] Set up uptime monitoring (optional)
- [ ] Plan for dependency updates
- [ ] Consider setting up automated backups of any persistent data (though this app is stateless)

## 4. Troubleshooting Common Deployment Issues

### 4.1. Application Fails to Start
**Symptoms**: Deployment fails, service crashes immediately
**Diagnosis**:
- Check build/logs for error messages
- Verify `requirements.txt` is valid
- Check for missing dependencies
- Ensure `app.py` exists and is executable
**Solutions**:
- Rebuild with fresh dependencies
- Check Python version compatibility
- Verify NLTK data downloads correctly
- Look for syntax errors in code

### 4.2. Application Starts but Returns 500 Errors
**Symptoms**: Service runs but all requests return 500
**Diagnosis**:
- Check application logs for exceptions
- Verify environment variables are set correctly
- Check if external APIs are accessible
- Verify file permissions
**Solutions**:
- Fix runtime errors in code
- Ensure API endpoints are reachable from deployment location
- Check firewall/network restrictions
- Add proper error handling if missing

### 4.3. Slow Performance or Timeouts
**Symptoms**: Requests take too long or timeout
**Diagnosis**:
- Check if PDF processing is the bottleneck
- Verify API call latency to Semantic Scholar
- Check worker count and timeout settings
- Look for blocking operations in request handlers
**Solutions**:
- Increase Gunicorn workers or timeout
- Implement/improve caching for API responses
- Optimize PDF processing (if possible)
- Consider asynchronous processing for large files
- Check resource limits on deployment platform

### 4.4. File Upload Issues
**Symptoms**: Upload fails or returns error
**Diagnosis**:
- Check file size limits
- Verify multipart/form-data handling
- Check temporary file storage permissions
- Verify virus/security scanning isn't blocking (unlikely but possible)
**Solutions**:
- Adjust `MAX_CONTENT_LENGTH` if needed
- Ensure tmp directory is writable
- Check file type validation logic
- Test with different PDF files

### 4.5. API Rate Limiting Issues
**Symptoms**: Works initially then starts failing with API errors
**Diagnosis**:
- Check if hitting Semantic Scholar rate limits (~100 req/5min)
- Verify caching is working
- Check if multiple instances are causing combined rate limit issues
**Solutions**:
- Implement or improve caching strategy
- Increase cache TTL
- Consider implementing request queuing or batching
- Evaluate if need to upgrade to paid API tier (for higher volume)
- Add user-friendly rate limit messages

### 4.6. Memory Issues
**Symptoms**: Application crashes with out-of-memory errors
**Diagnosis**:
- Check memory usage patterns
- Look for memory leaks in PDF processing or data structures
- Verify Gunicorn worker memory usage
**Solutions**:
- Reduce number of workers if memory constrained
- Optimize data structures (especially for large documents)
- Ensure proper cleanup of large objects
- Consider streaming processing for very large PDFs
- Increase memory allocation if possible (larger instance type)

## 5. Scaling Considerations

### 5.1. Horizontal Scaling
- Most PaaS platforms handle this automatically
- For VPS: Add more instances behind load balancer
- Ensure application is stateless (it is, for this use case)
- Use shared storage only if needed for persistent caches (not required for MVP)

### 5.2. Vertical Scaling
- Upgrade instance size for more CPU/RAM
- Particularly beneficial for handling larger PDFs or more concurrent users
- Monitor resource usage to determine optimal size

### 5.3. Caching Strategies
- **API Response Cache**: Cache Semantic Scholar responses (already recommended)
- **Result Cache**: Cache recent check results (if checking same documents repeatedly)
- **Template Cache**: Flask automatically caches templates in production
- Consider Redis or Memcached for distributed cache if scaling to multiple instances

### 5.4. Database Considerations
- Current design doesn't require persistent storage
- If adding user accounts/history later:
  - PostgreSQL or MySQL on managed service (Render, Railway, etc.)
  - SQLite for simple cases (but be aware of concurrency limitations)
  - Connection pooling for production

## 6. Update and Maintenance Procedures

### 6.1. Updating Dependencies
```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install -U package-name

# Or update all (be careful with breaking changes)
pip install -U -r requirements.txt

# Then regenerate requirements.txt
pip freeze > requirements.txt
```

### 6.2. Deploying Updates
#### Render/Railway/Fly.io:
- Push to connected branch → auto-deploy
- Or trigger manual deploy in dashboard

#### Docker:
```bash
# Rebuild and restart
docker build -t plagiarism-checker .
docker restart plagiarism-checker
```

#### VPS with Systemd:
```bash
# Pull new code
git pull origin main

# Restart service
sudo systemctl restart plagiarism-checker
```

### 6.3. Rollback Procedures
#### Render/Railway:
- Use deploy history to revert to previous deployment

#### Fly.io:
```bash
flyctl releases
flyctl deploy <release-version>  # or use --ha
```

#### Docker:
```bash
docker stop plagiarism-checker
docker run ...  # with previous image tag
# or if using compose with specific tag
docker-compose pull
docker-compose up -d
```

#### VPS:
```bash
# If using git, checkout previous commit
git checkout <previous-commit>
sudo systemctl restart plagiarism-checker
```

## 7. Monitoring and Observability

### 7.1. Logging
- Ensure `PYTHONUNBUFFERED=1` is set for real-time logs
- Most platforms capture stdout/stderr automatically
- Consider structured logging for production
- Log levels:
  - ERROR: Exceptional conditions
  - WARN: Potentially harmful situations
  - INFO: General operational messages
  - DEBUG: Detailed diagnostic info (only in dev)

### 7.2. Metrics to Monitor
- **Request Rate**: Requests per second/minute
- **Response Time**: Average and percentile (p50, p95, p99)
- **Error Rate**: Percentage of 5xx errors
- **Resource Usage**: CPU, memory, disk I/O per instance
- **External API Latency**: Time to Semantic Scholar and other APIs
- **Upload Size Distribution**: To understand usage patterns

### 7.3. Health Checks
Implement a simple health endpoint:
```python
@app.route('/health')
def health():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}, 200
```
Then configure platform to use this for liveness/readiness checks.

### 7.4. Alerting Considerations
- Set up alerts for:
  - High error rate (>5% for 5 minutes)
  - High latency (p95 > 2s for 10 minutes)
  - High resource utilization (>80% CPU/memory for 15 minutes)
  - Service downtime (no heartbeats for 2 minutes)

## 8. Special Considerations for This Application

### 8.1. Statelessness
- The application doesn't store user-specific data between requests
- Safe to run multiple instances behind load balancer
- No sticky sessions needed

### 8.2. External Dependencies
- **Semantic Scholar API**: Primary external dependency
  - Monitor their status page if available
  - Implement fallback or degraded mode if API unavailable
  - Consider caching to reduce dependency frequency
- **NLTK Data**: Downloaded at startup/build time
  - Ensure it's available in offline environments
  - Consider bundling with application if size permits

### 8.3. File Processing Security
- PDF parsing libraries can have vulnerabilities
- Keep PyMuPDF updated
- Consider running PDF processing in a sandbox if security is paramount
- Validate file content, not just extension

### 8.4. Internationalization
- Currently supports English interface
- If adding i18n later:
  - Use Flask-Babel or similar
  - Store translations separately
  - Ensure UTF-8 everywhere

## 8. Example Deployment Commands Summary

### For Quick Testing Locally:
```bash
# Clone repo
git clone https://github.com/yourusername/plagiarism-checker.git
cd plagiarism-checker

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python app.py
# Visit http://localhost:5000
```

### For Docker Testing:
```bash
docker build -t plagiarism-checker .
docker run -p 5000:5000 plagiarism-checker
# Visit http://localhost:5000
```

### For Render (via CLI - if you prefer):
```bash
# Install Render CLI (if available) or use web dashboard
# Generally, web dashboard is simpler for Render
```

### For Railway:
```bash
railway login
railway init
railway up
```

### For Fly.io:
```bash
flyctl launch  # First time
flyctl deploy  # Subsequent updates
```

## 9. Final Recommendations

1. **Start Simple**: Deploy to Render or Railway first for easiest setup
2. **Test Thoroughly**: Use the test cases from TEST_CASES.md before and after deployment
3. **Monitor Early**: Check logs frequently after initial deployment
4. **Iterate**: Begin with basic features, then add enhancements
5. **Document**: Keep track of environment-specific configurations
6. **Backup**: While this app is stateless, back up any custom configurations or data if you add persistence
7. **Stay Updated**: Regularly update dependencies and platform components
8. **Plan for Growth**: Even though starting small, design choices should allow for scaling

By following this deployment guide, AI agents should be able to successfully deploy the plagiarism checker application to a variety of hosting platforms with confidence in reliability, security, and performance.

Remember that the "best" platform depends on your specific needs:
- **For ease of use**: Render or Railway
- **For performance control**: Fly.io or Docker on any platform
- **For maximum control**: Traditional VPS
- **For ecosystem integration**: Choose based on existing infrastructure

Happy deploying! 🚀