import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os
import time

MODEL_PATH = "data/anomaly_model.joblib"

class AnomalyEngine:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            self.train_initial_model()

    def train_initial_model(self):
        # Create some dummy data for initial training
        # Features: [hour_of_day, request_frequency, endpoint_id, context_score]
        # 0: upload, 1: access, 2: list, 3: delete
        np.random.seed(42)
        normal_data = np.random.normal(loc=[12, 5, 1, 0.5], scale=[4, 2, 0.5, 0.1], size=(100, 4))
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.model.fit(normal_data)
        os.makedirs("data", exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)

    def predict(self, features):
        if self.model is None:
            self.load_model()
        
        # Isolation Forest returns -1 for anomalies and 1 for normal
        prediction = self.model.predict([features])[0]
        # decision_function returns a score where lower values are more anomalous
        score = self.model.decision_function([features])[0]
        
        is_anomaly = prediction == -1
        # Normalize score to 0-1 range (approximate)
        normalized_score = 1 / (1 + np.exp(-score))
        
        return is_anomaly, normalized_score

    def train(self, data):
        # data should be a list of feature lists
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.model.fit(data)
        joblib.dump(self.model, MODEL_PATH)

def extract_features(request_info):
    # Features: [hour_of_day, request_frequency, endpoint_id, context_score]
    hour = time.localtime(request_info['timestamp']).tm_hour
    freq = request_info.get('frequency', 1)
    endpoint_map = {"upload": 0, "access": 1, "list": 2, "delete": 3}
    endpoint_id = endpoint_map.get(request_info['endpoint'], 1)
    
    # Simple context score based on IP and User-Agent length
    context_score = (len(request_info['ip']) + len(request_info['user_agent'])) / 200.0
    
    return [hour, freq, endpoint_id, context_score]
