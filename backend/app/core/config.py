from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    login_max_attempts: int = 5
    login_lockout_minutes: int = 15
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_use_tls: bool = True
    app_base_url: str = "http://localhost:8000"
    environment: str = "development"
    require_email_verification: bool = False
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()
