from pydantic import BaseSettings


class AppConfig(BaseSettings):
    db_uri: str = "sqlite:///data/app-data.db"
