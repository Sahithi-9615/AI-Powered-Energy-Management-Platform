# 🚀 Deployment Guide - Smart Energy Platform

This guide covers multiple deployment options for your Smart Energy Analysis platform.

## 📋 Table of Contents
1. [Local Development](#local-development)
2. [Heroku Deployment](#heroku-deployment)
3. [PythonAnywhere Deployment](#pythonanywhere-deployment)
4. [AWS EC2 Deployment](#aws-ec2-deployment)
5. [Google Cloud Platform](#google-cloud-platform)
6. [Docker Deployment](#docker-deployment)

---

## 🏠 Local Development

### Quick Start
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

Access at: `http://localhost:5000`

---

## ☁️ Heroku Deployment

### Prerequisites
- Heroku account
- Heroku CLI installed
- Git installed

### Step 1: Prepare Files

Create `Procfile`:
```
web: gunicorn app:app
```

Update `requirements.txt`:
```
# Add to existing requirements
gunicorn==21.2.0
```

### Step 2: Initialize Git (if not done)
```bash
git init
git add .
git commit -m "Initial commit"
```

### Step 3: Create Heroku App
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-energy-app-name

# Set environment variables
heroku config:set GEMINI_API_KEY=your_api_key_here
heroku config:set SECRET_KEY=your_secret_key_here
```

### Step 4: Deploy
```bash
git push heroku main
```

### Step 5: Open App
```bash
heroku open
```

### Troubleshooting Heroku
```bash
# View logs
heroku logs --tail

# Restart app
heroku restart

# Check dynos
heroku ps
```

---

## 🐍 PythonAnywhere Deployment

### Step 1: Upload Files
1. Sign up at [PythonAnywhere](https://www.pythonanywhere.com/)
2. Go to Files → Upload files
3. Upload all project files

### Step 2: Create Virtual Environment
```bash
# In PythonAnywhere Bash console
cd ~
virtualenv --python=python3.9 venv
source venv/bin/activate
cd ~/your-project-folder
pip install -r requirements.txt
```

### Step 3: Configure Web App
1. Go to Web → Add a new web app
2. Choose Manual configuration → Python 3.9
3. Edit WSGI file:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/smart_energy_app'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['GEMINI_API_KEY'] = 'your_api_key_here'

# Import Flask app
from app import app as application
```

4. Set virtual environment path: `/home/yourusername/venv`
5. Reload web app

### Step 4: Access
Visit: `yourusername.pythonanywhere.com`

---

## 🌐 AWS EC2 Deployment

### Step 1: Launch EC2 Instance
1. Choose Ubuntu Server 22.04 LTS
2. Instance type: t2.micro (free tier)
3. Configure security group:
   - Allow HTTP (port 80)
   - Allow HTTPS (port 443)
   - Allow Custom TCP (port 5000) for testing

### Step 2: Connect and Setup
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv nginx -y

# Clone or upload project
git clone your-repo-url
# or use scp to upload files

cd smart_energy_app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Setup Gunicorn
```bash
pip install gunicorn

# Test
gunicorn --bind 0.0.0.0:5000 app:app
```

### Step 4: Create Systemd Service
```bash
sudo nano /etc/systemd/system/energy-app.service
```

Add:
```ini
[Unit]
Description=Smart Energy Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/smart_energy_app
Environment="PATH=/home/ubuntu/smart_energy_app/venv/bin"
ExecStart=/home/ubuntu/smart_energy_app/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl start energy-app
sudo systemctl enable energy-app
sudo systemctl status energy-app
```

### Step 5: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/energy-app
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/energy-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🐳 Docker Deployment

### Step 1: Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:app"]
```

### Step 2: Create docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./model.pkl:/app/model.pkl
      - ./reviews.json:/app/reviews.json
```

### Step 3: Build and Run
```bash
# Build image
docker build -t smart-energy-app .

# Run container
docker run -p 5000:5000 \
  -e GEMINI_API_KEY=your_key \
  smart-energy-app

# Or use docker-compose
docker-compose up -d
```

---

## 🔐 Security Checklist

Before deploying to production:

- [ ] Change SECRET_KEY to a strong random value
- [ ] Set FLASK_ENV=production
- [ ] Disable DEBUG mode
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS with SSL certificate
- [ ] Implement rate limiting
- [ ] Add authentication for admin features
- [ ] Sanitize all user inputs
- [ ] Keep dependencies updated
- [ ] Regular security audits

---

## 📊 Monitoring

### Application Monitoring
```python
# Add to app.py
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Health Check Endpoint
```python
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })
```

---

## 🔧 Environment Variables

Required for production:

```bash
# Gemini API
export GEMINI_API_KEY="your_gemini_key"

# Flask
export FLASK_ENV="production"
export SECRET_KEY="your_secret_key"

# Database (if added)
export DATABASE_URL="your_database_url"
```

---

## 📞 Support

For deployment issues:
1. Check logs first
2. Verify all dependencies are installed
3. Ensure model.pkl is accessible
4. Check firewall/security group settings
5. Verify environment variables are set

---

## 🎉 Post-Deployment

After successful deployment:

1. ✅ Test all features
2. 📊 Setup monitoring
3. 🔒 Configure backups
4. 📈 Setup analytics (optional)
5. 🚀 Announce launch!

**Congratulations on deploying your Smart Energy Platform! 🎊**
