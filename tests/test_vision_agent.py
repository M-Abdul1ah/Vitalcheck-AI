import io

from PIL import Image

from src.vision_agent import ImageError, MAX_SIDE, prepare_image, to_data_url


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


def run():
    # big photo is shrunk and stays a valid JPEG
    out = prepare_image(_img_bytes())
    img = Image.open(io.BytesIO(out))
    assert img.format == "JPEG" and max(img.size) == MAX_SIDE

    # small photo is not enlarged
    assert Image.open(io.BytesIO(prepare_image(_img_bytes((400, 300))))).size == (400, 300)

    # PNG with transparency becomes a normal JPEG
    assert Image.open(io.BytesIO(prepare_image(_img_bytes((300, 300), "PNG", "RGBA")))).format == "JPEG"

    # metadata (camera / GPS tags) is removed
    exif = Image.Exif()
    exif[271] = "SecretPhoneBrand"
    tagged = _img_bytes((300, 300), exif=exif.tobytes())
    assert Image.open(io.BytesIO(tagged)).getexif().get(271) == "SecretPhoneBrand"
    assert not Image.open(io.BytesIO(prepare_image(tagged))).getexif()

    # bad inputs
    assert _code(lambda: prepare_image(b"not an image")) == "unreadable"
    assert _code(lambda: prepare_image(_img_bytes((300, 300), "GIF", "P"))) == "bad_type"
    assert _code(lambda: prepare_image(_img_bytes((50, 50)))) == "too_small"
    assert _code(lambda: prepare_image(b"0" * (5 * 1024 * 1024 + 1))) == "too_large"

    assert to_data_url(out).startswith("data:image/jpeg;base64,")
    print("vision tests passed")


if __name__ == "__main__":
    run()
