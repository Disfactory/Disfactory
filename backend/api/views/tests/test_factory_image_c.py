from uuid import uuid4
from datetime import datetime, timezone, timedelta

from freezegun import freeze_time
from django.test import TestCase, Client

from api.models import Factory, Image, ReportRecord


FAKE_IMGUR_PATH = "https://i.imgur.com/RxArJUc.png"


class PostFactoryImageViewTestCase(TestCase):
    def setUp(self):
        self.cli = Client()
        self.factory = Factory.objects.create(
            name="test_factory",
            lat=24,
            lng=121,
            status_time=datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone(timedelta(hours=8))),
            display_number=666,
        )
        self.nickname = "somebody"
        self.contact = "0900000000"
        self.fake_url = "https://i.imgur.com/123456.png"
        self.fake_lat = 23.12
        self.fake_lng = 121.5566
        self.fake_datetime_str = "2020:03:21 12:33:59"
        self.fake_datetime = datetime.strptime(
            self.fake_datetime_str,
            "%Y:%m:%d %H:%M:%S",
        ).replace(tzinfo=timezone(timedelta(hours=8)))
        self.post_body = {
            "url": self.fake_url,
            "Latitude": self.fake_lat,
            "Longitude": self.fake_lng,
            "DateTimeOriginal": self.fake_datetime_str,
            "nickname": self.nickname,
            "contact": self.contact,
        }

    def test_image_upload_db_correct(self):
        test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone(timedelta(hours=8)))
        with freeze_time(test_time):
            resp = self.cli.post(
                f"/api/factories/{self.factory.id}/images",
                self.post_body,
                content_type="application/json",
            )

        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()

        img_id = resp_data["id"]
        img = Image.objects.get(pk=img_id)
        self.assertEqual(img.image_path, self.fake_url)
        self.assertEqual(img.created_at, test_time)
        self.assertEqual(img.orig_time, self.fake_datetime)
        self.assertEqual(img.orig_lat, self.fake_lat)
        self.assertEqual(img.orig_lng, self.fake_lng)
        self.assertEqual(img.factory_id, self.factory.id)

        report_record_id = img.report_record_id
        self.assertIsNotNone(report_record_id)
        report_record = ReportRecord.objects.get(pk=report_record_id)
        self.assertEqual(report_record.factory_id, self.factory.id)
        self.assertEqual(report_record.action_type, "POST_IMAGE")
        self.assertEqual(report_record.nickname, self.nickname)
        self.assertEqual(report_record.contact, self.contact)

    def test_return_400_if_url_not_provided(self):
        wrong_body = {
            "Latitude": self.fake_lat,
            "Longitude": self.fake_lng,
            "DateTimeOriginal": self.fake_datetime_str,
            "nickname": self.nickname,
            "contact": self.contact,
        }
        resp = self.cli.post(
            f"/api/factories/{self.factory.id}/images",
            wrong_body,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 400)

    def test_return_400_if_factory_id_not_exist(self):
        cli = Client()
        not_exist_factory_id = uuid4()
        resp = cli.post(
            f"/api/factories/{not_exist_factory_id}/images",
            self.post_body,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 400)
        expected_msg = f"Factory ID {not_exist_factory_id} does not exist."
        self.assertEqual(resp.content, expected_msg.encode("utf8"))
