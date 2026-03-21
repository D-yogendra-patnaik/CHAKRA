from typing import Any

# Mock policy config
# Usually fetched from Postgres via Redis cache
TENANT_POLICIES = {
    "default": {
        "block_threshold": 0.75,
        "warn_threshold": 0.5,
        "sanitize_pii": True
    },
    "bank_xyz": {
        "block_threshold": 0.6,
        "warn_threshold": 0.4,
        "sanitize_pii": True
    }
}

async def apply_policy(tenant_id: str, result: Any) -> Any:
    """
    Evaluates the aggregated GuardrailResult against the tenant's exact policy thresholds.
    """
    policy = TENANT_POLICIES.get(tenant_id, TENANT_POLICIES["default"])
    
    if result.risk_score >= policy["block_threshold"]:
        result.action = "block"
        result.explanation = f"Risk score {result.risk_score} exceeds block threshold of {policy['block_threshold']}."
    elif result.risk_score >= policy["warn_threshold"]:
        result.action = "warn"
        result.explanation = f"Risk score {result.risk_score} exceeds warn threshold."
    else:
        result.action = "allow"
        result.explanation = "Prompt is safe."
        
    # Example Sanitization
    if policy.get("sanitize_pii") and "pii_leak" in result.labels:
        result.action = "sanitize"
        result.explanation = "Detected PII. Proceeding with redaction."
        result.sanitized_prompt = "[REDACTED_PII]" # In reality use regex outputs for this
        
    return result
