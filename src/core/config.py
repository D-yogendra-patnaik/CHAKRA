from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Chakra AI Guardrail"
    DEBUG: bool = False
    
    # DB
    DATABASE_URL: str = "postgresql+psycopg2://chakra:password@localhost:5432/chakra"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Model config
    MODEL_NAME: str = "distilbert-base-uncased-finetuned-sst-2-english"
    
    # Server config
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
