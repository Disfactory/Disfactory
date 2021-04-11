from datetime import datetime, timezone
from uuid import uuid4

import pytest

from api.models import Factory, ReportRecord


pytestmark = pytest.mark.django_db


@pytest.fixture
def factory_factory(db):

    class FactoryFactory:

        def create(self, display_number=666):
            return Factory.objects.create(
                name="test_factory",
                lat=24,
                lng=121,
                status_time=datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc),
                display_number=display_number or 666,
            )

    return FactoryFactory()


@pytest.fixture
def report_factory(db):

    class ReportFactory:

        def create(self, factory, action_type="post_image", action_body=None):
            return ReportRecord.objects.create(
                factory=factory,
                action_type=action_type or "post_image",
                action_body=action_body or {},
                contact="0800-092000",
                others="猴～被我拍到了吧",
            )

        def bulk_create(self, n: int, **kwargs):
            return [self.create(**kwargs) for _ in range(n)]

    return ReportFactory()


def test_get_correct_report_record_with_order(client, factory_factory, report_factory):
    factory1 = factory_factory.create()
    reports_with_factory1 = report_factory.bulk_create(3, factory=factory1)

    factory2 = factory_factory.create(777)
    reports_with_factory2 = report_factory.bulk_create(2, factory=factory2)

    resp = client.get(f"/api/factories/{factory1.id}/report_records")
    assert resp.status_code == 200

    rrs = resp.json()
    assert [rr["id"] for rr in rrs] == [report.id for report in reports_with_factory1]

    resp = client.get(f"/api/factories/{factory2.id}/report_records")
    assert resp.status_code == 200

    rrs = resp.json()
    assert [rr["id"] for rr in rrs] == [report.id for report in reports_with_factory2]


def test_get_empty_if_no_report_record(client, factory_factory):
    factory = factory_factory.create()
    resp = client.get(f"/api/factories/{factory.id}/report_records")

    assert resp.status_code == 200
    assert not resp.json()


def test_get_empty_if_strange_factory_id(client):
    resp = client.get(f"/api/factories/{uuid4()}/report_records")
    assert resp.status_code == 200
    assert not resp.json()
