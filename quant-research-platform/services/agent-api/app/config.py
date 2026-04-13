from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_model_main: str = "gpt-5.4-mini"
    openai_model_cheap: str = "gpt-5.4-nano"


settings = Settings()
