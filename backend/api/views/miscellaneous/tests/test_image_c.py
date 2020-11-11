from datetime import datetime, timezone, timedelta
import json
from unittest.mock import patch
from pathlib import Path

from freezegun import freeze_time
from django.test import TestCase, Client
from django.conf import settings

from api.models import Image


HERE = Path(__file__).resolve().parent
FAKE_IMGUR_PATH = "https://i.imgur.com/RxArJUc.png"


class PostImageViewTestCase(TestCase):

    @patch("django_q.tasks.async_task")
    def test_image_with_exif_db_correct(self, patch_async_tasks):
        cli = Client()
        test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone(timedelta(hours=8)))
        with freeze_time(test_time):
            with open(HERE / "20180311_132133.jpg", "rb") as f_img:
                with patch('uuid.uuid4', return_value='temp_image'):
                    resp = cli.post("/api/legacy/images", {'image': f_img}, format='multipart')

        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()
        self.assertIn('token', resp_data)

        img_id = resp_data['token']
        img = Image.objects.get(pk=img_id)
        self.assertEqual(img.created_at, test_time)
        self.assertEqual(img.orig_time, datetime(2018, 3, 11, 13, 21, 33, tzinfo=timezone(timedelta(hours=8))))
        patch_async_tasks.assert_called_once_with(
            'api.tasks.upload_image',
            '/tmp/temp_image.jpg',
            settings.IMGUR_CLIENT_ID,
            img.id,
        )

    @patch("api.views.miscellaneous.image_c._get_image_original_date", return_value=None)
    @patch("django_q.tasks.async_task")
    def test_image_without_exif_db_correct(self, patch_async_tasks, _):
        cli = Client()
        test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone(timedelta(hours=8)))
        with freeze_time(test_time):
            with open(HERE / "20180311_132133.jpg", "rb") as f_img:
                with patch('uuid.uuid4', return_value='temp_image'):
                    resp = cli.post("/api/legacy/images", {'image': f_img}, format='multipart')

        resp_data = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertIn('token', resp_data)

        img_id = resp_data['token']
        img = Image.objects.get(pk=img_id)
        self.assertEqual(img.created_at, test_time)
        self.assertIsNone(img.orig_time)
        patch_async_tasks.assert_called_once_with(
            'api.tasks.upload_image',
            '/tmp/temp_image.jpg',
            settings.IMGUR_CLIENT_ID,
            img.id,
        )

    @patch("django_q.tasks.async_task")
    def test_return_400_if_not_image(self, _):
        cli = Client()
        with open(HERE / "test_image_c.py", "rb") as f_img:
            with patch('uuid.uuid4', return_value='temp_image'):
                resp = cli.post("/api/legacy/images", {'image': f_img}, format='multipart')

        self.assertEqual(resp.status_code, 400)

    @patch("django_q.tasks.async_task")
    def test_upload_img_url_directly(self, patch_async_tasks):
        cli = Client()
        fake_path = 'https://i.imgur.com/123456.png'
        fake_lat = 23.12
        fake_lng = 121.5566
        fake_datetime_str = "2020:03:21 12:33:59"
        post_data = {
            'data': {
                'path': fake_path,
                'exif': {
                    'Latitude': fake_lat,
                    'Longitude': fake_lng,
                    'DateTimeOriginal': fake_datetime_str,
                }
            }
        }
        with open(HERE / "20180311_132133.jpg", "rb") as f_img:
            resp = cli.post("/api/legacy/images", {
                'image': f_img,
                'json': json.dumps(post_data),
            }, format='multipart')

        self.assertEqual(resp.status_code, 200)
        patch_async_tasks.assert_not_called()

        resp_data = resp.json()
        img_id = resp_data['token']
        img = Image.objects.get(pk=img_id)
        self.assertEqual(img.image_path, fake_path)
        self.assertEqual(
            img.orig_time,
            datetime.strptime(fake_datetime_str, "%Y:%m:%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=8))),
        )
        self.assertEqual(img.orig_lat, fake_lat)
        self.assertEqual(img.orig_lng, fake_lng)
