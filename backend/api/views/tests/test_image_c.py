from datetime import datetime, timezone, timedelta

from django.test import TestCase, Client
from freezegun import freeze_time

from api.models import Image


class PostImageUrlViewTestCase(TestCase):
    def setUp(self):
        self.cli = Client()

    def test_post_image_url(self):
        fake_url = "https://i.imgur.com/123456.png"
        fake_lat = 23.12
        fake_lng = 121.5566
        fake_datetime_str = "2020:03:21 12:33:59"
        fake_deletehash = "asdjiwenvnxcvj;"
        fake_datetime = datetime.strptime(
            fake_datetime_str,
            "%Y:%m:%d %H:%M:%S",
        ).replace(tzinfo=timezone(timedelta(hours=8)))
        request_body = {
            "url": fake_url,
            "Latitude": fake_lat,
            "Longitude": fake_lng,
            "DateTimeOriginal": fake_datetime_str,
            "deletehash": fake_deletehash,
        }
        test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone(timedelta(hours=8)))
        with freeze_time(test_time):
            resp = self.cli.post(
                "/api/images",
                data=request_body,
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, 200)

        resp_data = resp.json()
        img_id = resp_data["token"]
        img = Image.objects.get(pk=img_id)
        self.assertEqual(img.image_path, fake_url)
        self.assertEqual(img.created_at, test_time)
        self.assertEqual(img.orig_time, fake_datetime)
        self.assertEqual(img.orig_lat, fake_lat)
        self.assertEqual(img.orig_lng, fake_lng)

    def test_post_image_url_400_if_no_url(self):
        fake_lat = 23.12
        fake_lng = 121.5566
        fake_datetime_str = "2020:03:21 12:33:59"
        fake_deletehash = "asdjiwenvnxcvj;"
        request_body = {
            "Latitude": fake_lat,
            "Longitude": fake_lng,
            "DateTimeOriginal": fake_datetime_str,
            "deletehash": fake_deletehash,
        }
        test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone(timedelta(hours=8)))
        with freeze_time(test_time):
            resp = self.cli.post(
                "/api/images",
                data=request_body,
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, 400)
