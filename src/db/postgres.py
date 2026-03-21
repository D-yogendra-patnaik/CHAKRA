import logging
from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from src.core.config import settings

logger = logging.getLogger("chakra")

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True)
    session_id = Column(String, index=True)
    timestamp = Column(DateTime)
    action = Column(String)
    risk_score = Column(Float)
    labels = Column(JSON)
    prompt_snippet = Column(String)

class TenantConfig(Base):
    __tablename__ = "tenant_configs"

    tenant_id = Column(String, primary_key=True)
    policy_json = Column(JSON)

# --- Lazy / Resilient engine setup ---
_engine = None
_SessionLocal = None

def _get_engine():
    global _engine
    if _engine is None:
        try:
            _engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        except Exception as e:
            logger.warning(f"Could not create DB engine: {e}. Running without Postgres.")
    return _engine

def get_session_factory():
    global _SessionLocal
    eng = _get_engine()
    if eng is None:
        return None
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    return _SessionLocal

def get_db():
    factory = get_session_factory()
    if factory is None:
        yield None
        return
    db = factory()
    try:
        yield db
    finally:
        db.close()

def init_db():
    eng = _get_engine()
    if eng:
        try:
            Base.metadata.create_all(bind=eng)
            logger.info("Database tables created.")
        except Exception as e:
            logger.warning(f"Could not initialize DB tables: {e}. Continuing without Postgres.")
