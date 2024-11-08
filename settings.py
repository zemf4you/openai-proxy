from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    proxy: str


settings = Settings()
