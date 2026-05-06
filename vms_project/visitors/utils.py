# visitors/utils.py
import base64
import uuid
import io
import os

from django.core.files.base import ContentFile
from django.core import signing
from django.conf import settings

from PIL import Image

# Optional QR support
try:
    import qrcode
except Exception:
    qrcode = None


# ------------------------------------------------------------------------------
# QR CODE HELPERS
# ------------------------------------------------------------------------------

def generate_qr_image_bytes(data: str, box_size: int = 10, border: int = 4) -> (bytes, str):
    """
    Return PNG bytes of a QR code and a suggested filename.
    Requires: qrcode[pil], pillow
    """
    if not qrcode:
        raise RuntimeError("qrcode library not installed. Run: pip install qrcode[pil]")

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    filename = f"qr_{uuid.uuid4().hex}.png"
    return buffer.read(), filename


def save_qr_to_filefield(visit, data_for_qr, field_name='qr_code'):
    """
    Generate QR and save to ImageField on a model instance.
    """
    png_bytes, filename = generate_qr_image_bytes(data_for_qr)
    content = ContentFile(png_bytes, name=filename)

    getattr(visit, field_name).save(filename, content, save=False)
    return getattr(visit, field_name).name


# ------------------------------------------------------------------------------
# TOKEN HELPERS
# ------------------------------------------------------------------------------

TOKEN_SALT = getattr(settings, 'VMS_TOKEN_SALT', 'vms-approve-salt')
TOKEN_MAX_AGE = getattr(settings, 'VMS_TOKEN_MAX_AGE', 60 * 60 * 24)  # 1 day


def make_approval_token(data: dict) -> str:
    """
    Create a signed token for approval links.
    """
    return signing.dumps(data, salt=TOKEN_SALT)


def load_approval_token(token: str, max_age: int = None) -> dict:
    max_age = max_age or TOKEN_MAX_AGE
    return signing.loads(token, salt=TOKEN_SALT, max_age=max_age)


# ------------------------------------------------------------------------------
# IMAGE DATA URL HANDLER (Python 3.13 SAFE)
# ------------------------------------------------------------------------------

def _save_photo_from_dataurl(dataurl, name_prefix='img'):
    """
    Accepts a data URL (data:image/png;base64,...)
    Returns: (filename, ContentFile)

    Usage:
        filename, content = _save_photo_from_dataurl(dataurl, 'visitor')
        instance.photo.save(filename, content, save=False)
    """

    if not dataurl or not isinstance(dataurl, str):
        raise ValueError("Expected dataurl string")

    if not dataurl.startswith('data:'):
        raise ValueError("Invalid dataurl (missing data: prefix)")

    try:
        header, b64data = dataurl.split(',', 1)
    except ValueError:
        raise ValueError("Malformed dataurl")

    # Decode base64
    try:
        binary = base64.b64decode(b64data)
    except Exception as e:
        raise ValueError("Base64 decode failed") from e

    # Load image with Pillow (replaces imghdr)
    try:
        image = Image.open(io.BytesIO(binary))
        image.verify()  # Validate image
        image = Image.open(io.BytesIO(binary))  # Reload after verify
    except Exception as e:
        raise ValueError("Invalid image data") from e

    # Get extension from actual image format
    ext = (image.format or "PNG").lower()
    ext = ext.replace("jpeg", "jpg")

    filename = f"{name_prefix}_{uuid.uuid4().hex}.{ext}"
    content = ContentFile(binary, name=filename)

    return filename, content