"""
Vision agent, step 1: prepare the user's photo (the skin model DermaVC-Net will read the result).
Checks the file, removes hidden metadata (GPS, camera info), fixes rotation,
shrinks it and returns a small JPEG. The photo is never written to disk.
"""
import io

from PIL import Image, ImageOps, UnidentifiedImageError

Image.MAX_IMAGE_PIXELS = 50_000_000   # refuse "decompression bomb" images

MAX_BYTES = 5 * 1024 * 1024   # largest upload accepted
MAX_SIDE = 1024               # longest side after resizing (small, fast input for the skin model)
MIN_SIDE = 100                # smaller than this is too blurry to describe
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class ImageError(ValueError):
    """code is one of: too_large, bad_type, unreadable, too_small."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def prepare_image(data: bytes) -> bytes:
    """Return a cleaned, resized JPEG (bytes) or raise ImageError."""
    if len(data) > MAX_BYTES:
        raise ImageError("too_large")
    try:
        img = Image.open(io.BytesIO(data))
        if img.format not in ALLOWED_FORMATS:
            raise ImageError("bad_type")
        img.load()
    except ImageError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, ValueError):
        raise ImageError("unreadable")

    img = ImageOps.exif_transpose(img)   # fix phone-camera rotation
    if min(img.size) < MIN_SIDE:
        raise ImageError("too_small")

    if img.mode in ("RGBA", "LA", "P"):  # flatten transparency onto white
        img = img.convert("RGBA")
        background = Image.new("RGB", img.size, "white")
        background.paste(img, mask=img.split()[-1])
        img = background
    else:
        img = img.convert("RGB")

    img.thumbnail((MAX_SIDE, MAX_SIDE))  # only shrinks, never enlarges
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=85)   # saving without exif= drops all metadata
    return out.getvalue()
