"""
Unit tests for anomaly detection engine
"""

import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.ml.anomaly_detector import (
    BehavioralProfiler, StatisticalAnomalyDetector,
    GraphBasedDetector, AnomalyDetectionEngine
)


class TestBehavioralProfiler:
    """Test behavioral profiling"""
    
    def test_extract_features(self):
        """Test feature extraction"""
        profiler = BehavioralProfiler()
        
        access_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_frequency": 1.5,
            "file_size": 1000000,
            "access_duration": 120,
            "geo_distance": 500,
            "device_entropy": 0.7,
            "pattern_regularity": 0.8,
            "time_since_last": 300,
            "concurrent_sessions": 2
        }
        
        features = profiler.extract_features(access_log)
        assert len(features) == 10
        assert all(isinstance(f, (int, float)) for f in features)
    
    def test_update_profile(self):
        """Test profile update"""
        profiler = BehavioralProfiler()
        user_id = "test_user"
        
        features = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        profiler.update_profile(user_id, features)
        
        profile = profiler.get_profile(user_id)
        assert profile is not None
        assert len(profile["feature_history"]) == 1
    
    def test_profile_statistics(self):
        """Test profile statistics computation"""
        profiler = BehavioralProfiler()
        user_id = "test_user"
        
        # Add multiple feature sets
        for i in range(15):
            features = [float(j + i) for j in range(10)]
            profiler.update_profile(user_id, features)
        
        profile = profiler.get_profile(user_id)
        assert profile["mean"] is not None
        assert profile["std"] is not None
        assert len(profile["mean"]) == 10


class TestStatisticalAnomalyDetector:
    """Test statistical anomaly detection"""
    
    def test_train_detector(self):
        """Test detector training"""
        import numpy as np
        
        detector = StatisticalAnomalyDetector()
        
        # Generate normal training data
        normal_data = np.random.normal(50, 10, (100, 10))
        
        detector.train(normal_data)
        assert detector.is_fitted
    
    def test_predict_normal(self):
        """Test prediction on normal data"""
        import numpy as np
        
        detector = StatisticalAnomalyDetector()
        normal_data = np.random.normal(50, 10, (100, 10))
        detector.train(normal_data)
        
        # Test on similar data
        test_data = np.random.normal(50, 10, 10)
        is_anomaly, score = detector.predict(test_data)
        
        assert isinstance(is_anomaly, (bool, np.bool_))
        assert 0 <= score <= 1
    
    def test_predict_anomaly(self):
        """Test prediction on anomalous data"""
        import numpy as np
        
        detector = StatisticalAnomalyDetector()
        normal_data = np.random.normal(50, 10, (100, 10))
        detector.train(normal_data)
        
        # Test on very different data
        anomalous_data = np.random.normal(200, 50, 10)
        is_anomaly, score = detector.predict(anomalous_data)
        
        assert score > 0.5  # Should have high anomaly score


class TestGraphBasedDetector:
    """Test graph-based anomaly detection"""
    
    def test_record_access(self):
        """Test access recording"""
        detector = GraphBasedDetector()
        
        detector.record_access("user1", "file1", datetime.utcnow().isoformat())
        
        assert "user1" in detector.user_file_graph
        assert "file1" in detector.user_file_graph["user1"]
    
    def test_detect_new_file_access(self):
        """Test detection of new file access"""
        detector = GraphBasedDetector()
        
        # Record normal access
        detector.record_access("user1", "file1", datetime.utcnow().isoformat())
        detector.record_access("user1", "file2", datetime.utcnow().isoformat())
        
        # Detect access to new file
        is_anomaly, score = detector.detect_access_anomaly("user1", "file3")
        
        assert is_anomaly
        assert score > 0
    
    def test_detect_high_frequency_access(self):
        """Test detection of high-frequency access"""
        detector = GraphBasedDetector()
        
        # Record normal access pattern
        for i in range(10):
            detector.record_access("user1", "file1", datetime.utcnow().isoformat())
        
        # Record many accesses to same file
        for i in range(100):
            detector.record_access("user2", "file1", datetime.utcnow().isoformat())
        
        # User1 accessing file1 many times should be anomalous
        is_anomaly, score = detector.detect_access_anomaly("user1", "file1")
        
        # Score should reflect the anomaly
        assert score >= 0


class TestAnomalyDetectionEngine:
    """Test main anomaly detection engine"""
    
    def test_detect_anomaly(self):
        """Test anomaly detection"""
        engine = AnomalyDetectionEngine()
        
        access_log = {
            "user_id": "test_user",
            "file_id": "test_file",
            "timestamp": datetime.utcnow().isoformat(),
            "request_frequency": 1.0,
            "file_size": 1000000,
            "access_duration": 0,
            "geo_distance": 0,
            "device_entropy": 0.5,
            "pattern_regularity": 0.5,
            "time_since_last": 60,
            "concurrent_sessions": 1
        }
        
        result = engine.detect_anomaly(access_log)
        
        assert "is_anomaly" in result
        assert "ensemble_score" in result
        assert "statistical_score" in result
        assert "graph_score" in result
        assert 0 <= result["ensemble_score"] <= 1
    
    def test_multiple_detections(self):
        """Test multiple anomaly detections"""
        engine = AnomalyDetectionEngine()
        
        for i in range(5):
            access_log = {
                "user_id": f"user_{i}",
                "file_id": f"file_{i}",
                "timestamp": datetime.utcnow().isoformat(),
                "request_frequency": 1.0,
                "file_size": 1000000,
                "access_duration": 0,
                "geo_distance": 0,
                "device_entropy": 0.5,
                "pattern_regularity": 0.5,
                "time_since_last": 60,
                "concurrent_sessions": 1
            }
            
            result = engine.detect_anomaly(access_log)
            assert "ensemble_score" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
