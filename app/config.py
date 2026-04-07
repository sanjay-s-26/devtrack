import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = pydantic_settings.SettingsConfigDict(env_file=".env")


settings = Settings()
