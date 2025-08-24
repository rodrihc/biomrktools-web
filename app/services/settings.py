from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str
    PORT: str
    AZURE_STORAGE_ACCOUNT: str
    AZURE_CONTAINER: str
    JSON_PATH: str
    DELTA_PATH: str
    API_BASE: str
    SAS_TOKEN: str

    class Config:
        env_file = ".env"

settings = Settings()
