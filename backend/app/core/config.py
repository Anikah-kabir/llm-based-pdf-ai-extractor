from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    llm_db_host: str = Field(..., alias="LLM_DB_HOST")
    llm_db_port: int = Field(..., alias="LLM_DB_PORT")
    llm_db_user: str = Field(..., alias="LLM_DB_USER")
    llm_db_pass: str = Field(..., alias="LLM_DB_PASS")
    llm_db_name: str = Field(..., alias="LLM_DB_NAME")
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.llm_db_user}:{self.llm_db_pass}"
            f"@{self.llm_db_host}:{self.llm_db_port}/{self.llm_db_name}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )

# Settings
@lru_cache
def get_settings():
    return Settings()