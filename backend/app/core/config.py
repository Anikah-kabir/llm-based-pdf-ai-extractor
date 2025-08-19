from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    use_ollama: str = Field(..., alias="USE_OLLAMA")
    ollama_model: str = Field(..., alias="OLLAMA_MODEL")
    ollama_host: str = Field(..., alias="OLLAMA_HOST")
    llm_db_host: str = Field(..., alias="LLM_DB_HOST")
    llm_db_port: int = Field(..., alias="LLM_DB_PORT")
    llm_db_user: str = Field(..., alias="LLM_DB_USER")
    llm_db_pass: str = Field(..., alias="LLM_DB_PASS")
    llm_db_name: str = Field(..., alias="LLM_DB_NAME")
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    access_token_expire_minutes: str = Field(..., alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: str | None = None
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"
    max_chunk_chars: int = Field(..., alias="MAX_CHUNK_CHARS")
    max_overlaps: int = Field(..., alias="MAX_OVERLAPS")
    max_text_chars_upload: int = Field(..., alias="MAX_TEXT_CHARS_UPLOAD")
    doc_type_detect_use_llm: bool = True
    doc_type_detect_model: str = "gpt-4o-mini" 
    doc_type_detect_max_chars: int = Field(..., alias="DOC_TYPE_DETECT_MAX_CHARS") 

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