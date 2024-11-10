from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: SecretStr
    proxy: SecretStr


settings = Settings()
