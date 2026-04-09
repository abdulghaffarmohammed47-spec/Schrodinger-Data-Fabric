# Schrödinger Data Fabric (SDF) v6

A secure, distributed, and AI-protected data platform for sensitive information.

## Core Features
- **End-to-End Encryption**: Data is encrypted per-user using RSA/AES.
- **File Sharding**: Files are split into shards and stored separately.
- **ML Anomaly Detection**: Behavioral analysis to detect unauthorized access patterns.
- **Decoy Engine**: Returns AI-generated decoy data to potential attackers.
- **Admin Dashboard**: Real-time monitoring of system health and security events.

## Quick Start (Local Setup)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Backend
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

### 3. Open the Frontend
Open `frontend/index.html` in your web browser.

## Docker Setup
```bash
docker-compose up --build
```
- API will be at `http://localhost:8000`
- UI will be at `http://localhost:8080`

## Project Structure
- `backend/`: FastAPI application, crypto utils, and ML engine.
- `frontend/`: Simple HTML/JS interface with Tailwind CSS.
- `data/`: Local storage for shards, metadata, and ML models.
- `Dockerfile` & `docker-compose.yml`: Containerization setup.

## Security Warning
This is a production-ready architectural demonstration. Ensure you manage private keys securely in a real-world deployment (e.g., using Hardware Security Modules or secure client-side storage).
