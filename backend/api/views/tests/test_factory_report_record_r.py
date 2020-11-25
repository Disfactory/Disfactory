from datetime import datetime, timezone
from uuid import uuid4

from django.test import TestCase, Client

from api.models import Factory, ReportRecord


class GetFactoryReportRecordTestCase(TestCase):
    def setUp(self):
        self.factory = self.create_factory()
        self.cli = Client()

    def create_factory(self, display_number=None):
        return Factory.objects.create(
            name="test_factory",
            lat=24,
            lng=121,
            status_time=datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc),
            display_number=display_number or 666,
        )

    def create_report_record(self, factory, action_type=None, action_body=None):
        return ReportRecord.objects.create(
            factory=factory,
            action_type=action_type or "post_image",
            action_body=action_body or {},
            contact="0800-092000",
            others="猴～被我拍到了吧",
        )

    def test_get_correct_report_record_with_order(self):
        rr1 = self.create_report_record(self.factory)
        rr2 = self.create_report_record(self.factory)
        rr3 = self.create_report_record(self.factory)

        factory2 = self.create_factory(777)
        rr4 = self.create_report_record(factory2)
        rr5 = self.create_report_record(factory2)

        resp = self.cli.get(f"/api/factories/{self.factory.id}/report_records")
        self.assertEqual(resp.status_code, 200)

        rrs = resp.json()
        self.assertEqual([rr1.id, rr2.id, rr3.id], [rr["id"] for rr in rrs])

        resp = self.cli.get(f"/api/factories/{factory2.id}/report_records")
        self.assertEqual(resp.status_code, 200)

        rrs = resp.json()
        self.assertEqual([rr4.id, rr5.id], [rr["id"] for rr in rrs])

    def test_get_empty_if_no_report_record(self):
        resp = self.cli.get(f"/api/factories/{self.factory.id}/report_records")
        self.assertEqual(resp.status_code, 200)

        rrs = resp.json()
        self.assertEqual([], [rr["id"] for rr in rrs])

    def test_get_empty_if_strange_factory_id(self):
        resp = self.cli.get(f"/api/factories/{uuid4()}/report_records")
        self.assertEqual(resp.status_code, 200)

        rrs = resp.json()
        self.assertEqual([], [rr["id"] for rr in rrs])
