from pydantic import BaseSettings


class AppConfig(BaseSettings):
    db_uri: str = "sqlite:///./data/app-data.db"
    redis_uri: str = "redis://redis:6379/0"
    secret_key: str = "2032i1k2123"
