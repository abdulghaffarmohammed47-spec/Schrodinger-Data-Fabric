"""
Advanced Anomaly Detection Engine for SDF v10
Implements LSTM-based sequence modeling, Isolation Forest, and graph-based detection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import json
import pickle
from pathlib import Path

from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn


class LSTMAnomalyDetector(nn.Module):
    """LSTM-based anomaly detector for behavioral sequences"""
    
    def __init__(self, input_size: int = 10, hidden_size: int = 64, num_layers: int = 2):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """Forward pass through LSTM"""
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]
        output = self.fc(last_hidden)
        return output


class BehavioralProfiler:
    """Build and maintain user behavioral profiles"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.scaler = StandardScaler()
    
    def extract_features(self, access_log: Dict[str, Any]) -> List[float]:
        """
        Extract behavioral features from access log
        
        Features:
        1. Hour of day (0-23)
        2. Day of week (0-6)
        3. Request frequency (requests per minute)
        4. File size accessed (normalized)
        5. Access duration (seconds)
        6. IP geolocation distance from last access (km)
        7. Device fingerprint entropy
        8. Request pattern regularity (0-1)
        9. Time since last access (minutes)
        10. Concurrent sessions count
        """
        timestamp = datetime.fromisoformat(access_log["timestamp"])
        
        features = [
            timestamp.hour,
            timestamp.weekday(),
            access_log.get("request_frequency", 1.0),
            min(access_log.get("file_size", 0) / 1e9, 10.0),  # Normalize to 0-10
            access_log.get("access_duration", 0),
            access_log.get("geo_distance", 0),
            access_log.get("device_entropy", 0.5),
            access_log.get("pattern_regularity", 0.5),
            access_log.get("time_since_last", 60),
            access_log.get("concurrent_sessions", 1)
        ]
        
        return features
    
    def update_profile(self, user_id: str, features: List[float]):
        """Update user behavioral profile"""
        if user_id not in self.profiles:
            self.profiles[user_id] = {
                "feature_history": [],
                "mean": None,
                "std": None,
                "last_updated": datetime.utcnow().isoformat()
            }
        
        profile = self.profiles[user_id]
        profile["feature_history"].append(features)
        
        # Keep only recent history
        if len(profile["feature_history"]) > self.window_size:
            profile["feature_history"] = profile["feature_history"][-self.window_size:]
        
        # Update statistics
        if len(profile["feature_history"]) >= 10:
            features_array = np.array(profile["feature_history"])
            profile["mean"] = features_array.mean(axis=0).tolist()
            profile["std"] = features_array.std(axis=0).tolist()
        
        profile["last_updated"] = datetime.utcnow().isoformat()
    
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user behavioral profile"""
        return self.profiles.get(user_id)


class StatisticalAnomalyDetector:
    """Statistical anomaly detection using Isolation Forest and LOF"""
    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.isolation_forest = IsolationForest(contamination=contamination, random_state=42)
        self.lof = LocalOutlierFactor(n_neighbors=20, contamination=contamination)
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def train(self, training_data: np.ndarray):
        """Train anomaly detectors on normal behavior"""
        scaled_data = self.scaler.fit_transform(training_data)
        self.isolation_forest.fit(scaled_data)
        self.lof.fit(scaled_data)
        self.is_fitted = True
    
    def predict(self, features: np.ndarray) -> Tuple[bool, float]:
        """
        Predict if features represent anomaly
        
        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        if not self.is_fitted:
            return False, 0.0
        
        scaled_features = self.scaler.transform(features.reshape(1, -1))
        
        # Isolation Forest prediction
        if_score = self.isolation_forest.decision_function(scaled_features)[0]
        if_anomaly = self.isolation_forest.predict(scaled_features)[0] == -1
        
        # LOF prediction
        lof_score = self.lof.decision_function(scaled_features)[0]
        lof_anomaly = self.lof.predict(scaled_features)[0] == -1
        
        # Ensemble decision
        is_anomaly = if_anomaly or lof_anomaly
        
        # Normalize scores to 0-1 range
        anomaly_score = (1 + if_score) / 2  # Convert from [-1, 1] to [0, 1]
        anomaly_score = max(0, min(1, anomaly_score))
        
        return is_anomaly, anomaly_score


class GraphBasedDetector:
    """Graph-based anomaly detection for access patterns"""
    
    def __init__(self):
        self.user_file_graph: Dict[str, set] = {}
        self.file_access_patterns: Dict[str, Dict[str, int]] = {}
        self.access_history: List[Dict[str, Any]] = []
    
    def record_access(self, user_id: str, file_id: str, timestamp: str):
        """Record file access in graph"""
        # Update user-file graph
        if user_id not in self.user_file_graph:
            self.user_file_graph[user_id] = set()
        self.user_file_graph[user_id].add(file_id)
        
        # Update file access patterns
        if file_id not in self.file_access_patterns:
            self.file_access_patterns[file_id] = {}
        
        if user_id not in self.file_access_patterns[file_id]:
            self.file_access_patterns[file_id][user_id] = 0
        
        self.file_access_patterns[file_id][user_id] += 1
        
        # Record access
        self.access_history.append({
            "user_id": user_id,
            "file_id": file_id,
            "timestamp": timestamp
        })
    
    def detect_access_anomaly(self, user_id: str, file_id: str) -> Tuple[bool, float]:
        """
        Detect anomalies in access patterns
        
        Anomalies include:
        - Access to files outside user's normal pattern
        - Unusual access frequency
        - Access to sensitive files by new users
        """
        if user_id not in self.user_file_graph:
            return False, 0.0
        
        user_files = self.user_file_graph[user_id]
        
        # Check if file is in user's normal access pattern
        if file_id not in user_files:
            # New file access - check if it's suspicious
            if file_id in self.file_access_patterns:
                # Calculate how many users access this file
                access_count = len(self.file_access_patterns[file_id])
                
                # If file is accessed by few users, it's more suspicious
                if access_count < 3:
                    return True, 0.8
            
            return True, 0.5
        
        # Check access frequency
        access_freq = self.file_access_patterns.get(file_id, {}).get(user_id, 0)
        
        # Calculate average access frequency for this file
        avg_freq = np.mean(list(self.file_access_patterns.get(file_id, {}).values())) if self.file_access_patterns.get(file_id) else 1
        
        if access_freq > avg_freq * 5:  # 5x normal frequency
            return True, 0.7
        
        return False, 0.1


class AnomalyDetectionEngine:
    """Main anomaly detection engine combining all methods"""
    
    def __init__(self):
        self.behavioral_profiler = BehavioralProfiler()
        self.statistical_detector = StatisticalAnomalyDetector()
        self.graph_detector = GraphBasedDetector()
        self.lstm_detector: Optional[LSTMAnomalyDetector] = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def initialize_lstm(self):
        """Initialize LSTM detector"""
        self.lstm_detector = LSTMAnomalyDetector().to(self.device)
    
    def train_statistical_detector(self, training_logs: List[Dict[str, Any]]):
        """Train statistical anomaly detectors"""
        features_list = []
        
        for log in training_logs:
            features = self.behavioral_profiler.extract_features(log)
            features_list.append(features)
        
        if features_list:
            training_data = np.array(features_list)
            self.statistical_detector.train(training_data)
    
    def detect_anomaly(self, access_log: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive anomaly detection
        
        Returns:
            Dictionary with anomaly scores from different detectors
        """
        user_id = access_log.get("user_id")
        file_id = access_log.get("file_id")
        
        # Extract features
        features = self.behavioral_profiler.extract_features(access_log)
        
        # Update profile
        self.behavioral_profiler.update_profile(user_id, features)
        
        # Statistical detection
        stat_anomaly, stat_score = self.statistical_detector.predict(np.array(features))
        
        # Graph-based detection
        graph_anomaly, graph_score = self.graph_detector.detect_access_anomaly(user_id, file_id)
        
        # Record access
        self.graph_detector.record_access(user_id, file_id, access_log.get("timestamp", datetime.utcnow().isoformat()))
        
        # Ensemble decision
        scores = [stat_score, graph_score]
        ensemble_score = np.mean(scores)
        
        # Determine if anomalous (threshold: 0.6)
        is_anomaly = ensemble_score > 0.6
        
        return {
            "is_anomaly": is_anomaly,
            "ensemble_score": float(ensemble_score),
            "statistical_score": float(stat_score),
            "graph_score": float(graph_score),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "file_id": file_id,
            "features": features
        }
    
    def save_model(self, path: str):
        """Save trained models to disk"""
        model_data = {
            "statistical_detector": {
                "scaler_mean": self.statistical_detector.scaler.mean_.tolist(),
                "scaler_scale": self.statistical_detector.scaler.scale_.tolist(),
            },
            "behavioral_profiles": self.behavioral_profiler.profiles,
            "graph_patterns": {
                "user_file_graph": {k: list(v) for k, v in self.graph_detector.user_file_graph.items()},
                "file_access_patterns": self.graph_detector.file_access_patterns
            }
        }
        
        with open(path, "w") as f:
            json.dump(model_data, f, indent=2)
    
    def load_model(self, path: str):
        """Load trained models from disk"""
        with open(path, "r") as f:
            model_data = json.load(f)
        
        # Restore scaler
        if "statistical_detector" in model_data:
            self.statistical_detector.scaler.mean_ = np.array(model_data["statistical_detector"]["scaler_mean"])
            self.statistical_detector.scaler.scale_ = np.array(model_data["statistical_detector"]["scaler_scale"])
        
        # Restore profiles
        self.behavioral_profiler.profiles = model_data.get("behavioral_profiles", {})
        
        # Restore graph patterns
        graph_data = model_data.get("graph_patterns", {})
        self.graph_detector.user_file_graph = {k: set(v) for k, v in graph_data.get("user_file_graph", {}).items()}
        self.graph_detector.file_access_patterns = graph_data.get("file_access_patterns", {})


# Export main engine
anomaly_engine = AnomalyDetectionEngine()
