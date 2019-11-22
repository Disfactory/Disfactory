from datetime import datetime, timezone

from django.test import TestCase, Client
from django.conf import settings
from django.contrib.gis.geos import Point
from freezegun import freeze_time

from api.models import Factory, ReportRecord


class PutUpdateFactoryAttribute(TestCase):

    def setUp(self):
        self.factory = Factory.objects.create(
            name="test_factory",
            lat=24,
            lng=121,
            status_time=datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc),
        )

    def test_update_factory_normal_attribute(self):
        self.assertEqual(self.factory.name, "test_factory")
        self.assertEqual(self.factory.lat, 24)
        self.assertEqual(self.factory.lng, 121)
        cli = Client()
        put_body = {
            "name": "correct_factory",
            "factory_type": "6",
        }
        resp = cli.put(f"/api/factories/{self.factory.id}", data=put_body, content_type="application/json")
        self.assertEqual(resp.status_code, 200)

        factory = Factory.objects.get(pk=self.factory.id)
        self.assertEqual(factory.name, "correct_factory")
        self.assertEqual(factory.lat, 24)
        self.assertEqual(factory.lng, 121)
        self.assertEqual(factory.factory_type, "6")

        report_records = ReportRecord.objects.filter(factory_id=self.factory.id)
        self.assertEqual(len(report_records), 1)
        self.assertEqual(report_records[0].action_type, "UPDATE")
        self.assertEqual(report_records[0].action_body, put_body)

    def test_update_factory_with_contact(self):
        self.assertEqual(self.factory.name, "test_factory")
        self.assertEqual(self.factory.lat, 24)
        self.assertEqual(self.factory.lng, 121)
        cli = Client()
        put_body = {
            "name": "correct_factory",
            "factory_type": "6",
            "contact": "0800092000",
            "others": "這工廠讓我坐骨神經痛",
        }
        resp = cli.put(f"/api/factories/{self.factory.id}", data=put_body, content_type="application/json")
        self.assertEqual(resp.status_code, 200)

        factory = Factory.objects.get(pk=self.factory.id)
        self.assertEqual(factory.name, "correct_factory")
        self.assertEqual(factory.lat, 24)
        self.assertEqual(factory.lng, 121)
        self.assertEqual(factory.factory_type, "6")

        report_records = ReportRecord.objects.filter(factory_id=self.factory.id)
        self.assertEqual(len(report_records), 1)
        self.assertEqual(report_records[0].action_type, "UPDATE")
        self.assertEqual(report_records[0].action_body, put_body)
        self.assertEqual(report_records[0].contact, "0800092000")
        self.assertEqual(report_records[0].others, "這工廠讓我坐骨神經痛")

    def test_update_factory_status(self):
        cli = Client()
        put_body = {
            "status": "A",
        }
        test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc)
        with freeze_time(test_time):
            resp = cli.put(
                f"/api/factories/{self.factory.id}",
                data=put_body,
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, 200)

        factory = Factory.objects.get(pk=self.factory.id)
        self.assertEqual(factory.status, "A")
        self.assertEqual(factory.status_time, test_time)

    def test_update_factory_lat_or_lng_should_have_new_point(self):
        self.assertEqual(self.factory.lat, 24)
        self.assertEqual(self.factory.lng, 121)
        cli = Client()
        put_body = {
            "lat": 24.5,
            "lng": 121.5,
        }
        resp = cli.put(
            f"/api/factories/{self.factory.id}",
            data=put_body,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

        factory = Factory.objects.get(pk=self.factory.id)
        self.assertEqual(factory.lat, 24.5)
        self.assertEqual(factory.lng, 121.5)

        pnt = Point(121.5, 24.5, srid=4326)
        pnt.transform(settings.POSTGIS_SRID)
        self.assertEqual(factory.point, pnt)

    def test_400_if_wrong_data(self):
        cli = Client()
        put_body = {
            "lat": 90,
        }
        resp = cli.put(
            f"/api/factories/{self.factory.id}",
            data=put_body,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

        put_body = {
            "lng": 10,
        }
        resp = cli.put(
            f"/api/factories/{self.factory.id}",
            data=put_body,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
