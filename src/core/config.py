from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    SECRET: str
    DATABASE_URL: str
    ENVIRONMENT: str = "development" 
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
config = Config()