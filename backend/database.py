from sqlalchemy import create_engine, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, StaticPool
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pricing_user:secure_password@localhost:5432/pricing_engine"
)

# Connection pooling for PostgreSQL
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("DEBUG", "False") == "True",
    )
else:
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool if os.getenv("ENV") == "testing" else None,
        echo=os.getenv("DEBUG", "False") == "True",
    )

# TimescaleDB specific setup
@event.listens_for(engine, "connect")
def setup_timescaledb(dbapi_conn, connection_record):
    """Enable TimescaleDB extensions on connection (PostgreSQL only)"""
    # Skip for SQLite
    if "sqlite" in DATABASE_URL:
        return
    
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        dbapi_conn.commit()
        logger.info("✓ TimescaleDB extensions enabled")
    except Exception as e:
        logger.error(f"Error setting up extensions: {e}")
    finally:
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Session:
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables initialized")

def drop_all_tables():
    """Drop all tables (use with caution)"""
    Base.metadata.drop_all(bind=engine)
    logger.warning("⚠️  All tables dropped!")