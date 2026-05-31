"""Typed config loaded from environment variables (with .env fallback)."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


class ConfigError(RuntimeError):
    """Raised when required environment variables are missing or invalid."""


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class Config:
    AWS_REGION: str
    BEDROCK_KB_ID: str
    BEDROCK_MODEL_ARN: str
    BEDROCK_NUM_RESULTS: int
    SECRET_KEY: str
    FLASK_ENV: str
    S3_BUCKET: str = ""
    S3_PREFIX: str = "projects/incident-rag-bedrock/data/sample_documents"
    BEDROCK_DATA_SOURCE_ID: str = ""
    MAX_UPLOAD_BYTES: int = 5_242_880

    @classmethod
    def from_env(cls) -> "Config":
        max_upload = os.environ.get("MAX_UPLOAD_BYTES", "5242880").strip()
        return cls(
            AWS_REGION=_require("AWS_REGION"),
            BEDROCK_KB_ID=_require("BEDROCK_KB_ID"),
            BEDROCK_MODEL_ARN=_require("BEDROCK_MODEL_ARN"),
            BEDROCK_NUM_RESULTS=int(os.environ.get("BEDROCK_NUM_RESULTS", "5")),
            SECRET_KEY=_require("FLASK_SECRET_KEY"),
            FLASK_ENV=os.environ.get("FLASK_ENV", "production"),
            S3_BUCKET=os.environ.get("S3_BUCKET", "").strip(),
            S3_PREFIX=os.environ.get(
                "S3_PREFIX", "projects/incident-rag-bedrock/data/sample_documents"
            ).strip(),
            BEDROCK_DATA_SOURCE_ID=os.environ.get("BEDROCK_DATA_SOURCE_ID", "").strip(),
            MAX_UPLOAD_BYTES=int(max_upload),
        )
