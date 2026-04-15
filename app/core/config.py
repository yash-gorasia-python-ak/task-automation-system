from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str
    CELERY_DB_URL: str

    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    SUPERUSER_NAME: str
    SUPERUSER_PASSWORD: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: SecretStr
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_URL: str
    RABBITMQ_URL: str

    DOMAIN: str


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings(**{})

