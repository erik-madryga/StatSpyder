# backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic_settings import BaseSettings

# Load environment variables safely
class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"  # Fallback to local sqlite if env isn't loaded

    class Config:
        env_file = ".env"

settings = Settings()

# pool_pre_ping=True checks if the connection is alive before sending queries
# (Crucial for serverless or pooled cloud environments like Supabase)
db_url = settings.database_url
if db_url.endswith("?pgbouncer=true"):
    db_url = db_url.replace("?pgbouncer=true", "")

engine = create_engine(
    db_url, 
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI Dependency to yield a database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()