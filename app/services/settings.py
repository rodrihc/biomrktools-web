from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Explicitly load .env first
load_dotenv(".env", override=False)  # override=False means host vars take priority
class Settings(BaseSettings):
    HOST: str
    PORT: str    
    BIOMRKTOOLS_SA_TOKEN: str | None = None
    BIOMRKTOOLS_ENV: str | None = None
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
