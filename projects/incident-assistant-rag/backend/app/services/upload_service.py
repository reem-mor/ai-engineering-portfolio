from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class UploadService:
    async def save_upload(self, file: UploadFile) -> tuple[str, int]:
        if not file.filename:
            raise ValueError("Uploaded file must have a filename.")
        suffix = Path(file.filename).suffix.lower()
        if suffix not in settings.allowed_file_extensions:
            raise ValueError(f"Unsupported file type: {suffix}")
        settings.raw_data_dir.mkdir(parents=True, exist_ok=True)
        saved_filename = f"{uuid4().hex}{suffix}"
        output_path = settings.raw_data_dir / saved_filename
        size = 0
        too_large = False
        with output_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.max_upload_size_bytes:
                    too_large = True
                    break
                buffer.write(chunk)
        if too_large:
            # Unlink after the output file is closed (Windows locks open files).
            output_path.unlink(missing_ok=True)
            raise ValueError("File is too large.")
        if size == 0:
            output_path.unlink(missing_ok=True)
            raise ValueError("File is empty.")
        return saved_filename, size
