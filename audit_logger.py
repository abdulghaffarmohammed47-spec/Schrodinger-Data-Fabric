"""
Enterprise Audit Logging and Compliance System for SDF v10
Implements immutable append-only logs, tamper detection, and compliance frameworks
"""

import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid
from pathlib import Path


class EventCategory(str, Enum):
    """Audit event categories"""
    AUTHENTICATION = "authentication"
    FILE_OPERATION = "file_operation"
    ACCESS_CONTROL = "access_control"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    SYSTEM = "system"
    ENCRYPTION = "encryption"
    ANOMALY = "anomaly"


class EventSeverity(str, Enum):
    """Event severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ALERT = "alert"


class AuditEvent:
    """Immutable audit event with cryptographic commitment"""
    
    def __init__(
        self,
        category: EventCategory,
        action: str,
        user_id: str,
        resource_id: Optional[str] = None,
        severity: EventSeverity = EventSeverity.INFO,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        self.event_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
        self.category = category
        self.action = action
        self.user_id = user_id
        self.resource_id = resource_id
        self.severity = severity
        self.details = details or {}
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.previous_hash = None
        self.event_hash = None
        self._compute_hash()
    
    def _compute_hash(self):
        """Compute cryptographic hash of event (blockchain-style)"""
        event_data = {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "category": self.category.value,
            "action": self.action,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "severity": self.severity.value,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "previous_hash": self.previous_hash
        }
        
        event_string = json.dumps(event_data, sort_keys=True)
        self.event_hash = hashlib.sha256(event_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "category": self.category.value,
            "action": self.action,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "severity": self.severity.value,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "event_hash": self.event_hash,
            "previous_hash": self.previous_hash
        }


class AuditLog:
    """Immutable append-only audit log with tamper detection"""
    
    def __init__(self, log_file: str = "audit_log.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.events: List[AuditEvent] = []
        self.last_event_hash = None
        self._load_existing_log()
    
    def _load_existing_log(self):
        """Load existing audit log from disk"""
        if self.log_file.exists():
            with open(self.log_file, "r") as f:
                for line in f:
                    if line.strip():
                        event_data = json.loads(line)
                        event = AuditEvent(
                            category=EventCategory(event_data["category"]),
                            action=event_data["action"],
                            user_id=event_data["user_id"],
                            resource_id=event_data.get("resource_id"),
                            severity=EventSeverity(event_data.get("severity", "info")),
                            details=event_data.get("details", {}),
                            ip_address=event_data.get("ip_address"),
                            user_agent=event_data.get("user_agent")
                        )
                        event.event_id = event_data["event_id"]
                        event.timestamp = event_data["timestamp"]
                        event.event_hash = event_data["event_hash"]
                        event.previous_hash = event_data.get("previous_hash")
                        self.events.append(event)
                        self.last_event_hash = event.event_hash
    
    def append_event(self, event: AuditEvent) -> str:
        """
        Append event to immutable log
        
        Returns:
            Event ID
        """
        # Link to previous event (blockchain-style)
        event.previous_hash = self.last_event_hash
        event._compute_hash()
        
        # Append to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")
        
        # Update in-memory log
        self.events.append(event)
        self.last_event_hash = event.event_hash
        
        return event.event_id
    
    def verify_integrity(self) -> bool:
        """Verify integrity of entire audit log"""
        previous_hash = None
        
        for event in self.events:
            if event.previous_hash != previous_hash:
                return False
            
            # Recompute hash to verify
            event_data = event.to_dict()
            event_data["previous_hash"] = previous_hash
            event_data.pop("event_hash")
            
            event_string = json.dumps(event_data, sort_keys=True)
            computed_hash = hashlib.sha256(event_string.encode()).hexdigest()
            
            if computed_hash != event.event_hash:
                return False
            
            previous_hash = event.event_hash
        
        return True
    
    def detect_tampering(self) -> List[Dict[str, Any]]:
        """Detect any tampering in audit log"""
        tampered_events = []
        previous_hash = None
        
        for i, event in enumerate(self.events):
            if event.previous_hash != previous_hash:
                tampered_events.append({
                    "event_index": i,
                    "event_id": event.event_id,
                    "reason": "Previous hash mismatch",
                    "expected_previous": previous_hash,
                    "actual_previous": event.previous_hash
                })
            
            previous_hash = event.event_hash
        
        return tampered_events
    
    def query_events(
        self,
        user_id: Optional[str] = None,
        category: Optional[EventCategory] = None,
        severity: Optional[EventSeverity] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query events with filters"""
        results = []
        
        for event in reversed(self.events):
            # Apply filters
            if user_id and event.user_id != user_id:
                continue
            
            if category and event.category != category:
                continue
            
            if severity and event.severity != severity:
                continue
            
            if start_time and event.timestamp < start_time:
                continue
            
            if end_time and event.timestamp > end_time:
                continue
            
            results.append(event.to_dict())
            
            if len(results) >= limit:
                break
        
        return results
    
    def export_for_compliance(self, format: str = "json") -> str:
        """Export audit log for compliance purposes"""
        if format == "json":
            return json.dumps([e.to_dict() for e in self.events], indent=2)
        
        elif format == "csv":
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "timestamp", "event_id", "category", "action", "user_id",
                "resource_id", "severity", "ip_address"
            ])
            writer.writeheader()
            
            for event in self.events:
                writer.writerow({
                    "timestamp": event.timestamp,
                    "event_id": event.event_id,
                    "category": event.category.value,
                    "action": event.action,
                    "user_id": event.user_id,
                    "resource_id": event.resource_id,
                    "severity": event.severity.value,
                    "ip_address": event.ip_address
                })
            
            return output.getvalue()
        
        return ""


class ComplianceFramework:
    """Compliance framework for multiple standards"""
    
    def __init__(self, audit_log: AuditLog):
        self.audit_log = audit_log
        self.frameworks = {
            "GDPR": self._check_gdpr,
            "HIPAA": self._check_hipaa,
            "SOC2": self._check_soc2,
            "PCI-DSS": self._check_pci_dss
        }
    
    def _check_gdpr(self) -> Dict[str, Any]:
        """Check GDPR compliance"""
        events = self.audit_log.query_events(limit=10000)
        
        # Check for data deletion events
        deletion_events = [e for e in events if e["action"] == "delete"]
        
        # Check for access logs
        access_events = [e for e in events if e["category"] == "access_control"]
        
        return {
            "framework": "GDPR",
            "status": "compliant" if len(deletion_events) > 0 and len(access_events) > 0 else "needs_review",
            "deletion_events": len(deletion_events),
            "access_logs": len(access_events),
            "checks": {
                "data_deletion_capability": len(deletion_events) > 0,
                "access_logging": len(access_events) > 0,
                "audit_trail": self.audit_log.verify_integrity()
            }
        }
    
    def _check_hipaa(self) -> Dict[str, Any]:
        """Check HIPAA compliance"""
        events = self.audit_log.query_events(limit=10000)
        
        # Check for encryption events
        encryption_events = [e for e in events if e["category"] == "encryption"]
        
        # Check for authentication events
        auth_events = [e for e in events if e["category"] == "authentication"]
        
        # Check for anomaly detection
        anomaly_events = [e for e in events if e["category"] == "anomaly"]
        
        return {
            "framework": "HIPAA",
            "status": "compliant" if all([
                len(encryption_events) > 0,
                len(auth_events) > 0,
                len(anomaly_events) > 0
            ]) else "needs_review",
            "encryption_events": len(encryption_events),
            "authentication_events": len(auth_events),
            "anomaly_detection_events": len(anomaly_events),
            "checks": {
                "encryption_enabled": len(encryption_events) > 0,
                "access_controls": len(auth_events) > 0,
                "monitoring": len(anomaly_events) > 0,
                "audit_trail": self.audit_log.verify_integrity()
            }
        }
    
    def _check_soc2(self) -> Dict[str, Any]:
        """Check SOC 2 compliance"""
        events = self.audit_log.query_events(limit=10000)
        
        # Check for security events
        security_events = [e for e in events if e["category"] == "security"]
        
        # Check for system events
        system_events = [e for e in events if e["category"] == "system"]
        
        return {
            "framework": "SOC2",
            "status": "compliant" if len(security_events) > 0 and len(system_events) > 0 else "needs_review",
            "security_events": len(security_events),
            "system_events": len(system_events),
            "checks": {
                "security_monitoring": len(security_events) > 0,
                "system_monitoring": len(system_events) > 0,
                "audit_trail": self.audit_log.verify_integrity()
            }
        }
    
    def _check_pci_dss(self) -> Dict[str, Any]:
        """Check PCI-DSS compliance"""
        events = self.audit_log.query_events(limit=10000)
        
        # Check for access control events
        access_events = [e for e in events if e["category"] == "access_control"]
        
        # Check for encryption events
        encryption_events = [e for e in events if e["category"] == "encryption"]
        
        return {
            "framework": "PCI-DSS",
            "status": "compliant" if len(access_events) > 0 and len(encryption_events) > 0 else "needs_review",
            "access_control_events": len(access_events),
            "encryption_events": len(encryption_events),
            "checks": {
                "access_control": len(access_events) > 0,
                "encryption": len(encryption_events) > 0,
                "audit_trail": self.audit_log.verify_integrity()
            }
        }
    
    def check_all_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Check compliance across all frameworks"""
        return {
            name: check_func() for name, check_func in self.frameworks.items()
        }


# Export main components
audit_log = AuditLog()
compliance_framework = ComplianceFramework(audit_log)
