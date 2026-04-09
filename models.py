from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    uid: str
    email: str
    public_key: str

class FileMetadata(BaseModel):
    file_id: str
    owner_uid: str
    filename: str
    shard_count: int
    encrypted_aes_key: str
    timestamp: float

class AccessLog(BaseModel):
    file_id: str
    user_uid: str
    ip_address: str
    user_agent: str
    timestamp: float
    anomaly_score: float
    is_anomaly: bool
