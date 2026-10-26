from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import model_validator


class Settings(BaseSettings):
    DATABASE_URL_MASTER: str = "mysql+aiomysql://root:123456@localhost:3306/coinwise"
    DATABASE_URL_SLAVE: str = "mysql+aiomysql://root:123456@localhost:3306/coinwise"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ES_HOST: str = "http://localhost:9200"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    ENCRYPTION_KEY: str = ""
    DATA_ENCRYPTION_KEY: str = ""
    DEBUG: bool = False
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""

    # 阿里云百炼
    BAILIAN_API_KEY: str = ""
    BAILIAN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    BAILIAN_MODEL: str = "qwen-plus"
    BAILIAN_TEMPERATURE: float = 0.3
    BAILIAN_MAX_TOKENS: int = 1500
    BAILIAN_TOP_P: float = 0.7
    BAILIAN_ENABLE_SEARCH: bool = False

    class Config:
        env_file = str(Path(__file__).resolve().parent.parent.parent / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

    @model_validator(mode="after")
    def validate_secrets(self):
        if not self.JWT_SECRET:
            raise ValueError("JWT_SECRET 未设置，请在 .env 中配置")
        if not self.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY 未设置，请在 .env 中配置")
        if not self.DATA_ENCRYPTION_KEY:
            raise ValueError("DATA_ENCRYPTION_KEY 未设置，请在 .env 中配置")
        return self


settings = Settings()