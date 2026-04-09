"""
Unit tests for deception engine and threat intelligence
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.security.deception_engine import (
    DeceptionEngine, DecoyType, ThreatIntelligence,
    AutoResponseEngine
)


class TestDeceptionEngine:
    """Test decoy data generation"""
    
    def test_generate_financial_decoy(self):
        """Test financial decoy generation"""
        engine = DeceptionEngine()
        decoy = engine.generate_financial_decoy()
        
        assert decoy["decoy_type"] == DecoyType.FINANCIAL
        assert "account_id" in decoy
        assert "account_holder" in decoy
        assert "balance" in decoy
        assert "transactions" in decoy
        assert len(decoy["transactions"]) > 0
    
    def test_generate_email_decoy(self):
        """Test email decoy generation"""
        engine = DeceptionEngine()
        decoy = engine.generate_email_decoy()
        
        assert decoy["decoy_type"] == DecoyType.EMAIL
        assert "mailbox_id" in decoy
        assert "owner" in decoy
        assert "emails" in decoy
        assert len(decoy["emails"]) > 0
    
    def test_generate_log_decoy(self):
        """Test log decoy generation"""
        engine = DeceptionEngine()
        decoy = engine.generate_log_decoy()
        
        assert decoy["decoy_type"] == DecoyType.LOGS
        assert "service_id" in decoy
        assert "environment" in decoy
        assert "logs" in decoy
        assert len(decoy["logs"]) > 0
    
    def test_generate_database_decoy(self):
        """Test database decoy generation"""
        engine = DeceptionEngine()
        decoy = engine.generate_database_decoy()
        
        assert decoy["decoy_type"] == DecoyType.DATABASE
        assert "database_id" in decoy
        assert "tables" in decoy
        assert "users" in decoy["tables"]
        assert "orders" in decoy["tables"]
        assert "products" in decoy["tables"]
    
    def test_generate_credentials_decoy(self):
        """Test credentials decoy generation"""
        engine = DeceptionEngine()
        decoy = engine.generate_credentials_decoy()
        
        assert decoy["decoy_type"] == DecoyType.CREDENTIALS
        assert "vault_id" in decoy
        assert "credentials" in decoy
        assert len(decoy["credentials"]) > 0
    
    def test_generate_document_decoy(self):
        """Test document decoy generation"""
        engine = DeceptionEngine()
        decoy = engine.generate_document_decoy()
        
        assert decoy["decoy_type"] == DecoyType.DOCUMENTS
        assert "repository_id" in decoy
        assert "documents" in decoy
        assert len(decoy["documents"]) > 0
    
    def test_generate_metrics_decoy(self):
        """Test metrics decoy generation"""
        engine = DeceptionEngine()
        decoy = engine.generate_metrics_decoy()
        
        assert decoy["decoy_type"] == DecoyType.METRICS
        assert "cluster_id" in decoy
        assert "metrics" in decoy
        assert len(decoy["metrics"]) > 0
    
    def test_generate_random_decoy(self):
        """Test random decoy generation"""
        engine = DeceptionEngine()
        decoy = engine.generate_decoy()
        
        assert "decoy_type" in decoy
        assert decoy["decoy_type"] in DecoyType
    
    def test_generate_specific_decoy(self):
        """Test specific decoy type generation"""
        engine = DeceptionEngine()
        decoy = engine.generate_decoy(DecoyType.FINANCIAL)
        
        assert decoy["decoy_type"] == DecoyType.FINANCIAL
    
    def test_cache_decoy(self):
        """Test decoy caching"""
        engine = DeceptionEngine()
        decoy = engine.generate_decoy()
        
        decoy_id = "test_decoy_123"
        engine.cache_decoy(decoy_id, decoy)
        
        cached = engine.get_cached_decoy(decoy_id)
        assert cached == decoy


class TestThreatIntelligence:
    """Test threat intelligence and attack tracking"""
    
    def test_record_attack(self):
        """Test attack recording"""
        ti = ThreatIntelligence()
        
        ti.record_attack(
            attacker_ip="192.168.1.100",
            target_ip="10.0.0.1",
            attack_type="brute_force",
            severity="high"
        )
        
        assert len(ti.threat_events) == 1
        assert "192.168.1.100" in ti.threat_graph
    
    def test_detect_coordinated_attack(self):
        """Test coordinated attack detection"""
        ti = ThreatIntelligence()
        
        # Record attacks from multiple IPs to same target
        for i in range(5):
            ti.record_attack(
                attacker_ip=f"192.168.1.{100+i}",
                target_ip="10.0.0.1",
                attack_type="sql_injection",
                severity="critical"
            )
        
        coordinated = ti.detect_coordinated_attack(threshold=3)
        assert len(coordinated) > 0
        assert coordinated[0]["target"] == "10.0.0.1"
        assert coordinated[0]["attacker_count"] >= 3
    
    def test_threat_score(self):
        """Test threat score calculation"""
        ti = ThreatIntelligence()
        
        attacker_ip = "192.168.1.100"
        
        # Record multiple attacks
        for i in range(5):
            ti.record_attack(
                attacker_ip=attacker_ip,
                target_ip=f"10.0.0.{i}",
                attack_type="brute_force",
                severity="high"
            )
        
        score = ti.get_threat_score(attacker_ip)
        assert 0 <= score <= 100
        assert score > 0  # Should have non-zero score after attacks
    
    def test_threat_feed(self):
        """Test threat feed generation"""
        ti = ThreatIntelligence()
        
        # Record multiple attacks
        for i in range(10):
            ti.record_attack(
                attacker_ip=f"192.168.1.{100+i}",
                target_ip="10.0.0.1",
                attack_type="ddos",
                severity="critical"
            )
        
        feed = ti.get_threat_feed(limit=5)
        assert len(feed) <= 5
        assert len(feed) > 0


class TestAutoResponseEngine:
    """Test automatic response engine"""
    
    def test_determine_response_low_threat(self):
        """Test response determination for low threat"""
        engine = AutoResponseEngine(DeceptionEngine())
        
        response = engine.determine_response(threat_score=10)
        assert response["action"] == "allow"
        assert response["decoy_enabled"] == False
    
    def test_determine_response_medium_threat(self):
        """Test response determination for medium threat"""
        engine = AutoResponseEngine(DeceptionEngine())
        
        response = engine.determine_response(threat_score=35)
        assert response["action"] == "monitor"
        assert response["decoy_enabled"] == False
    
    def test_determine_response_high_threat(self):
        """Test response determination for high threat"""
        engine = AutoResponseEngine(DeceptionEngine())
        
        response = engine.determine_response(threat_score=65)
        assert response["action"] == "decoy"
        assert response["decoy_enabled"] == True
    
    def test_determine_response_critical_threat(self):
        """Test response determination for critical threat"""
        engine = AutoResponseEngine(DeceptionEngine())
        
        response = engine.determine_response(threat_score=90)
        assert response["action"] == "block"
        assert response["decoy_enabled"] == False
    
    def test_execute_response(self):
        """Test response execution"""
        engine = AutoResponseEngine(DeceptionEngine())
        
        action = engine.execute_response(
            threat_score=65,
            user_id="attacker_user",
            resource_id="sensitive_file"
        )
        
        assert "action_id" in action
        assert "timestamp" in action
        assert action["user_id"] == "attacker_user"
        assert action["resource_id"] == "sensitive_file"
        assert action["action"] == "decoy"
    
    def test_execute_response_with_decoy(self):
        """Test response execution with decoy data"""
        engine = AutoResponseEngine(DeceptionEngine())
        
        action = engine.execute_response(
            threat_score=70,
            user_id="attacker",
            resource_id="file"
        )
        
        if action["action"] == "decoy":
            assert "decoy_id" in action
            assert "decoy_data" in action


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
