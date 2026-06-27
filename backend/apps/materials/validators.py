from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError


PDF_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}
ARCHIVE_CONTENT_TYPES = {"application/zip", "application/x-zip-compressed", "application/vnd.rar", "application/x-rar-compressed"}
RESOURCE_CONTENT_TYPES = {
    *PDF_CONTENT_TYPES,
    *ARCHIVE_CONTENT_TYPES,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "text/csv",
    "text/x-python",
    "application/x-ipynb+json",
    "application/json",
}


def validate_upload_size(value) -> None:
    max_size = getattr(settings, "MAX_UPLOAD_SIZE", 50 * 1024 * 1024)
    if value.size and value.size > max_size:
        raise ValidationError(f"File is too large. Maximum allowed size is {max_size // (1024 * 1024)} MB.")


def validate_content_type(value, allowed: set[str]) -> None:
    content_type = getattr(value.file, "content_type", None) or getattr(value, "content_type", None)
    if content_type and content_type not in allowed:
        raise ValidationError("Unsupported file content type.")


def validate_pdf_file(value) -> None:
    validate_upload_size(value)
    if Path(value.name).suffix.lower() != ".pdf":
        raise ValidationError("Only PDF files are allowed.")
    validate_content_type(value, PDF_CONTENT_TYPES)


def validate_archive_file(value) -> None:
    validate_upload_size(value)
    if Path(value.name).suffix.lower() not in {".zip", ".rar"}:
        raise ValidationError("Only ZIP or RAR archives are allowed.")
    validate_content_type(value, ARCHIVE_CONTENT_TYPES)


def validate_resource_file(value) -> None:
    validate_upload_size(value)
    allowed = {".pdf", ".docx", ".pptx", ".zip", ".rar", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".csv", ".py", ".ipynb"}
    if Path(value.name).suffix.lower() not in allowed:
        raise ValidationError("Unsupported resource file type.")
    validate_content_type(value, RESOURCE_CONTENT_TYPES)
