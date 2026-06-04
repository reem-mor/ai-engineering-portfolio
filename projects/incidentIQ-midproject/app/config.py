"""Typed config loaded from environment variables (with .env fallback)."""
from __future__ import annotations

import os
import secrets
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

_FALSE_VALUES = {"false", "0", "no", "off"}
_TRUE_VALUES = {"true", "1", "yes", "on"}


class ConfigError(RuntimeError):
    """Raised when required environment variables are missing or invalid."""


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if raw in _TRUE_VALUES:
        return True
    if raw in _FALSE_VALUES:
        return False
    return default


@dataclass(frozen=True)
class Config:
    AWS_REGION: str
    BEDROCK_KB_ID: str
    BEDROCK_MODEL_ARN: str
    BEDROCK_NUM_RESULTS: int
    SECRET_KEY: str
    FLASK_ENV: str
    S3_BUCKET: str = ""
    S3_PREFIX: str = "projects/incidentIQ-midproject/data/sample_documents"
    BEDROCK_DATA_SOURCE_ID: str = ""
    MAX_UPLOAD_BYTES: int = 5_242_880
    BEDROCK_AGENT_ID: str = ""
    BEDROCK_AGENT_ALIAS_ID: str = ""
    RAG_BACKEND: str = "agent"
    USE_BEDROCK: bool = True

    @classmethod
    def from_env(cls) -> "Config":
        max_upload = os.environ.get("MAX_UPLOAD_BYTES", "5242880").strip()
        rag_backend = os.environ.get("RAG_BACKEND", "agent").strip().lower()
        if rag_backend not in ("agent", "retrieve_and_generate"):
            raise ConfigError(
                f"Invalid RAG_BACKEND={rag_backend!r}; use 'agent' or 'retrieve_and_generate'"
            )
        agent_id = os.environ.get("BEDROCK_AGENT_ID", "").strip()
        agent_alias = os.environ.get("BEDROCK_AGENT_ALIAS_ID", "").strip()
        if rag_backend == "agent" and (not agent_id or not agent_alias):
            raise ConfigError(
                "RAG_BACKEND=agent requires BEDROCK_AGENT_ID and BEDROCK_AGENT_ALIAS_ID"
            )
        return cls(
            AWS_REGION=_require("AWS_REGION"),
            BEDROCK_KB_ID=_require("BEDROCK_KB_ID"),
            BEDROCK_MODEL_ARN=_require("BEDROCK_MODEL_ARN"),
            BEDROCK_NUM_RESULTS=int(os.environ.get("BEDROCK_NUM_RESULTS", "5")),
            SECRET_KEY=_require("FLASK_SECRET_KEY"),
            FLASK_ENV=os.environ.get("FLASK_ENV", "production"),
            S3_BUCKET=os.environ.get("S3_BUCKET", "").strip(),
            S3_PREFIX=os.environ.get(
                "S3_PREFIX", "projects/incidentIQ-midproject/data/sample_documents"
            ).strip(),
            BEDROCK_DATA_SOURCE_ID=os.environ.get("BEDROCK_DATA_SOURCE_ID", "").strip(),
            MAX_UPLOAD_BYTES=int(max_upload),
            BEDROCK_AGENT_ID=agent_id,
            BEDROCK_AGENT_ALIAS_ID=agent_alias,
            RAG_BACKEND=rag_backend,
            USE_BEDROCK=_env_bool("USE_BEDROCK", True),
        )

    @classmethod
    def local(cls) -> "Config":
        """Build an offline-safe config that never requires AWS credentials.

        Used as the default startup path when Bedrock is disabled
        (``USE_BEDROCK=false``) or AWS configuration is incomplete. The local
        RAG + deterministic tools demo runs entirely from this config.
        """
        secret = os.environ.get("FLASK_SECRET_KEY", "").strip() or (
            "dev-local-" + secrets.token_hex(16)
        )
        max_upload = os.environ.get("MAX_UPLOAD_BYTES", "5242880").strip()
        return cls(
            AWS_REGION=os.environ.get("AWS_REGION", "us-east-1").strip() or "us-east-1",
            BEDROCK_KB_ID=os.environ.get("BEDROCK_KB_ID", "").strip(),
            BEDROCK_MODEL_ARN=os.environ.get("BEDROCK_MODEL_ARN", "").strip(),
            BEDROCK_NUM_RESULTS=int(os.environ.get("BEDROCK_NUM_RESULTS", "5") or "5"),
            SECRET_KEY=secret,
            FLASK_ENV=os.environ.get("FLASK_ENV", "development"),
            S3_BUCKET=os.environ.get("S3_BUCKET", "").strip(),
            S3_PREFIX=os.environ.get(
                "S3_PREFIX", "projects/incidentIQ-midproject/data/sample_documents"
            ).strip(),
            BEDROCK_DATA_SOURCE_ID=os.environ.get("BEDROCK_DATA_SOURCE_ID", "").strip(),
            MAX_UPLOAD_BYTES=int(max_upload or "5242880"),
            BEDROCK_AGENT_ID=os.environ.get("BEDROCK_AGENT_ID", "").strip(),
            BEDROCK_AGENT_ALIAS_ID=os.environ.get("BEDROCK_AGENT_ALIAS_ID", "").strip(),
            RAG_BACKEND="local",
            USE_BEDROCK=False,
        )
