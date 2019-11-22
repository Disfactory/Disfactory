from datetime import datetime, timezone
from unittest.mock import patch
from pathlib import Path

from freezegun import freeze_time
from django.test import TestCase, Client
from django.conf import settings

from api.models import Image


HERE = Path(__file__).resolve().parent
FAKE_IMGUR_PATH = "https://i.imgur.com/RxArJUc.png"


class PostImageViewTestCase(TestCase):

    @patch("api.views.image_c._upload_image", return_value=FAKE_IMGUR_PATH)
    def test_image_with_exif_db_correct(self, patch_upload):
        cli = Client()
        test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc)
        with freeze_time(test_time):
            with open(HERE / "20180311_132133.jpg", "rb") as f_img:
                resp = cli.post("/api/images", {'image': f_img}, format='multipart')

        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()
        self.assertIn('token', resp_data)

        img_id = resp_data['token']
        img = Image.objects.get(pk=img_id)
        self.assertEqual(img.image_path, FAKE_IMGUR_PATH)
        self.assertEqual(img.created_at, test_time)
        self.assertEqual(img.orig_time, datetime(2018, 3, 11, 13, 21, 33, tzinfo=timezone.utc))

    @patch("api.views.image_c._get_image_original_date", return_value=None)
    @patch("api.views.image_c._upload_image", return_value=FAKE_IMGUR_PATH)
    def test_image_without_exif_db_correct(self, patch_upload, _):
        cli = Client()
        test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc)
        with freeze_time(test_time):
            with open(HERE / "20180311_132133.jpg", "rb") as f_img:
                resp = cli.post("/api/images", {'image': f_img}, format='multipart')

        resp_data = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertIn('token', resp_data)

        img_id = resp_data['token']
        img = Image.objects.get(pk=img_id)
        self.assertEqual(img.image_path, FAKE_IMGUR_PATH)
        self.assertEqual(img.created_at, test_time)
        self.assertIsNone(img.orig_time)

    @patch("api.views.image_c._upload_image", return_value=FAKE_IMGUR_PATH)
    def test_return_400_if_not_image(self, patch_upload):
        cli = Client()
        with open(HERE / "test_image_c.py", "rb") as f_img:
            resp = cli.post("/api/images", {'image': f_img}, format='multipart')

        self.assertEqual(resp.status_code, 400)
