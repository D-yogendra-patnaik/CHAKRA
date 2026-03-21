import logging
import json
from datetime import datetime

logger = logging.getLogger("chakra_audit")
logger.setLevel(logging.INFO)

# In production, route to a structured JSON file or directly to Elasticsearch/Datadog
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)

def log_audit_action(tenant_id: str, session_id: str, action: str, risk_score: float, labels: list, latency_ms: float):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "tenant_id": tenant_id,
        "session_id": session_id,
        "action": action,
        "risk_score": risk_score,
        "labels": labels,
        "latency_ms": latency_ms
    }
    logger.info(json.dumps(log_entry))
    
    # Can also insert asynchronously to Postgres here using db.postgres.SessionLocal
