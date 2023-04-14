from pydantic import BaseSettings


class AppConfig(BaseSettings):
    db_uri: str = "sqlite:///./data/app-data.db"
    secret_key: str = "2032i1k2123"
