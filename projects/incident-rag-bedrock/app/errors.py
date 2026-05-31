"""Map low-level boto3 errors to user-safe messages."""
from __future__ import annotations

from botocore.exceptions import BotoCoreError, ClientError


class BedrockError(Exception):
    """Raised by BedrockRagClient for any user-presentable failure."""

    def __init__(self, user_message: str, *, code: str = "bedrock_error") -> None:
        super().__init__(user_message)
        self.user_message = user_message
        self.code = code


_FRIENDLY = {
    "ThrottlingException": "Bedrock is throttling requests. Please try again in a moment.",
    "AccessDeniedException": "The server is not authorized to call Bedrock. Check IAM permissions.",
    "ValidationException": "The Bedrock request was rejected as invalid. Try a shorter question.",
    "ResourceNotFoundException": "The configured Knowledge Base or model could not be found.",
    "ServiceQuotaExceededException": "A Bedrock service quota was exceeded.",
    "NoSuchBucket": "The configured S3 bucket does not exist.",
    "AccessDenied": "S3 denied the upload. Check bucket policy and IAM PutObject permissions.",
}


def translate(exc: Exception) -> BedrockError:
    if isinstance(exc, ClientError):
        code = exc.response.get("Error", {}).get("Code", "ClientError")
        msg = _FRIENDLY.get(code, "Bedrock returned an unexpected error.")
        return BedrockError(msg, code=code)
    if isinstance(exc, BotoCoreError):
        return BedrockError("Could not reach AWS Bedrock. Check network or credentials.", code="botocore_error")
    return BedrockError("Unexpected server error while calling Bedrock.", code="unknown")
