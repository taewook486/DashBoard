# DashBoard Deployment Guide

**@SPEC:IMPROVE-001** - Deployment instructions for the modular DashBoard application

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Traditional Hosting](#traditional-hosting)
5. [Cloud Platforms](#cloud-platforms)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### Required Software

- **Python**: 3.11 or higher
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (optional)
- **Git**: For cloning the repository

### Required API Keys (Optional)

- **Google Gemini API Key**: For AI macro analysis
- **OpenAI API Key**: For AI stock summaries
- **FRED API Key**: For economic data

---

## Environment Configuration

### Step 1: Clone Repository

```bash
git clone https://github.com/taewook486/DashBoard.git
cd DashBoard
```

### Step 2: Create Environment File

```bash
cp .env.example .env
```

### Step 3: Configure Environment Variables

Edit `.env` with your configuration:

```env
# Flask Configuration
FLASK_ENV=production
PORT=5001
LOG_LEVEL=INFO

# API Keys (Optional)
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
FRED_API_KEY=your_fred_api_key_here

# Data Directory
DATA_DIR=./us_market/data

# Security
CORS_ENABLED=true
ALLOWED_ORIGINS=*
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100 per minute

# Feature Flags
ENABLE_AI_FEATURES=true
ENABLE_DATA_UPDATE=true
```

### Environment Variables Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `FLASK_ENV` | string | production | Flask environment mode |
| `PORT` | integer | 5001 | Application port |
| `LOG_LEVEL` | string | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `GOOGLE_API_KEY` | string | - | Google Gemini API key |
| `OPENAI_API_KEY` | string | - | OpenAI API key |
| `FRED_API_KEY` | string | - | FRED API key |
| `DATA_DIR` | string | ./us_market/data | Data directory path |
| `CORS_ENABLED` | boolean | true | Enable CORS |
| `ALLOWED_ORIGINS` | string | * | Allowed CORS origins |
| `RATE_LIMIT_ENABLED` | boolean | true | Enable rate limiting |
| `RATE_LIMIT_DEFAULT` | string | 100 per minute | Default rate limit |

---

## Docker Deployment

### Option 1: Docker Build

#### Build Image

```bash
docker build -t dashboard:latest .
```

#### Run Container

```bash
docker run -d \
  --name dashboard \
  -p 5001:5001 \
  --env-file .env \
  --restart unless-stopped \
  dashboard:latest
```

#### View Logs

```bash
docker logs -f dashboard
```

#### Stop Container

```bash
docker stop dashboard
docker rm dashboard
```

---

### Option 2: Docker Compose

#### Start Services

```bash
docker-compose up -d
```

#### View Logs

```bash
docker-compose logs -f
```

#### Stop Services

```bash
docker-compose down
```

#### Restart Services

```bash
docker-compose restart
```

---

### Docker Health Checks

The Dockerfile includes a built-in health check:

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' dashboard

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' dashboard
```

---

## Traditional Hosting

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

### Step 2: Set Environment Variables

```bash
export FLASK_ENV=production
export PORT=5001
export LOG_LEVEL=INFO

# Load from .env file
source .env  # Linux/Mac
# Or use: python-dotenv package
```

### Step 3: Run with Gunicorn

```bash
gunicorn --bind 0.0.0.0:5001 \
  --workers 2 \
  --threads 4 \
  --access-logfile - \
  --error-logfile - \
  "app:create_app()"
```

### Gunicorn Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `--workers` | 2 | Number of worker processes |
| `--threads` | 4 | Threads per worker |
| `--bind` | 0.0.0.0:5001 | Bind address |
| `--access-logfile` | - | Access log location (- for stdout) |
| `--error-logfile` | - | Error log location (- for stderr) |
| `--log-level` | info | Log level |
| `--timeout` | 30 | Request timeout (seconds) |

### Step 4: Systemd Service (Linux)

Create `/etc/systemd/system/dashboard.service`:

```ini
[Unit]
Description=DashBoard Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/DashBoard
Environment="PATH=/path/to/DashBoard/venv/bin"
EnvironmentFile=/path/to/DashBoard/.env
ExecStart=/path/to/DashBoard/venv/bin/gunicorn \
  --bind 0.0.0.0:5001 \
  --workers 2 \
  --threads 4 \
  "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl enable dashboard
sudo systemctl start dashboard
sudo systemctl status dashboard
```

---

## Cloud Platforms

### Render Deployment

#### Prerequisites

- GitHub repository with code
- Render account (free tier available)

#### Deployment Steps

1. **Connect Repository**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - **Name**: dashboard
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT "app:create_app()"`

3. **Environment Variables**
   - Add all variables from `.env` file
   - Render automatically sets `PORT` variable

4. **Deploy**
   - Click "Create Web Service"
   - Deployment starts automatically
   - Access at: `https://dashboard.onrender.com`

#### Automatic Deployments

- Render automatically deploys on push to main branch
- Preview deployments available for pull requests

---

### Railway Deployment

#### Prerequisites

- Railway account
- GitHub repository

#### Deployment Steps

1. **Start New Project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"

2. **Select Repository**
   - Choose your DashBoard repository
   - Select branch (main)

3. **Configure**
   - **Root Directory**: `.`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT "app:create_app()"`

4. **Environment Variables**
   - Add variables from `.env` file

5. **Deploy**
   - Click "Deploy"
   - Railway provides a temporary URL
   - Add custom domain in settings

---

### Vercel Deployment

#### Prerequisites

- Vercel account
- GitHub repository

#### Deployment Steps

1. **Install Vercel CLI**

```bash
npm install -g vercel
```

2. **Login**

```bash
vercel login
```

3. **Deploy**

```bash
vercel
```

4. **Configure**
   - Follow the interactive prompts
   - Set environment variables
   - Configure build settings

5. **Production Deployment**

```bash
vercel --prod
```

---

## Monitoring & Maintenance

### Health Checks

#### Check Health Endpoint

```bash
curl http://localhost:5001/health
```

#### Expected Response

```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "components": {
    "api": "healthy",
    "data": "healthy"
  }
}
```

### Log Monitoring

#### Docker Logs

```bash
# Follow logs
docker logs -f dashboard

# Last 100 lines
docker logs --tail 100 dashboard

# Specific time range
docker logs --since 1h dashboard
```

#### Gunicorn Logs

```bash
# Access logs
tail -f /var/log/dashboard/access.log

# Error logs
tail -f /var/log/dashboard/error.log
```

### Performance Monitoring

#### Basic Metrics

```bash
# Check memory usage
docker stats dashboard

# Check CPU usage
top -p $(pgrep -f dashboard)
```

#### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 http://localhost:5001/health
```

### Backup Strategy

#### Data Backup

```bash
# Backup data directory
tar -czf backup_$(date +%Y%m%d).tar.gz us_market/data/

# Upload to cloud storage (optional)
aws s3 cp backup_$(date +%Y%m%d).tar.gz s3://backups/
```

#### Database Backup (if applicable)

```bash
# Dump database
pg_dump dbname > backup_$(date +%Y%m%d).sql

# Restore
psql dbname < backup_20250115.sql
```

### Update Strategy

#### Zero-Downtime Deployment

```bash
# Pull latest changes
git pull origin main

# Build new image
docker build -t dashboard:latest .

# Stop old container
docker stop dashboard

# Start new container
docker run -d --name dashboard \
  -p 5001:5001 \
  --env-file .env \
  --restart unless-stopped \
  dashboard:latest

# Clean up old container
docker rm dashboard_old
```

---

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Check what's using the port
lsof -i :5001

# Kill the process
kill -9 $(lsof -t -i:5001)
```

#### Permission Denied

```bash
# Fix file permissions
chmod +x scripts/*.sh
chown -R www-data:www-data /path/to/DashBoard
```

#### Out of Memory

```bash
# Check memory usage
free -h

# Increase swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Dependencies Issues

```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

---

## Security Best Practices

1. **Use Environment Variables**: Never commit `.env` file
2. **Enable HTTPS**: Use SSL certificates in production
3. **Rate Limiting**: Keep rate limiting enabled
4. **CORS Configuration**: Restrict allowed origins
5. **Regular Updates**: Keep dependencies updated
6. **Monitoring**: Set up alerts for errors and downtime

---

## Support

For deployment issues:
- Check logs: `docker logs dashboard`
- Review configuration: `.env` file
- Check health: `/health` endpoint
- Open GitHub issue for support

---

**@SPEC:IMPROVE-001** - Modular Architecture Refactoring
