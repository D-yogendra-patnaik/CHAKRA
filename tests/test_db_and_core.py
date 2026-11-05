import pytest
from unittest.mock import MagicMock, patch
from src.core.observability import log_audit_action
import src.db.redis_client as redis_module
import src.db.postgres as postgres_module

# --- Observability Tests ---
def test_log_audit_action():
    with patch("src.core.observability.logger.info") as mock_info:
        log_audit_action("t1", "s1", "allow", 0.05, ["safe"], 12.5)
        assert mock_info.called
        log_str = mock_info.call_args[0][0]
        assert "t1" in log_str
        assert "allow" in log_str
        assert "12.5" in log_str

# --- Redis Client Tests ---
def test_redis_when_unavailable():
    # Force _redis_available to False
    with patch.object(redis_module, "_redis_available", False):
        client = redis_module._get_redis()
        assert client is None
        # Rate limit returns True when redis is unavailable
        assert redis_module.check_rate_limit("any_tenant") is True
        # store_session_context does not raise
        redis_module.store_session_context("s1", {"foo": "bar"})

def test_redis_rate_limit_allowed():
    mock_client = MagicMock()
    mock_client.incr.return_value = 1
    with patch.object(redis_module, "_get_redis", return_value=mock_client):
        allowed = redis_module.check_rate_limit("tenant1", limit=10, window=60)
        assert allowed is True
        mock_client.expire.assert_called_with("rate_limit:tenant1", 60)

def test_redis_rate_limit_exceeded():
    mock_client = MagicMock()
    mock_client.incr.return_value = 101
    with patch.object(redis_module, "_get_redis", return_value=mock_client):
        allowed = redis_module.check_rate_limit("tenant1", limit=100)
        assert allowed is False

def test_redis_store_session_context():
    mock_client = MagicMock()
    with patch.object(redis_module, "_get_redis", return_value=mock_client):
        redis_module.store_session_context("sess123", {"key": "val"})
        mock_client.hset.assert_called_with("session:sess123", mapping={"key": "val"})
        mock_client.expire.assert_called_with("session:sess123", 3600)

def test_redis_connection_exception():
    with patch("redis.from_url", side_effect=Exception("Redis connection error")):
        with patch.object(redis_module, "_redis_available", None):
            with patch.object(redis_module, "_redis_client", None):
                client = redis_module._get_redis()
                assert client is None
                assert redis_module._redis_available is False

# --- Postgres Tests ---
def test_postgres_engine_creation_sqlite_mock():
    with patch.object(postgres_module, "settings") as mock_settings:
        mock_settings.DATABASE_URL = "sqlite:///:memory:"
        with patch.object(postgres_module, "_engine", None):
            eng = postgres_module._get_engine()
            assert eng is not None
            postgres_module.init_db()

def test_postgres_get_db_generator():
    with patch.object(postgres_module, "settings") as mock_settings:
        mock_settings.DATABASE_URL = "sqlite:///:memory:"
        with patch.object(postgres_module, "_engine", None):
            with patch.object(postgres_module, "_SessionLocal", None):
                gen = postgres_module.get_db()
                db = next(gen)
                assert db is not None
                try:
                    next(gen)
                except StopIteration:
                    pass

def test_postgres_engine_failure_fallback():
    with patch("src.db.postgres.create_engine", side_effect=Exception("DB down")):
        with patch.object(postgres_module, "_engine", None):
            with patch.object(postgres_module, "_SessionLocal", None):
                eng = postgres_module._get_engine()
                assert eng is None
                gen = postgres_module.get_db()
                db = next(gen)
                assert db is None
                postgres_module.init_db()  # Should not raise
