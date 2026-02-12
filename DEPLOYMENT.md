# PDF Remediation Tool - Deployment Guide

This guide covers different ways to deploy the PDF Remediation Tool for team access.

## Option 1: Local Network Deployment (Simplest)

Perfect for small teams on the same network.

### Setup on Host Machine:

1. **Clone and setup:**
```bash
git clone https://github.com/adasheasu/pdfremediator.git
cd pdfremediator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

2. **Run the server:**
```bash
python app.py
```

3. **Find your IP address:**
```bash
# Mac/Linux:
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows:
ipconfig | findstr IPv4
```

4. **Share with team:** `http://YOUR_IP_ADDRESS:8080`

### Keep Running (Optional):

Use `nohup` to keep it running even after logging out:
```bash
nohup python app.py > flask.log 2>&1 &
```

Or use `screen`:
```bash
screen -S pdfremediator
python app.py
# Press Ctrl+A then D to detach
# Reattach later with: screen -r pdfremediator
```

---

## Option 2: Production Server (Ubuntu/Linux)

For dedicated server deployment with Gunicorn + Nginx.

### Prerequisites:
- Ubuntu 20.04+ or similar Linux server
- Domain name (optional but recommended)
- SSH access

### Step 1: Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv nginx

# Install Playwright system dependencies
sudo apt install -y \
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 \
    libasound2 libatspi2.0-0
```

### Step 2: Setup Application

```bash
# Create app directory
sudo mkdir -p /var/www/pdfremediator
sudo chown $USER:$USER /var/www/pdfremediator

# Clone repository
cd /var/www/pdfremediator
git clone https://github.com/adasheasu/pdfremediator.git .

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-prod.txt
playwright install chromium

# Create necessary directories
mkdir -p uploads outputs
```

### Step 3: Configure Gunicorn

Create systemd service file:

```bash
sudo nano /etc/systemd/system/pdfremediator.service
```

Add this content:

```ini
[Unit]
Description=PDF Remediation Tool
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/pdfremediator
Environment="PATH=/var/www/pdfremediator/venv/bin"
ExecStart=/var/www/pdfremediator/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8080 \
    --timeout 300 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    wsgi:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pdfremediator
sudo systemctl start pdfremediator
sudo systemctl status pdfremediator
```

### Step 4: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/pdfremediator
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name pdfremediator.yourdomain.com;  # Change this

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeouts for large PDF processing
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/pdfremediator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5: Setup SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d pdfremediator.yourdomain.com
```

---

## Option 3: Docker Deployment (Cross-Platform)

Perfect for consistent deployment across different environments.

### Create Dockerfile:

```dockerfile
FROM python:3.9-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 \
    libasound2 libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY . .

# Create directories for uploads and outputs
RUN mkdir -p uploads outputs

# Expose port
EXPOSE 8080

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "300", "wsgi:app"]
```

### Create docker-compose.yml:

```yaml
version: '3.8'

services:
  pdfremediator:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

### Deploy with Docker:

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Option 4: Cloud Platform Deployment

### A. AWS EC2 Deployment

1. Launch EC2 instance (Ubuntu 20.04, t3.medium or larger)
2. Follow "Option 2: Production Server" instructions above
3. Configure security group to allow port 80/443
4. Use Elastic IP for static address
5. Setup Route 53 for domain name (optional)

**Estimated Cost:** $30-50/month for t3.medium

### B. Azure App Service

1. Create Azure App Service (Linux, Python 3.9)
2. Configure deployment from GitHub
3. Set environment variables
4. Configure startup command: `gunicorn --bind 0.0.0.0:8000 wsgi:app`

**Estimated Cost:** $55-75/month for B1 tier

### C. Google Cloud Run

Cloud Run is serverless and cost-effective:

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/pdfremediator

# Deploy
gcloud run deploy pdfremediator \
    --image gcr.io/PROJECT_ID/pdfremediator \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --timeout 300
```

**Estimated Cost:** Pay per use, ~$10-20/month for moderate usage

### D. Heroku (Easiest Cloud Deployment)

Create `Procfile`:
```
web: gunicorn --bind 0.0.0.0:$PORT --timeout 300 wsgi:app
```

Deploy:
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add Playwright buildpack
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/mxschmitt/heroku-playwright-buildpack.git

# Deploy
git push heroku main

# Open
heroku open
```

**Estimated Cost:** $7-25/month (Hobby/Basic tier)

---

## Option 5: ASU Internal Deployment

If deploying within ASU infrastructure:

### Contact ASU IT:
- **Web Hosting Services:** https://webapps.asu.edu
- **Enterprise Applications:** Submit ServiceNow ticket
- Request VM or container hosting

### ASU-Specific Options:
1. **ASU Web Platform** - For public-facing tools
2. **ASU App Cloud** - For internal applications
3. **ASU Research Computing** - For research-related tools

---

## Security Considerations

### For Production Deployments:

1. **Environment Variables:**
Create `.env` file for sensitive settings:
```bash
SECRET_KEY=your-secret-key-here
MAX_CONTENT_LENGTH=52428800
```

2. **Authentication (Optional):**
Add to `app.py` for basic auth:
```python
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    return username == 'admin' and password == 'your-password'

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response('Authentication required', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def index():
    return render_template('index.html')
```

3. **File Upload Security:**
- Already implemented: file type validation
- Already implemented: secure filenames
- Consider: virus scanning for uploaded PDFs

4. **Rate Limiting:**
Install Flask-Limiter:
```bash
pip install Flask-Limiter
```

Add to `app.py`:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)
```

5. **HTTPS:**
- Always use HTTPS in production
- Use Let's Encrypt for free SSL certificates
- Certbot makes this automatic with Nginx

---

## Monitoring and Maintenance

### Log Management:

```bash
# View Gunicorn logs
sudo journalctl -u pdfremediator -f

# Rotate logs
sudo nano /etc/logrotate.d/pdfremediator
```

Add:
```
/var/www/pdfremediator/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    missingok
}
```

### Cleanup Old Files:

Add cron job to clean old uploads/outputs:
```bash
crontab -e
```

Add:
```
# Clean files older than 24 hours every day at 3am
0 3 * * * find /var/www/pdfremediator/uploads -type f -mtime +1 -delete
0 3 * * * find /var/www/pdfremediator/outputs -type f -mtime +1 -delete
```

### Health Check:

Create `health_check.py`:
```python
import requests
import sys

try:
    response = requests.get('http://localhost:8080/', timeout=5)
    if response.status_code == 200:
        print("✅ Application is healthy")
        sys.exit(0)
    else:
        print(f"❌ Application returned {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Health check failed: {e}")
    sys.exit(1)
```

---

## Updating the Application

### Pull Latest Changes:

```bash
cd /var/www/pdfremediator
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart pdfremediator
```

### Zero-Downtime Updates (with Gunicorn):

```bash
# Gunicorn supports graceful reload
sudo systemctl reload pdfremediator
```

---

## Troubleshooting

### Common Issues:

1. **Playwright not working:**
```bash
# Reinstall Playwright with system dependencies
playwright install --with-deps chromium
```

2. **Permission errors:**
```bash
sudo chown -R www-data:www-data /var/www/pdfremediator
sudo chmod -R 755 /var/www/pdfremediator
```

3. **Port already in use:**
```bash
# Find process using port 8080
sudo lsof -i :8080
# Kill if necessary
sudo kill -9 PID
```

4. **Large PDF timeouts:**
Increase timeout in Gunicorn and Nginx (see configurations above)

---

## Quick Comparison

| Option | Best For | Setup Time | Cost | Maintenance |
|--------|----------|------------|------|-------------|
| Local Network | Small team, same network | 10 min | Free | Low |
| Production Server | Organization-wide | 1-2 hours | $30-50/mo | Medium |
| Docker | Any environment | 30 min | Variable | Low |
| Heroku | Quick cloud deploy | 20 min | $7-25/mo | Very Low |
| AWS/Azure | Enterprise | 2-4 hours | $50+/mo | Medium-High |

---

## Recommended Approach

**For ASU Team:**
1. **Start:** Local network deployment (Option 1)
2. **Scale:** ASU internal hosting (Option 5)
3. **Alternative:** Docker on ASU infrastructure (Option 3)

This gives you instant access while working toward a permanent solution through ASU IT.
