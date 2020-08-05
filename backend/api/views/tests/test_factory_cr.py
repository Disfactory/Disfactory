import datetime
from unittest.mock import patch
from uuid import uuid4

from freezegun import freeze_time
from django.test import TestCase, Client
from django.conf import settings
from django.contrib.gis.geos import Point

from ...models import Factory, ReportRecord, Image


class GetNearbyOrCreateFactoriesViewTestCase(TestCase):

    def setUp(self):
        self.cli = Client()

    def test_get_nearby_factory_wrong_params(self):

        # case 1: missing parameter
        resp = self.cli.get("/api/factories?lat=23")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, b"Missing query parameter: lng, range.")

        resp = self.cli.get("/api/factories?lng=121&range=0.2")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, b"Missing query parameter: lat.")

        # case 2: not querying Taiwan
        resp = self.cli.get(
            "/api/factories?lat=39.9046126&lng=116.3977254&range=1")
        self.assertEqual(resp.status_code, 400)
        self.assertIn(
            b"The query position is not in the range of Taiwan.", resp.content)

        # case 3: wrong query radius
        resp = self.cli.get("/api/factories?lat=23&lng=121&range=10000")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            resp.content, b"`range` should be within 0.01 to 100 km, but got 10000.0")

        resp = self.cli.get("/api/factories?lat=23&lng=121&range=0.001")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            resp.content, b"`range` should be within 0.01 to 100 km, but got 0.001")

    def test_get_nearby_factory_called_util_func_correctly(self):

        with patch("api.views.factories_cr._get_nearby_factories") as mock_func:
            lat = 23.12
            lng = 121.5566
            r = 0.5
            self.cli.get(f"/api/factories?lat={lat}&lng={lng}&range={r}")

            mock_func.assert_called_once_with(
                latitude=lat,
                longitude=lng,
                radius=r,
            )

    def test_get_nearby_factory_called_on_test_data(self):

        # in sync with api/tests/test_models.py
        lat = 23.234
        lng = 120.1
        r = 1
        resp = self.cli.get(f"/api/factories?lat={lat}&lng={lng}&range={r}")
        self.assertEqual(resp.status_code, 200)

        factories = resp.json()
        self.assertEqual(len(factories), 9)
        self.assertCountEqual([f["name"] for f in factories], [
            "既有違章工廠 No.2",
            "既有違章工廠 No.3",
            "既有違章工廠 No.8",
            "既有違章工廠 No.9",
            "既有違章工廠 No.10",
            "既有違章工廠 No.11",
            "既有違章工廠 No.12",
            "既有違章工廠 No.13",
            "既有違章工廠 No.22",
        ])

    def test_create_new_factory_db_status_correct(self):
        lat = 23.234
        lng = 120.1
        others = "這個工廠實在太臭啦，趕緊檢舉吧"
        nickname = "路過的家庭主婦"
        contact = "07-7533967"
        factory_type = "2-3"
        im1 = Image.objects.create(
            image_path="https://i.imgur.com/RxArJUc.png")
        im2 = Image.objects.create(
            image_path="https://imgur.dcard.tw/BB2L2LT.jpg")
        im_not_related = Image.objects.create(
            image_path="https://i.imgur.com/T3pdEyR.jpg")
        request_body = {
            "name": "a new factory",
            "type": factory_type,
            "images": [str(im1.id), str(im2.id)],
            "others": others,
            "lat": lat,
            "lng": lng,
            "nickname": nickname,
            "contact": contact,
        }
        pnt = Point(lng, lat, srid=4326)
        pnt.transform(settings.POSTGIS_SRID)

        test_time = datetime.datetime(
            2019, 11, 11, 11, 11, 11, tzinfo=datetime.timezone.utc)
        with freeze_time(test_time):
            resp = self.cli.post(
                "/api/factories", data=request_body, content_type="application/json")

        self.assertEqual(resp.status_code, 200, resp.content)

        new_factory_id = resp.json()["id"]
        new_factory = Factory.objects.get(pk=new_factory_id)

        self.assertEqual(new_factory.lat, lat)
        self.assertEqual(new_factory.lng, lng)
        self.assertEqual(new_factory.point, pnt)
        self.assertEqual(new_factory.factory_type, factory_type)

        report_records = ReportRecord.objects.filter(factory_id=new_factory_id)
        self.assertEqual(len(report_records), 1)
        report_record = report_records[0]
        self.assertEqual(str(report_record.factory_id), new_factory_id)
        self.assertEqual(report_record.action_type, "POST")
        self.assertEqual(report_record.action_body, request_body)
        self.assertEqual(report_record.nickname, nickname)
        self.assertEqual(report_record.contact, contact)
        self.assertEqual(report_record.others, others)
        self.assertEqual(report_record.created_at, test_time)

        related_images = Image.objects.only(
            "factory_id").filter(id__in=[im1.id, im2.id])
        self.assertEqual(
            set([str(img.factory_id) for img in related_images]),
            set([new_factory_id]),
        )
        not_related_images = Image.objects.only(
            "factory_id").filter(id__in=[im_not_related.id])
        self.assertEqual(
            set([str(img.factory_id) for img in not_related_images]),
            set(['None']),
        )

    def test_create_new_factory_raise_if_image_id_not_exist(self):
        im1 = Image.objects.create(
            image_path="https://i.imgur.com/RxArJUc.png")
        Image.objects.create(image_path="https://imgur.dcard.tw/BB2L2LT.jpg")
        request_body = {
            "name": "a new factory",
            "type": "2-3",
            "images": [str(im1.id), str(uuid4())],
            "others": "這個工廠實在太臭啦，趕緊檢舉吧",
            "lat": 23.234,
            "lng": 120.1,
            "nickname": "路過的家庭主婦",
            "contact": "07-7533967",
        }
        resp = self.cli.post(
            "/api/factories", data=request_body, content_type="application/json")

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, b'please check if every image id exist')

    def test_create_new_factory_allow_no_contact(self):
        request_body = {
            "name": "a new factory",
            "type": "2-3",
            "images": [],
            "others": "",
            "lat": 23.234,
            "lng": 120.1,
            "nickname": "",
        }
        resp = self.cli.post(
            "/api/factories", data=request_body, content_type="application/json")

        self.assertEqual(resp.status_code, 200)

    def test_create_new_factory_raise_if_not_in_Taiwan(self):
        request_body = {
            "name": "a new factory",
            "type": "2-3",
            "images": [],
            "others": "",
            "lat": -23.234,
            "lng": 120.1,
            "nickname": "",
            "contact": "07-7533967",
        }
        resp = self.cli.post(
            "/api/factories", data=request_body, content_type="application/json")

        self.assertEqual(resp.status_code, 400)
        self.assertIn("lat", resp.json())

    def test_create_new_factory_raise_if_type_is_not_invalid(self):
        lat = 23.234
        lng = 120.1
        others = "這個工廠實在太臭啦，趕緊檢舉吧"
        nickname = "路過的家庭主婦"
        contact = "07-7533967"
        im1 = Image.objects.create(
            image_path="https://i.imgur.com/RxArJUc.png")
        im2 = Image.objects.create(
            image_path="https://imgur.dcard.tw/BB2L2LT.jpg")
        request_body = {
            "name": "a new factory",
            "type": "aaaaa",
            "images": [str(im1.id), str(im2.id)],
            "others": others,
            "lat": lat,
            "lng": lng,
            "nickname": nickname,
            "contact": contact,
        }

        resp = self.cli.post(
            "/api/factories",
            data=request_body,
            content_type="application/json"
        )

        self.assertEqual(resp.status_code, 400)
        self.assertIn("type", resp.json())
