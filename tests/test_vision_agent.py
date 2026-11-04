import io

from PIL import Image

from src.vision_agent import ImageError, MAX_SIDE, prepare_image


def _img_bytes(size=(2000, 1500), fmt="JPEG", mode="RGB", exif=None):
    img = Image.new(mode, size, "red")
    buf = io.BytesIO()
    kwargs = {"exif": exif} if exif else {}
    img.save(buf, format=fmt, **kwargs)
    return buf.getvalue()


def _code(fn):
    try:
        fn()
    except ImageError as e:
        return e.code
    return None


def test_big_photo_is_shrunk_and_stays_jpeg():
    img = Image.open(io.BytesIO(prepare_image(_img_bytes())))
    assert img.format == "JPEG" and max(img.size) == MAX_SIDE


def test_small_photo_is_not_enlarged():
    assert Image.open(io.BytesIO(prepare_image(_img_bytes((400, 300))))).size == (400, 300)


def test_transparent_png_becomes_jpeg():
    assert Image.open(io.BytesIO(prepare_image(_img_bytes((300, 300), "PNG", "RGBA")))).format == "JPEG"


def test_metadata_is_removed():
    exif = Image.Exif()
    exif[271] = "SecretPhoneBrand"
    tagged = _img_bytes((300, 300), exif=exif.tobytes())
    assert Image.open(io.BytesIO(tagged)).getexif().get(271) == "SecretPhoneBrand"
    assert not Image.open(io.BytesIO(prepare_image(tagged))).getexif()


def test_bad_inputs_are_rejected():
    assert _code(lambda: prepare_image(b"not an image")) == "unreadable"
    assert _code(lambda: prepare_image(_img_bytes((300, 300), "GIF", "P"))) == "bad_type"
    assert _code(lambda: prepare_image(_img_bytes((50, 50)))) == "too_small"
    assert _code(lambda: prepare_image(b"0" * (5 * 1024 * 1024 + 1))) == "too_large"
