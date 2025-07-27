from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Banco de ingestão
    database_url: str = "postgresql+psycopg2://ingest_user:ingest_pass@postgres_ingest:5432/ingest_db"
    
    # RabbitMQ (para futura integração)
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672//"
    
    # Configurações do watcher
    scan_interval: int = 3
    processed_limit: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
