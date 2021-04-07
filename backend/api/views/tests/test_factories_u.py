from datetime import datetime, timezone
from uuid import uuid4

from django.test import TestCase, Client
from freezegun import freeze_time

from api.models import Factory, ReportRecord


class PutUpdateFactoryAttribute(TestCase):
    def setUp(self):
        self.factory = Factory.objects.create(
            name="test_factory",
            lat=24,
            lng=121,
            status_time=datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc),
            display_number=666,
        )

    def test_update_factory_normal_attribute(self):
        assert self.factory.name == "test_factory"
        assert self.factory.lat == 24
        assert self.factory.lng == 121
        cli = Client()
        put_body = {
            "name": "correct_factory",
            "factory_type": "6",
        }
        resp = cli.put(
            f"/api/factories/{self.factory.id}", data=put_body, content_type="application/json"
        )
        assert resp.status_code == 200

        factory = Factory.objects.get(pk=self.factory.id)
        assert factory.name == "correct_factory"
        assert factory.lat == 24
        assert factory.lng == 121
        assert factory.factory_type == "6"

        report_records = ReportRecord.objects.filter(factory_id=self.factory.id)
        assert len(report_records) == 1
        assert report_records[0].action_type == "UPDATE"
        assert report_records[0].action_body == put_body

    def test_update_factory_with_contact(self):
        assert self.factory.name == "test_factory"
        assert self.factory.lat == 24
        assert self.factory.lng == 121
        cli = Client()
        put_body = {
            "name": "correct_factory",
            "factory_type": "6",
            "contact": "0800092000",
            "others": "這工廠讓我坐骨神經痛",
        }
        resp = cli.put(
            f"/api/factories/{self.factory.id}", data=put_body, content_type="application/json"
        )
        assert resp.status_code == 200

        factory = Factory.objects.get(pk=self.factory.id)
        assert factory.name == "correct_factory"
        assert factory.lat == 24
        assert factory.lng == 121
        assert factory.factory_type == "6"

        report_records = ReportRecord.objects.filter(factory_id=self.factory.id)
        assert len(report_records) == 1
        assert report_records[0].action_type == "UPDATE"
        assert report_records[0].action_body == put_body
        assert report_records[0].contact == "0800092000"
        assert report_records[0].others == "這工廠讓我坐骨神經痛"

    def test_update_factory_status(self):
        cli = Client()
        put_body = {
            "cet_report_status": "P",
        }
        test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc)
        with freeze_time(test_time):
            resp = cli.put(
                f"/api/factories/{self.factory.id}",
                data=put_body,
                content_type="application/json",
            )
        assert resp.status_code == 200

        factory = Factory.objects.get(pk=self.factory.id)
        assert factory.cet_report_status == "P"

    def test_update_factory_lat_or_lng_should_have_new_point(self):
        assert self.factory.lat == 24
        assert self.factory.lng == 121
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
        assert resp.status_code == 400
        assert resp.content == b"Factory position cannot be modified."

    def test_get_single_factory(self):
        cli = Client()
        resp = cli.get(f"/api/factories/{self.factory.id}")
        resp_data = resp.json()
        assert resp_data["name"] == self.factory.name
        assert resp_data["lat"] == self.factory.lat
        assert resp_data["lng"] == self.factory.lng
        assert resp_data["cet_report_status"] == self.factory.cet_report_status

    def test_get_single_factory_not_exist(self):
        cli = Client()
        not_existed_code = uuid4()
        resp = cli.get(f"/api/factories/{not_existed_code}")

        assert resp.status_code == 400
