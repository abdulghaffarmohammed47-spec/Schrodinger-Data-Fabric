"""
Deception Layer for SDF v10
Generates realistic fake data to confuse attackers and destroy incentives for data theft
"""

import json
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid
from faker import Faker


class DecoyType(str, Enum):
    """Types of decoy data"""
    FINANCIAL = "financial"
    EMAIL = "email"
    LOGS = "logs"
    DATABASE = "database"
    CREDENTIALS = "credentials"
    DOCUMENTS = "documents"
    METRICS = "metrics"


class DeceptionEngine:
    """Generate realistic decoy data to confuse attackers"""
    
    def __init__(self):
        self.faker = Faker()
        self.decoy_cache: Dict[str, Dict[str, Any]] = {}
    
    def generate_financial_decoy(self) -> Dict[str, Any]:
        """Generate realistic fake financial data"""
        transactions = []
        for _ in range(random.randint(50, 200)):
            transactions.append({
                "transaction_id": str(uuid.uuid4()),
                "timestamp": (datetime.utcnow() - timedelta(days=random.randint(0, 90))).isoformat(),
                "amount": round(random.uniform(10, 50000), 2),
                "currency": random.choice(["USD", "EUR", "GBP", "JPY"]),
                "merchant": self.faker.company(),
                "category": random.choice(["Travel", "Dining", "Shopping", "Utilities", "Healthcare"]),
                "status": random.choice(["completed", "pending", "cancelled"]),
                "account_last_4": str(random.randint(1000, 9999))
            })
        
        return {
            "decoy_type": DecoyType.FINANCIAL,
            "account_id": str(uuid.uuid4()),
            "account_holder": self.faker.name(),
            "balance": round(random.uniform(1000, 1000000), 2),
            "transactions": transactions,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def generate_email_decoy(self) -> Dict[str, Any]:
        """Generate realistic fake email archive"""
        emails = []
        for _ in range(random.randint(100, 500)):
            emails.append({
                "message_id": str(uuid.uuid4()),
                "from": self.faker.email(),
                "to": self.faker.email(),
                "subject": self.faker.sentence(),
                "timestamp": (datetime.utcnow() - timedelta(days=random.randint(0, 180))).isoformat(),
                "body": self.faker.paragraph(nb_sentences=random.randint(3, 10)),
                "attachments": random.randint(0, 3),
                "read": random.choice([True, False])
            })
        
        return {
            "decoy_type": DecoyType.EMAIL,
            "mailbox_id": str(uuid.uuid4()),
            "owner": self.faker.email(),
            "total_messages": len(emails),
            "emails": emails,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def generate_log_decoy(self) -> Dict[str, Any]:
        """Generate realistic fake application logs"""
        logs = []
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"]
        
        for _ in range(random.randint(500, 2000)):
            logs.append({
                "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(0, 1440))).isoformat(),
                "level": random.choice(log_levels),
                "service": random.choice(["auth-service", "api-gateway", "database", "cache", "queue"]),
                "message": self.faker.sentence(),
                "trace_id": str(uuid.uuid4()),
                "duration_ms": random.randint(1, 5000),
                "status_code": random.choice([200, 201, 400, 401, 403, 404, 500, 503])
            })
        
        return {
            "decoy_type": DecoyType.LOGS,
            "service_id": str(uuid.uuid4()),
            "environment": random.choice(["production", "staging", "development"]),
            "total_logs": len(logs),
            "logs": logs,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def generate_database_decoy(self) -> Dict[str, Any]:
        """Generate realistic fake database records"""
        tables = {}
        
        # Users table
        users = []
        for _ in range(random.randint(100, 500)):
            users.append({
                "id": uuid.uuid4().hex,
                "username": self.faker.user_name(),
                "email": self.faker.email(),
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat(),
                "last_login": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
                "status": random.choice(["active", "inactive", "suspended"])
            })
        tables["users"] = users
        
        # Orders table
        orders = []
        for _ in range(random.randint(500, 2000)):
            orders.append({
                "id": uuid.uuid4().hex,
                "user_id": random.choice(users)["id"],
                "amount": round(random.uniform(10, 10000), 2),
                "status": random.choice(["pending", "processing", "completed", "cancelled"]),
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 180))).isoformat()
            })
        tables["orders"] = orders
        
        # Products table
        products = []
        for _ in range(random.randint(50, 200)):
            products.append({
                "id": uuid.uuid4().hex,
                "name": self.faker.word(),
                "price": round(random.uniform(10, 1000), 2),
                "stock": random.randint(0, 1000),
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat()
            })
        tables["products"] = products
        
        return {
            "decoy_type": DecoyType.DATABASE,
            "database_id": str(uuid.uuid4()),
            "tables": tables,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def generate_credentials_decoy(self) -> Dict[str, Any]:
        """Generate realistic fake credentials (honeypot)"""
        credentials = []
        
        for _ in range(random.randint(20, 50)):
            credentials.append({
                "username": self.faker.user_name(),
                "email": self.faker.email(),
                "password_hash": uuid.uuid4().hex,
                "api_key": uuid.uuid4().hex,
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat(),
                "last_used": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
                "permissions": random.choice(["admin", "user", "guest"])
            })
        
        return {
            "decoy_type": DecoyType.CREDENTIALS,
            "vault_id": str(uuid.uuid4()),
            "credentials": credentials,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def generate_document_decoy(self) -> Dict[str, Any]:
        """Generate realistic fake documents"""
        documents = []
        
        for _ in range(random.randint(50, 200)):
            documents.append({
                "id": uuid.uuid4().hex,
                "title": self.faker.sentence(),
                "author": self.faker.name(),
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat(),
                "modified_at": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
                "size_bytes": random.randint(1000, 10000000),
                "content": self.faker.paragraph(nb_sentences=random.randint(5, 20)),
                "tags": [self.faker.word() for _ in range(random.randint(1, 5))],
                "access_level": random.choice(["public", "internal", "confidential", "restricted"])
            })
        
        return {
            "decoy_type": DecoyType.DOCUMENTS,
            "repository_id": str(uuid.uuid4()),
            "documents": documents,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def generate_metrics_decoy(self) -> Dict[str, Any]:
        """Generate realistic fake system metrics"""
        metrics = []
        
        for _ in range(random.randint(100, 500)):
            metrics.append({
                "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(0, 1440))).isoformat(),
                "metric_name": random.choice([
                    "cpu_usage", "memory_usage", "disk_usage", "network_io",
                    "request_latency", "error_rate", "throughput"
                ]),
                "value": round(random.uniform(0, 100), 2),
                "unit": random.choice(["%", "ms", "MB", "Mbps"]),
                "host": f"server-{random.randint(1, 100)}",
                "status": random.choice(["normal", "warning", "critical"])
            })
        
        return {
            "decoy_type": DecoyType.METRICS,
            "cluster_id": str(uuid.uuid4()),
            "metrics": metrics,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def generate_decoy(self, decoy_type: Optional[DecoyType] = None) -> Dict[str, Any]:
        """Generate decoy data of specified type or random type"""
        if decoy_type is None:
            decoy_type = random.choice(list(DecoyType))
        
        generators = {
            DecoyType.FINANCIAL: self.generate_financial_decoy,
            DecoyType.EMAIL: self.generate_email_decoy,
            DecoyType.LOGS: self.generate_log_decoy,
            DecoyType.DATABASE: self.generate_database_decoy,
            DecoyType.CREDENTIALS: self.generate_credentials_decoy,
            DecoyType.DOCUMENTS: self.generate_document_decoy,
            DecoyType.METRICS: self.generate_metrics_decoy
        }
        
        generator = generators.get(decoy_type)
        if not generator:
            raise ValueError(f"Unknown decoy type: {decoy_type}")
        
        return generator()
    
    def cache_decoy(self, decoy_id: str, decoy_data: Dict[str, Any]):
        """Cache decoy data for reuse"""
        self.decoy_cache[decoy_id] = decoy_data
    
    def get_cached_decoy(self, decoy_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached decoy data"""
        return self.decoy_cache.get(decoy_id)


class ThreatIntelligence:
    """Global threat intelligence and attack tracking"""
    
    def __init__(self):
        self.threat_events: List[Dict[str, Any]] = []
        self.threat_graph: Dict[str, set] = {}  # IP -> set of attacked IPs
        self.attacker_profiles: Dict[str, Dict[str, Any]] = {}
    
    def record_attack(self, attacker_ip: str, target_ip: str, attack_type: str, severity: str):
        """Record attack event for threat intelligence"""
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "attacker_ip": attacker_ip,
            "target_ip": target_ip,
            "attack_type": attack_type,
            "severity": severity,
            "status": "detected"
        }
        
        self.threat_events.append(event)
        
        # Update threat graph
        if attacker_ip not in self.threat_graph:
            self.threat_graph[attacker_ip] = set()
        self.threat_graph[attacker_ip].add(target_ip)
        
        # Update attacker profile
        if attacker_ip not in self.attacker_profiles:
            self.attacker_profiles[attacker_ip] = {
                "first_seen": datetime.utcnow().isoformat(),
                "attack_count": 0,
                "attack_types": set(),
                "targets": set(),
                "severity_levels": set()
            }
        
        profile = self.attacker_profiles[attacker_ip]
        profile["attack_count"] += 1
        profile["attack_types"].add(attack_type)
        profile["targets"].add(target_ip)
        profile["severity_levels"].add(severity)
        profile["last_seen"] = datetime.utcnow().isoformat()
    
    def detect_coordinated_attack(self, threshold: int = 3) -> List[Dict[str, Any]]:
        """Detect coordinated attacks from multiple IPs"""
        coordinated_attacks = []
        
        # Find targets attacked by multiple IPs
        target_attackers: Dict[str, set] = {}
        for attacker_ip, targets in self.threat_graph.items():
            for target in targets:
                if target not in target_attackers:
                    target_attackers[target] = set()
                target_attackers[target].add(attacker_ip)
        
        # Identify coordinated attacks
        for target, attackers in target_attackers.items():
            if len(attackers) >= threshold:
                coordinated_attacks.append({
                    "target": target,
                    "attacker_count": len(attackers),
                    "attackers": list(attackers),
                    "detected_at": datetime.utcnow().isoformat()
                })
        
        return coordinated_attacks
    
    def get_threat_score(self, ip_address: str) -> float:
        """Calculate threat score for IP address (0-100)"""
        if ip_address not in self.attacker_profiles:
            return 0.0
        
        profile = self.attacker_profiles[ip_address]
        
        # Score based on attack frequency
        attack_score = min(profile["attack_count"] * 5, 50)
        
        # Score based on severity
        severity_score = 0
        if "critical" in profile["severity_levels"]:
            severity_score = 30
        elif "high" in profile["severity_levels"]:
            severity_score = 20
        elif "medium" in profile["severity_levels"]:
            severity_score = 10
        
        # Score based on diversity of attacks
        diversity_score = min(len(profile["attack_types"]) * 5, 20)
        
        total_score = attack_score + severity_score + diversity_score
        return min(total_score, 100.0)
    
    def get_threat_feed(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent threat events for public feed"""
        return sorted(
            self.threat_events[-limit:],
            key=lambda x: x["timestamp"],
            reverse=True
        )


class AutoResponseEngine:
    """Automatic threat response based on threat level"""
    
    def __init__(self, deception_engine: DeceptionEngine):
        self.deception_engine = deception_engine
        self.response_actions: List[Dict[str, Any]] = []
    
    def determine_response(self, threat_score: float) -> Dict[str, Any]:
        """Determine response action based on threat score"""
        if threat_score < 20:
            return {
                "action": "allow",
                "description": "Low threat - allow access",
                "decoy_enabled": False
            }
        elif threat_score < 50:
            return {
                "action": "monitor",
                "description": "Medium threat - monitor access",
                "decoy_enabled": False
            }
        elif threat_score < 80:
            return {
                "action": "decoy",
                "description": "High threat - serve decoy data",
                "decoy_enabled": True,
                "decoy_type": random.choice(list(DecoyType))
            }
        else:
            return {
                "action": "block",
                "description": "Critical threat - block access",
                "decoy_enabled": False
            }
    
    def execute_response(self, threat_score: float, user_id: str, resource_id: str) -> Dict[str, Any]:
        """Execute response action"""
        response = self.determine_response(threat_score)
        
        action_record = {
            "action_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "resource_id": resource_id,
            "threat_score": threat_score,
            "action": response["action"],
            "description": response["description"]
        }
        
        # Generate decoy if needed
        if response.get("decoy_enabled"):
            decoy_data = self.deception_engine.generate_decoy(response.get("decoy_type"))
            action_record["decoy_id"] = decoy_data.get("decoy_type")
            action_record["decoy_data"] = decoy_data
        
        self.response_actions.append(action_record)
        return action_record


# Export main components
deception_engine = DeceptionEngine()
threat_intelligence = ThreatIntelligence()
auto_response_engine = AutoResponseEngine(deception_engine)
