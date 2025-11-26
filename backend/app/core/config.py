# Pydantic settings
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Intelligent Ingestion Pipeline RAG"

    # Adding db settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    UPLOAD_DIR: str = "temp_storage" # Directory for temp files

    REDIS_HOST: str
    LLM_NAME: str
    EMBEDDINGS_MODEL_NAME: str
    QDRANT_HOST: str
    QDRANT_HOST: int

    @property
    def DATABASE_URL(self) -> str:
        # Creating the database URL: postgresql+asyncpg://user:pass@localhost:5432/db_name
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        # Define the .env file location
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()