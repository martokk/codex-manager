from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    # Environment Settings #
    ENV_NAME: str = "Unknown"
    DEBUG: bool = True

    # Log
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_ECHO: bool = False

    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 5000
    BASE_DOMAIN: str = "localhost:5000"
    BASE_URL: str = "http://localhost:5000"
    PROXY_HOST: str = "127.0.0.1"
    UVICORN_RELOAD: bool = True
    UVICORN_ENTRYPOINT: str = "python_fastapi_stack.core.app:app"

    # API
    API_V1_PREFIX: str = "/api/v1"
    JWT_ACCESS_SECRET_KEY: str = "jwt_access_secret_key"
    JWT_REFRESH_SECRET_KEY: str = "jwt_refresh_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080
    ALGORITHM: str = "HS256"

    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int | None = None
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None
    NOTIFY_EMAIL_TO: EmailStr | None = None

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAILS_ENABLED: bool = False

    # Users
    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = False

    # Notify
    TELEGRAM_API_TOKEN: str = ""
    TELEGRAM_CHAT_ID: int = 0
    NOTIFY_ON_START: bool = True

    # Project Settings
    PROJECT_NAME: str = "Python FastAPI Stack"
    PACKAGE_NAME: str = PROJECT_NAME.lower().replace("-", "_").replace(" ", "_")
    PROJECT_DESCRIPTION: str = (
        f"{PROJECT_NAME}: poetry, fastapi, sqlmodel, alembic, loguru, crud, notify."
    )
    VERSION: str = ""
