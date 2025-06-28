from django.conf import settings
from django.forms import ValidationError
from django.template.defaultfilters import filesizeformat
import magic


def validate_image_mime_type(file):
    allowed_mimes = [
        "image/jpeg",
        "image/png",
        "image/jpg",
    ]

    try:
        file.seek(0)
        buffer = file.read(1024)
        file.seek(0)
        mime_type = magic.from_buffer(buffer, mime=True)

        if mime_type not in allowed_mimes:
            raise ValidationError("file not supported")
    except (magic.MagicException, Exception):
        raise ValidationError(f"Error occured please try again")


def validate_file_size(file):
    max_size_mb = getattr(
        settings, "MAX_UPLOAD_SIZE_MB", 1
    )  # Taille max par défaut de 5MB
    max_size_bytes = max_size_mb * 1024 * 1024

    if file.size > max_size_bytes:
        raise ValidationError(f"max file size is {filesizeformat(max_size_bytes)}.")
