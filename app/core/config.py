from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    OLLAMA_BASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()