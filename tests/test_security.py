import pytest
from unittest.mock import patch
from fastapi import HTTPException
from src.core.security import get_tenant_from_key, VALID_API_KEYS

def test_get_tenant_from_key_valid():
    for key, expected_tenant in VALID_API_KEYS.items():
        with patch("src.core.security.check_rate_limit", return_value=True):
            tenant = get_tenant_from_key(api_key=key)
            assert tenant == expected_tenant

def test_get_tenant_from_key_invalid():
    with pytest.raises(HTTPException) as exc_info:
        get_tenant_from_key(api_key="invalid_token")
    assert exc_info.value.status_code == 401
    assert "Invalid API Key" in exc_info.value.detail

def test_get_tenant_from_key_rate_limited():
    with patch("src.core.security.check_rate_limit", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_from_key(api_key="sk_test_123")
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail
