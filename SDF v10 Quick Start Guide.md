# SDF v10 Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Docker & Docker Compose installed
- 8GB RAM available
- 10GB disk space

### Step 1: Clone & Setup

```bash
git clone https://github.com/yourusername/sdf-v10.git
cd sdf-v10
```

### Step 2: Start Services

```bash
docker-compose up -d
```

### Step 3: Verify Installation

```bash
# Check all services are running
docker-compose ps

# Test API health
curl http://localhost:8000/api/v1/health
```

### Step 4: Access Dashboards

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

---

## 📋 First Steps

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'
```

### 3. Upload a File

```bash
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "file=@/path/to/file.txt" \
  -F "user_id=<user_id>" \
  -F "session_id=<session_id>"
```

### 4. Generate Decoy Data

```bash
curl -X POST http://localhost:8000/api/v1/security/decoys/generate \
  -H "Content-Type: application/json" \
  -d '{
    "decoy_type": "financial",
    "session_id": "<session_id>"
  }'
```

### 5. Check Threat Intelligence

```bash
curl http://localhost:8000/api/v1/security/threats/feed?limit=10
```

---

## 🔍 Key Features Demo

### Anomaly Detection

The system automatically detects unusual access patterns:

```bash
# Access file (normal)
curl http://localhost:8000/api/v1/files/file_id?user_id=user&session_id=session

# System analyzes:
# - Time of access
# - Geographic location
# - Device fingerprint
# - Access frequency
# - Behavioral patterns
```

### Deception Engine

When threats are detected, the system serves fake data:

```bash
# High threat score → Decoy data returned
# Attacker gets realistic but fake data
# No indication of failure
# Stolen data is unreliable
```

### Threat Intelligence

Real-time threat tracking and coordination detection:

```bash
# Get threat score for IP
curl http://localhost:8000/api/v1/security/threats/score/192.168.1.100

# Detect coordinated attacks
curl http://localhost:8000/api/v1/security/threats/coordinated?threshold=3
```

---

## 📊 Monitoring

### Grafana Dashboards

1. **Login**: http://localhost:3000 (admin/admin)
2. **Add Data Source**: Prometheus (http://prometheus:9090)
3. **Import Dashboards**:
   - SDF Security Dashboard
   - System Performance
   - Threat Intelligence

### Key Metrics

- `sdf_files_uploaded_total` - Total files uploaded
- `sdf_anomalies_detected_total` - Total anomalies detected
- `sdf_threats_blocked_total` - Total threats blocked
- `sdf_decoy_data_served_total` - Decoy data served
- `sdf_api_latency_ms` - API response latency

---

## 🔐 Security Features

### Encryption

- **Algorithm**: ChaCha20-Poly1305 (authenticated encryption)
- **Key Size**: 256-bit
- **Key Derivation**: Argon2id with 64MB memory

### File Sharding

- **Method**: Shamir's Secret Sharing (3-of-5)
- **Distribution**: Across multiple regions
- **Integrity**: Merkle tree verification

### Anomaly Detection

- **Methods**: LSTM + Isolation Forest + Graph Analysis
- **Features**: 10 behavioral signals
- **Real-time**: <50ms detection latency

### Deception

- **Decoy Types**: 7 (financial, email, logs, database, credentials, documents, metrics)
- **Realism**: Generated with Faker library
- **Transparency**: No indication of failure to attacker

---

## 🛠️ Common Tasks

### View Logs

```bash
# Backend logs
docker-compose logs -f sdf-backend

# Database logs
docker-compose logs -f postgres

# Redis logs
docker-compose logs -f redis
```

### Stop Services

```bash
docker-compose down
```

### Restart Services

```bash
docker-compose restart
```

### Clean Up

```bash
# Remove containers
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it sdf-v10-db psql -U sdf_user -d sdf_v10

# View tables
\dt

# Query data
SELECT * FROM audit_events LIMIT 10;
```

---

## 📚 API Examples

### Authentication Flow

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "user@example.com",
    "password": "secure_password"
})
user_id = response.json()["user_id"]

# 2. Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "user@example.com",
    "password": "secure_password"
})
session_id = response.json()["session_id"]

# 3. Upload file
with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {"user_id": user_id, "session_id": session_id}
    response = requests.post(f"{BASE_URL}/files/upload", files=files, data=data)
    file_id = response.json()["file_id"]

# 4. Access file
response = requests.get(
    f"{BASE_URL}/files/{file_id}",
    params={"user_id": user_id, "session_id": session_id}
)

# 5. Get anomaly results
response = requests.get(
    f"{BASE_URL}/security/anomalies",
    params={"session_id": session_id}
)
```

### Threat Intelligence

```python
# Get threat feed
response = requests.get(f"{BASE_URL}/security/threats/feed?limit=50")
threats = response.json()["threat_feed"]

# Get threat score
response = requests.get(
    f"{BASE_URL}/security/threats/score/192.168.1.100"
)
threat_score = response.json()["threat_score"]

# Detect coordinated attacks
response = requests.get(
    f"{BASE_URL}/security/threats/coordinated?threshold=3"
)
coordinated = response.json()["coordinated_attacks"]
```

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check Docker daemon
docker ps

# Check port conflicts
netstat -tlnp | grep 8000
netstat -tlnp | grep 5432

# Restart Docker
sudo systemctl restart docker
```

### Database Connection Error

```bash
# Check PostgreSQL status
docker-compose logs postgres

# Recreate database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec postgres psql -U sdf_user -d sdf_v10 -f schema.sql
```

### High Memory Usage

```bash
# Check memory
docker stats

# Restart services
docker-compose restart

# Check logs for memory leaks
docker-compose logs sdf-backend | grep -i memory
```

### API Not Responding

```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Check logs
docker-compose logs -f sdf-backend

# Restart API
docker-compose restart sdf-backend
```

---

## 📖 Next Steps

1. **Read Full Documentation**: See `README.md`
2. **Deployment Guide**: See `DEPLOYMENT.md`
3. **Architecture Details**: See `SDF_v10_ARCHITECTURE.md`
4. **API Documentation**: Visit http://localhost:8000/docs

---

## 🆘 Support

- **Issues**: https://github.com/yourusername/sdf-v10/issues
- **Discussions**: https://github.com/yourusername/sdf-v10/discussions
- **Email**: support@sdf-v10.io
- **Slack**: https://sdf-v10.slack.com

---

**Happy securing! 🔐**
