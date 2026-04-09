"""
Security endpoints for threat intelligence, deception, and auto-response
"""

from fastapi import APIRouter, Request, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from ..security.deception_engine import (
    deception_engine, threat_intelligence, auto_response_engine
)
from ..security.audit_logger import audit_log, AuditEvent, EventCategory, EventSeverity

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/security", tags=["security"])


# ============================================================================
# THREAT INTELLIGENCE ENDPOINTS
# ============================================================================

@router.post("/threats/record")
async def record_threat(
    request: Request,
    attacker_ip: str,
    target_ip: str,
    attack_type: str,
    severity: str,
    session_id: str = None
):
    """Record detected threat for intelligence gathering"""
    try:
        # Record in threat intelligence
        threat_intelligence.record_attack(attacker_ip, target_ip, attack_type, severity)
        
        # Log event
        audit_event = AuditEvent(
            category=EventCategory.SECURITY,
            action="threat_recorded",
            user_id="system",
            resource_id=target_ip,
            severity=EventSeverity.ALERT,
            details={
                "attacker_ip": attacker_ip,
                "attack_type": attack_type,
                "severity": severity
            },
            ip_address=request.client.host
        )
        audit_log.append_event(audit_event)
        
        return {
            "status": "success",
            "message": "Threat recorded",
            "threat_id": audit_event.event_id
        }
    
    except Exception as e:
        logger.error(f"Threat recording error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threats/feed")
async def get_threat_feed(
    session_id: str = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get public threat feed for network visibility"""
    try:
        feed = threat_intelligence.get_threat_feed(limit=limit)
        
        return {
            "status": "success",
            "threat_feed": feed,
            "count": len(feed),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Threat feed error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threats/coordinated")
async def detect_coordinated_attacks(
    session_id: str = None,
    threshold: int = Query(3, ge=2, le=100)
):
    """Detect coordinated attacks from multiple IPs"""
    try:
        coordinated = threat_intelligence.detect_coordinated_attack(threshold=threshold)
        
        return {
            "status": "success",
            "coordinated_attacks": coordinated,
            "count": len(coordinated),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Coordinated attack detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threats/score/{ip_address}")
async def get_threat_score(
    ip_address: str,
    session_id: str = None
):
    """Get threat score for IP address"""
    try:
        score = threat_intelligence.get_threat_score(ip_address)
        
        # Determine threat level
        if score < 20:
            threat_level = "low"
        elif score < 50:
            threat_level = "medium"
        elif score < 80:
            threat_level = "high"
        else:
            threat_level = "critical"
        
        return {
            "status": "success",
            "ip_address": ip_address,
            "threat_score": score,
            "threat_level": threat_level,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Threat score error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DECEPTION ENGINE ENDPOINTS
# ============================================================================

@router.post("/decoys/generate")
async def generate_decoy(
    request: Request,
    decoy_type: Optional[str] = None,
    session_id: str = None
):
    """Generate realistic decoy data"""
    try:
        decoy = deception_engine.generate_decoy(decoy_type)
        
        # Cache decoy for later retrieval
        decoy_id = decoy.get("decoy_type", "unknown")
        deception_engine.cache_decoy(decoy_id, decoy)
        
        # Log event
        audit_event = AuditEvent(
            category=EventCategory.SECURITY,
            action="decoy_generated",
            user_id="system",
            severity=EventSeverity.INFO,
            details={"decoy_type": str(decoy.get("decoy_type"))}
        )
        audit_log.append_event(audit_event)
        
        return {
            "status": "success",
            "decoy_type": str(decoy.get("decoy_type")),
            "decoy_id": decoy_id,
            "message": "Decoy data generated successfully"
        }
    
    except Exception as e:
        logger.error(f"Decoy generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/decoys/{decoy_id}")
async def retrieve_decoy(
    decoy_id: str,
    session_id: str = None
):
    """Retrieve cached decoy data"""
    try:
        decoy = deception_engine.get_cached_decoy(decoy_id)
        
        if not decoy:
            raise HTTPException(status_code=404, detail="Decoy not found")
        
        return {
            "status": "success",
            "decoy": decoy
        }
    
    except Exception as e:
        logger.error(f"Decoy retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AUTO-RESPONSE ENGINE ENDPOINTS
# ============================================================================

@router.post("/response/execute")
async def execute_response(
    request: Request,
    threat_score: float,
    user_id: str,
    resource_id: str,
    session_id: str = None
):
    """Execute automatic threat response"""
    try:
        action = auto_response_engine.execute_response(threat_score, user_id, resource_id)
        
        # Log response action
        audit_event = AuditEvent(
            category=EventCategory.SECURITY,
            action="threat_response_executed",
            user_id=user_id,
            resource_id=resource_id,
            severity=EventSeverity.WARNING,
            details={
                "threat_score": threat_score,
                "response_action": action["action"],
                "action_id": action["action_id"]
            },
            ip_address=request.client.host
        )
        audit_log.append_event(audit_event)
        
        return {
            "status": "success",
            "action": action["action"],
            "description": action["description"],
            "action_id": action["action_id"],
            "timestamp": action["timestamp"]
        }
    
    except Exception as e:
        logger.error(f"Response execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/response/determine")
async def determine_response(
    threat_score: float = Query(..., ge=0, le=100),
    session_id: str = None
):
    """Determine appropriate response for threat score"""
    try:
        response = auto_response_engine.determine_response(threat_score)
        
        return {
            "status": "success",
            "threat_score": threat_score,
            "action": response["action"],
            "description": response["description"],
            "decoy_enabled": response.get("decoy_enabled", False),
            "decoy_type": response.get("decoy_type")
        }
    
    except Exception as e:
        logger.error(f"Response determination error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# THREAT INTELLIGENCE DASHBOARD
# ============================================================================

@router.get("/dashboard/overview")
async def get_security_overview(session_id: str = None):
    """Get security dashboard overview"""
    try:
        # Get threat statistics
        threat_feed = threat_intelligence.get_threat_feed(limit=1000)
        coordinated_attacks = threat_intelligence.detect_coordinated_attack(threshold=2)
        
        # Calculate statistics
        total_threats = len(threat_feed)
        critical_threats = len([t for t in threat_feed if t["severity"] == "critical"])
        high_threats = len([t for t in threat_feed if t["severity"] == "high"])
        
        # Get top attackers
        top_attackers = sorted(
            threat_intelligence.attacker_profiles.items(),
            key=lambda x: x[1]["attack_count"],
            reverse=True
        )[:10]
        
        return {
            "status": "success",
            "statistics": {
                "total_threats": total_threats,
                "critical_threats": critical_threats,
                "high_threats": high_threats,
                "coordinated_attacks": len(coordinated_attacks),
                "unique_attackers": len(threat_intelligence.attacker_profiles)
            },
            "top_attackers": [
                {
                    "ip": ip,
                    "attack_count": profile["attack_count"],
                    "threat_score": threat_intelligence.get_threat_score(ip),
                    "attack_types": list(profile["attack_types"]),
                    "last_seen": profile.get("last_seen")
                }
                for ip, profile in top_attackers
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Dashboard overview error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/threat-map")
async def get_threat_map(session_id: str = None):
    """Get threat map for visualization"""
    try:
        threat_feed = threat_intelligence.get_threat_feed(limit=500)
        
        # Group by attack type
        attacks_by_type = {}
        for threat in threat_feed:
            attack_type = threat["attack_type"]
            if attack_type not in attacks_by_type:
                attacks_by_type[attack_type] = 0
            attacks_by_type[attack_type] += 1
        
        # Group by severity
        attacks_by_severity = {}
        for threat in threat_feed:
            severity = threat["severity"]
            if severity not in attacks_by_severity:
                attacks_by_severity[severity] = 0
            attacks_by_severity[severity] += 1
        
        return {
            "status": "success",
            "threat_feed": threat_feed,
            "attacks_by_type": attacks_by_type,
            "attacks_by_severity": attacks_by_severity,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Threat map error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/response-actions")
async def get_response_actions(
    session_id: str = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get recent response actions"""
    try:
        actions = auto_response_engine.response_actions[-limit:]
        
        return {
            "status": "success",
            "actions": actions,
            "count": len(actions),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Response actions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
