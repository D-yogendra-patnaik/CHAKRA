from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from src.db.redis_client import check_rate_limit

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

VALID_API_KEYS = {
    "sk_test_123": "default",
    "sk_bank_456": "bank_xyz"
}

def get_tenant_from_key(api_key: str = Security(api_key_header)) -> str:
    tenant_id = VALID_API_KEYS.get(api_key)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    
    # Enforce Rate Limiting
    if not check_rate_limit(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
        
    return tenant_id
