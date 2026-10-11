from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'postgresql+psycopg://tourism:tourism_local@localhost:5432/tourism'
    jwt_secret: str
    admin_email: str = 'admin@quan1.local'
    admin_password: str
    cors_origins: str = 'http://localhost:8081'
    seed_demo: bool = True
    worker_required: bool = False
    worker_stale_seconds: int = Field(default=90, ge=10, le=3600)
    job_lease_seconds: int = Field(default=120, ge=60, le=3600)

settings = Settings()
if len(settings.jwt_secret) < 32 or len(settings.admin_password) < 12:
    raise ValueError('JWT_SECRET must be >=32 characters and ADMIN_PASSWORD >=12 characters')
