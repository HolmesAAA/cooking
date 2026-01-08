from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io
from typing import Optional
from config import settings
import logging

logger = logging.getLogger(__name__)


def validate_file_type(file: UploadFile) -> str:
    """
    Validate file type and return media type (image or video)
    """
    content_type = file.content_type.lower()

    if content_type in settings.allowed_image_types_list:
        return "image"
    elif content_type in settings.allowed_video_types_list:
        return "video"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{content_type}' is not allowed. Allowed types: {settings.allowed_image_types}, {settings.allowed_video_types}",
        )


def validate_file_size(file: UploadFile, max_size: int = None) -> int:
    """
    Validate file size and return size in bytes
    """
    if max_size is None:
        max_size = settings.max_file_size_bytes

    # Read file to get size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Seek back to beginning

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed size ({max_size / (1024 * 1024):.0f} MB)",
        )

    return file_size


def generate_thumbnail(image_data: bytes, max_size: tuple = (300, 300)) -> Optional[bytes]:
    """
    Generate thumbnail from image data
    Returns thumbnail as bytes or None if failed
    """
    try:
        # Open image
        image = Image.open(io.BytesIO(image_data))

        # Convert RGBA to RGB if necessary
        if image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
            image = background

        # Generate thumbnail
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save to bytes
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=85, optimize=True)
        output.seek(0)

        return output.read()

    except Exception as e:
        logger.error(f"Failed to generate thumbnail: {e}")
        return None


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
