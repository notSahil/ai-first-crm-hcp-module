import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://crm_user:crm_pass@localhost:5432/crm_db")

# Try PostgreSQL first; fall back to SQLite if not available (for local dev)
def _create_engine_with_fallback():
    try:
        eng = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
        # Test connectivity
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connected to PostgreSQL")
        return eng
    except Exception as e:
        print(f"⚠️  PostgreSQL not available ({e}). Falling back to SQLite.")
        sqlite_url = "sqlite:///./crm_local.db"
        return create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})

engine = _create_engine_with_fallback()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
