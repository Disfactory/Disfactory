from datetime import datetime

from PIL import Image, ExifTags


def _get_image_original_date(f_image):
    img = Image.open(f_image)

    exif_raw = img._getexif()
    if exif_raw is None:
        return None

    exif = {}
    for k, v in exif_raw.items():
        if k in ExifTags.TAGS:
            exif[ExifTags.TAGS[k]] = v

    try:
        return datetime.strptime(exif["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
    except Exception:
        return None


def _is_image(f_image):
    try:
        Image.open(f_image)
        return True
    except IOError:
        return False
