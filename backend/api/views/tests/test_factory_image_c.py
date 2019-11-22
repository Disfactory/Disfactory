from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch
from pathlib import Path

from freezegun import freeze_time
from django.test import TestCase, Client
from django.conf import settings

from api.models import Factory, Image, ReportRecord


HERE = Path(__file__).resolve().parent
FAKE_IMGUR_PATH = "https://i.imgur.com/RxArJUc.png"


class PostFactoryImageViewTestCase(TestCase):

    def setUp(self):
        self.factory = Factory.objects.create(
            name="test_factory",
            lat=24,
            lng=121,
            status_time=datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc),
        )

    @patch("api.views.factory_image_c._upload_image", return_value=FAKE_IMGUR_PATH)
    def test_image_with_exif_db_correct(self, patch_upload):
        cli = Client()
        test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc)
        with freeze_time(test_time):
            with open(HERE / "20180311_132133.jpg", "rb") as f_img:
                resp = cli.post(
                    f"/api/factories/{self.factory.id}/images",
                    {'image': f_img},
                    format='multipart',
                )

        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()

        img_id = resp_data['id']
        img = Image.objects.get(pk=img_id)
        self.assertEqual(img.image_path, FAKE_IMGUR_PATH)
        self.assertEqual(img.created_at, test_time)
        self.assertEqual(img.orig_time, datetime(2018, 3, 11, 13, 21, 33, tzinfo=timezone.utc))
        self.assertEqual(img.factory_id, self.factory.id)

        report_record_id = img.report_record_id
        self.assertIsNotNone(report_record_id)
        report_record = ReportRecord.objects.get(pk=report_record_id)
        self.assertEqual(report_record.factory_id, self.factory.id)
        self.assertEqual(report_record.action_type, "POST_IMAGE")

    @patch("api.views.factory_image_c._upload_image", return_value=FAKE_IMGUR_PATH)
    def test_image_without_exif_db_correct(self, patch_upload):
        cli = Client()
        test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc)
        with freeze_time(test_time):
            with open(HERE / "20180311_132133_noexif.jpg", "rb") as f_img:
                resp = cli.post(
                    f"/api/factories/{self.factory.id}/images",
                    {'image': f_img},
                    format='multipart',
                )

        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()

        img_id = resp_data['id']
        img = Image.objects.get(pk=img_id)
        self.assertEqual(img.image_path, FAKE_IMGUR_PATH)
        self.assertEqual(img.created_at, test_time)
        self.assertIsNone(img.orig_time)
        self.assertEqual(img.factory_id, self.factory.id)

        report_record_id = img.report_record_id
        self.assertIsNotNone(report_record_id)
        report_record = ReportRecord.objects.get(pk=report_record_id)
        self.assertEqual(report_record.factory_id, self.factory.id)
        self.assertEqual(report_record.action_type, "POST_IMAGE")

    @patch("api.views.factory_image_c._upload_image", return_value=FAKE_IMGUR_PATH)
    def test_return_400_if_not_image(self, patch_upload):
        cli = Client()
        with open(HERE / "test_factory_image_c.py", "rb") as f_img:
            resp = cli.post(
                f"/api/factories/{self.factory.id}/images",
                {'image': f_img},
                format='multipart',
            )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, b'The uploaded file cannot be parsed to Image')

    def test_return_400_if_factory_id_not_exist(self):
        cli = Client()

        not_exist_factory_id = uuid4()
        with open(HERE / "20180311_132133_noexif.jpg", "rb") as f_img:
            resp = cli.post(
                f"/api/factories/{not_exist_factory_id}/images",
                {'image': f_img},
                format='multipart',
            )

        self.assertEqual(resp.status_code, 400)
        expected_msg = f'Factory ID {not_exist_factory_id} does not exist.'
        self.assertEqual(resp.content, expected_msg.encode('utf8'))
