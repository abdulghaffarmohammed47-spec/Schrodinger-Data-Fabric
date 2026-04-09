from fastapi import FastAPI, UploadFile, File, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import json
import uuid
from typing import List
from .models import User, FileMetadata, AccessLog
from .crypto_utils import generate_key_pair, encrypt_aes_key, decrypt_aes_key, encrypt_shard, decrypt_shard, split_file, join_shards
from .anomaly_engine import AnomalyEngine, extract_features

app = FastAPI(title="Schrödinger Data Fabric (SDF) API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines and storage
anomaly_engine = AnomalyEngine()
DATA_DIR = "data"
SHARD_DIR = os.path.join(DATA_DIR, "shards")
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")

os.makedirs(SHARD_DIR, exist_ok=True)

# Helper functions for storage
def load_json(file_path, default=[]):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return default

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

@app.post("/register")
async def register_user(user: User):
    users = load_json(USERS_FILE, {})
    users[user.uid] = user.dict()
    save_json(USERS_FILE, users)
    return {"status": "success", "message": f"User {user.uid} registered"}

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...), user_uid: str = None):
    if not user_uid:
        raise HTTPException(status_code=400, detail="User UID required")
    
    users = load_json(USERS_FILE, {})
    if user_uid not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Read file content
    content = await file.read()
    
    # Encryption and Sharding
    aes_key = os.urandom(32)
    shards = split_file(content, shard_count=5)
    
    file_id = str(uuid.uuid4())
    shard_paths = []
    
    for i, shard in enumerate(shards):
        enc_shard = encrypt_shard(shard, aes_key)
        shard_filename = f"{file_id}_shard_{i}.enc"
        shard_path = os.path.join(SHARD_DIR, shard_filename)
        with open(shard_path, 'w') as f:
            f.write(enc_shard)
        shard_paths.append(shard_path)
    
    # Encrypt AES key with user's public key
    public_key = users[user_uid]['public_key']
    enc_aes_key = encrypt_aes_key(aes_key, public_key)
    
    # Store metadata
    metadata = FileMetadata(
        file_id=file_id,
        owner_uid=user_uid,
        filename=file.filename,
        shard_count=len(shards),
        encrypted_aes_key=enc_aes_key,
        timestamp=time.time()
    )
    
    all_metadata = load_json(METADATA_FILE, {})
    all_metadata[file_id] = metadata.dict()
    save_json(METADATA_FILE, all_metadata)
    
    return {"status": "success", "file_id": file_id}

@app.get("/access/{file_id}")
async def access_file(request: Request, file_id: str, user_uid: str, private_key: str = None):
    # Anomaly Detection
    request_info = {
        "timestamp": time.time(),
        "ip": request.client.host,
        "user_agent": request.headers.get("user-agent", ""),
        "endpoint": "access"
    }
    
    features = extract_features(request_info)
    is_anomaly, score = anomaly_engine.predict(features)
    
    # Log access
    log = AccessLog(
        file_id=file_id,
        user_uid=user_uid,
        ip_address=request_info['ip'],
        user_agent=request_info['user_agent'],
        timestamp=request_info['timestamp'],
        anomaly_score=score,
        is_anomaly=is_anomaly
    )
    all_logs = load_json(LOGS_FILE, [])
    all_logs.append(log.dict())
    save_json(LOGS_FILE, all_logs)
    
    if is_anomaly:
        # Return decoy data
        decoy_data = {
            "status": "warning",
            "message": "Access patterns detected as anomalous. Providing decoy data.",
            "data": "DECOY_CONTENT_PROTECTED_BY_SDF"
        }
        return JSONResponse(content=decoy_data, status_code=200)
    
    # Real access flow
    all_metadata = load_json(METADATA_FILE, {})
    if file_id not in all_metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    metadata = all_metadata[file_id]
    if metadata['owner_uid'] != user_uid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not private_key:
        raise HTTPException(status_code=400, detail="Private key required for decryption")
    
    try:
        aes_key = decrypt_aes_key(metadata['encrypted_aes_key'], private_key)
        
        shards = []
        for i in range(metadata['shard_count']):
            shard_filename = f"{file_id}_shard_{i}.enc"
            shard_path = os.path.join(SHARD_DIR, shard_filename)
            with open(shard_path, 'r') as f:
                enc_shard = f.read()
            shards.append(decrypt_shard(enc_shard, aes_key))
        
        content = join_shards(shards)
        return {"status": "success", "filename": metadata['filename'], "content": content.decode('utf-8', errors='ignore')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")

@app.get("/admin/logs")
async def get_logs():
    return load_json(LOGS_FILE, [])

@app.get("/admin/stats")
async def get_stats():
    logs = load_json(LOGS_FILE, [])
    files = load_json(METADATA_FILE, {})
    users = load_json(USERS_FILE, {})
    
    return {
        "total_files": len(files),
        "total_users": len(users),
        "total_access_requests": len(logs),
        "anomaly_count": sum(1 for log in logs if log['is_anomaly'])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
