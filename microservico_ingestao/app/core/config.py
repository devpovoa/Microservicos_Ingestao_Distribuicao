import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url : str = os.getenv("DATABASE_URL", "postgresql+psycopg2://ingest_user:ingest_pass@postgres_ingest:5432/ingest_db")
    
settings = Settings()