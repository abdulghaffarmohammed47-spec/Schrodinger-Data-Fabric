# SDF v10 Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Security Hardening](#security-hardening)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Disaster Recovery](#backup--disaster-recovery)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS 11+, or Windows with WSL2
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 50GB free space minimum

### Software Requirements

- Python 3.11+
- Node.js 18+
- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 15+
- Redis 7+
- Git

### Installation

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip nodejs npm docker.io docker-compose postgresql-15 redis-server

# macOS
brew install python@3.11 node postgresql redis docker

# Verify installations
python3 --version
node --version
docker --version
docker-compose --version
```

---

## Local Development

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/sdf-v10.git
cd sdf-v10
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 6. Initialize Database

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database
createdb sdf_v10
psql sdf_v10 < schema.sql
```

### 7. Start Services

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Redis:**
```bash
redis-server
```

Access the application at `http://localhost:3000`

---

## Docker Deployment

### 1. Build Images

```bash
docker-compose build
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Verify Services

```bash
docker-compose ps
```

### 4. View Logs

```bash
docker-compose logs -f sdf-backend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### 5. Access Services

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

---

## Production Deployment

### 1. Pre-Deployment Checklist

- [ ] SSL/TLS certificates obtained
- [ ] Database backups configured
- [ ] Monitoring and alerting set up
- [ ] Security audit completed
- [ ] Load balancer configured
- [ ] CDN configured (if applicable)
- [ ] DNS records updated
- [ ] Firewall rules configured

### 2. Environment Configuration

```bash
# Create production .env
cp .env.example .env.production

# Edit with production values
ENVIRONMENT=production
DEBUG=false
ALLOWED_HOSTS=sdf-v10.example.com
DATABASE_URL=postgresql://user:password@prod-db:5432/sdf_v10
REDIS_URL=redis://prod-redis:6379
SECRET_KEY=<generate-secure-key>
```

### 3. SSL/TLS Setup

```bash
# Using Let's Encrypt with Certbot
sudo certbot certonly --standalone -d sdf-v10.example.com

# Copy certificates to config directory
sudo cp /etc/letsencrypt/live/sdf-v10.example.com/fullchain.pem config/ssl/
sudo cp /etc/letsencrypt/live/sdf-v10.example.com/privkey.pem config/ssl/
```

### 4. Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace sdf-v10

# Create secrets
kubectl create secret generic sdf-secrets \
  --from-literal=database-url=$DATABASE_URL \
  --from-literal=redis-url=$REDIS_URL \
  -n sdf-v10

# Deploy
kubectl apply -f k8s/ -n sdf-v10

# Verify deployment
kubectl get pods -n sdf-v10
```

### 5. Load Balancer Configuration

```nginx
# Nginx example
upstream sdf_backend {
    server sdf-backend-1:8000;
    server sdf-backend-2:8000;
    server sdf-backend-3:8000;
}

server {
    listen 443 ssl http2;
    server_name sdf-v10.example.com;

    ssl_certificate /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/private/privkey.pem;

    location /api {
        proxy_pass http://sdf_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://sdf_frontend;
    }
}
```

---

## Security Hardening

### 1. Database Security

```sql
-- Create restricted user
CREATE USER sdf_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE sdf_v10 TO sdf_user;
GRANT USAGE ON SCHEMA public TO sdf_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO sdf_user;

-- Enable SSL
ssl = on
ssl_cert_file = '/etc/postgresql/server.crt'
ssl_key_file = '/etc/postgresql/server.key'
```

### 2. Redis Security

```bash
# Enable authentication
requirepass secure_redis_password

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
```

### 3. Firewall Rules

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 80/tcp    # HTTP
sudo ufw enable
```

### 4. API Security

```python
# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login_user(request: Request):
    pass
```

### 5. CORS Configuration

```python
# Restrict CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sdf-v10.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## Monitoring & Logging

### 1. Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'sdf-backend'
    static_configs:
      - targets: ['localhost:8000']

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
```

### 2. Grafana Dashboards

Import pre-built dashboards:
- SDF Security Dashboard (ID: 12345)
- PostgreSQL Dashboard (ID: 9628)
- Redis Dashboard (ID: 11114)

### 3. Centralized Logging

```bash
# ELK Stack setup
docker run -d --name elasticsearch docker.elastic.co/elasticsearch/elasticsearch:8.0.0
docker run -d --name kibana docker.elastic.co/kibana/kibana:8.0.0
docker run -d --name logstash docker.elastic.co/logstash/logstash:8.0.0
```

### 4. Alerting Rules

```yaml
# alert.rules.yml
groups:
  - name: sdf_alerts
    rules:
      - alert: HighAnomalyScore
        expr: sdf_anomaly_score > 0.8
        for: 5m
        annotations:
          summary: "High anomaly score detected"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        annotations:
          summary: "PostgreSQL database is down"
```

---

## Backup & Disaster Recovery

### 1. Database Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/sdf-v10"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump sdf_v10 | gzip > $BACKUP_DIR/sdf_v10_$DATE.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/sdf_v10_$DATE.sql.gz s3://sdf-backups/
```

### 2. Redis Backups

```bash
# Redis RDB backup
redis-cli BGSAVE

# Copy RDB file
cp /var/lib/redis/dump.rdb /backups/redis_$(date +%Y%m%d).rdb
```

### 3. Disaster Recovery Plan

```
Recovery Time Objective (RTO): 1 hour
Recovery Point Objective (RPO): 15 minutes

Steps:
1. Restore database from latest backup
2. Restore Redis cache
3. Restart application services
4. Verify system health
5. Notify stakeholders
```

---

## Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection string
psql $DATABASE_URL -c "SELECT 1"
```

**2. Redis Connection Error**
```bash
# Check Redis status
redis-cli ping

# Check Redis logs
tail -f /var/log/redis/redis-server.log
```

**3. API Not Responding**
```bash
# Check API logs
docker-compose logs sdf-backend

# Check port availability
netstat -tlnp | grep 8000
```

**4. High Memory Usage**
```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart
```

**5. SSL Certificate Issues**
```bash
# Verify certificate
openssl x509 -in /etc/ssl/certs/fullchain.pem -text -noout

# Renew certificate
sudo certbot renew --force-renewal
```

### Debug Mode

```bash
# Enable debug logging
DEBUG=true
LOG_LEVEL=DEBUG

# Run with verbose output
python -m uvicorn main:app --log-level debug
```

---

## Performance Tuning

### 1. Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_user_id ON files(owner_id);
CREATE INDEX idx_created_at ON files(created_at);
CREATE INDEX idx_event_timestamp ON audit_events(timestamp);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM files WHERE owner_id = 'user_id';
```

### 2. Redis Optimization

```
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 3. API Optimization

```python
# Enable caching
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

@app.get("/api/v1/files")
@cached(namespace="files", expire=300)
async def get_files():
    pass
```

---

## Support & Documentation

- **Documentation**: https://docs.sdf-v10.io
- **Issue Tracker**: https://github.com/yourusername/sdf-v10/issues
- **Email Support**: support@sdf-v10.io
- **Slack Community**: https://sdf-v10.slack.com
