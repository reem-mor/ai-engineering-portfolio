from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_project_root() -> Path:
    """
    Resolve the project root directory.

    Expected project layout:
        incident-assistant-rag/
        ├── backend/
        │   └── app/
        └── data/

    Also supports a mistaken nested backend layout:
        backend/backend/app/

    The goal is to return the directory that contains `data/`.
    """
    app_container = Path(__file__).resolve().parents[2]

    if (app_container / "data").is_dir():
        return app_container

    parent = app_container.parent
    if (parent / "data").is_dir():
        return parent

    return app_container


_PROJECT_ROOT_DEFAULT = _resolve_project_root()


class Settings(BaseSettings):
    # Application
    app_name: str = "IncidentIQ RAG API"
    app_version: str = "0.1.0"
    environment: str = "local"

    # API
    api_prefix: str = "/api"

    # Paths
    project_root: Path = Field(default=_PROJECT_ROOT_DEFAULT)
    data_dir: Path = Field(default=_PROJECT_ROOT_DEFAULT / "data")
    raw_data_dir: Path = Field(default=_PROJECT_ROOT_DEFAULT / "data" / "raw")
    processed_data_dir: Path = Field(
        default=_PROJECT_ROOT_DEFAULT / "data" / "processed"
    )
    chunks_data_dir: Path = Field(default=_PROJECT_ROOT_DEFAULT / "data" / "chunks")
    embeddings_data_dir: Path = Field(
        default=_PROJECT_ROOT_DEFAULT / "data" / "embeddings"
    )
    faiss_index_dir: Path = Field(
        default=_PROJECT_ROOT_DEFAULT / "data" / "faiss_index"
    )
    sample_documents_dir: Path = Field(
        default=_PROJECT_ROOT_DEFAULT / "data" / "sample_documents"
    )

    # FAISS index files
    faiss_index_file: str = "incidentiq.index"
    faiss_metadata_file: str = "incidentiq_metadata.json"

    # Upload validation
    allowed_file_extensions: set[str] = {".md", ".txt", ".csv", ".pdf", ".docx"}
    max_upload_size_bytes: int = 10 * 1024 * 1024

    # Chunking
    chunk_size: int = 700
    chunk_overlap: int = 120
    min_chunk_size: int = 80

    # Retrieval
    top_k_default: int = 5
    top_k_min: int = 1
    top_k_max: int = 10
    retrieval_score_threshold: float = 0.25

    # OpenAI
    openai_api_key: str | None = None
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    answer_model: str = "gpt-4o-mini"

    # Supabase - optional
    database_enabled: bool = False
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
