from datetime import datetime
from pathlib import Path

from django.test import TestCase

from ..utils import _get_image_original_date, _is_image

HERE = Path(__file__).resolve().parent


class MiscellaneousTestCase(TestCase):
    def test_get_image_original_date(self):
        img_path = HERE / "20180311_132133.jpg"
        with open(img_path, "rb") as f_img:
            img_date = _get_image_original_date(f_img)
        self.assertEqual(img_date, datetime(2018, 3, 11, 13, 21, 33))

    def test_get_image_original_date_if_no_exif(self):
        img_path = HERE / "20180311_132133_noexif.jpg"
        with open(img_path, "rb") as f_img:
            img_date = _get_image_original_date(f_img)
        self.assertIsNone(img_date)

    def test_is_image(self):
        img_path = HERE / "20180311_132133.jpg"
        with open(img_path, "rb") as f_img:
            self.assertTrue(_is_image(f_img))

    def test_is_not_image(self):
        img_path = HERE / "test_utils.py"
        with open(img_path, "rb") as f_img:
            self.assertFalse(_is_image(f_img))
