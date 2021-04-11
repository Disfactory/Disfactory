from datetime import datetime, timezone
from uuid import uuid4

import pytest
from freezegun import freeze_time

from api.models import Factory, ReportRecord


pytestmark = pytest.mark.django_db


@pytest.fixture
def factory(db):
    return Factory.objects.create(
        name="test_factory",
        lat=24,
        lng=121,
        status_time=datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc),
        display_number=666,
    )


def test_update_factory_normal_attribute(factory, client):
    assert factory.name == "test_factory"
    assert factory.lat == 24
    assert factory.lng == 121
    put_body = {
        "name": "correct_factory",
        "factory_type": "6",
    }
    resp = client.put(
        f"/api/factories/{factory.id}", data=put_body, content_type="application/json"
    )
    assert resp.status_code == 200

    factory = Factory.objects.get(pk=factory.id)
    assert factory.name == "correct_factory"
    assert factory.lat == 24
    assert factory.lng == 121
    assert factory.factory_type == "6"

    report_records = ReportRecord.objects.filter(factory_id=factory.id)
    assert len(report_records) == 1
    assert report_records[0].action_type == "UPDATE"
    assert report_records[0].action_body == put_body


def test_update_factory_with_contact(factory, client):
    assert factory.name == "test_factory"
    assert factory.lat == 24
    assert factory.lng == 121

    put_body = {
        "name": "correct_factory",
        "factory_type": "6",
        "contact": "0800092000",
        "others": "這工廠讓我坐骨神經痛",
    }
    resp = client.put(
        f"/api/factories/{factory.id}", data=put_body, content_type="application/json"
    )
    assert resp.status_code == 200

    factory = Factory.objects.get(pk=factory.id)
    assert factory.name == "correct_factory"
    assert factory.lat == 24
    assert factory.lng == 121
    assert factory.factory_type == "6"

    report_records = ReportRecord.objects.filter(factory_id=factory.id)
    assert len(report_records) == 1
    assert report_records[0].action_type == "UPDATE"
    assert report_records[0].action_body == put_body
    assert report_records[0].contact == "0800092000"
    assert report_records[0].others == "這工廠讓我坐骨神經痛"


def test_update_factory_status(factory, client):
    put_body = {
        "cet_report_status": "P",
    }
    test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc)
    with freeze_time(test_time):
        resp = client.put(
            f"/api/factories/{factory.id}",
            data=put_body,
            content_type="application/json",
        )
    assert resp.status_code == 200

    factory = Factory.objects.get(pk=factory.id)
    assert factory.cet_report_status == "P"


def test_update_factory_lat_or_lng_should_have_new_point(factory, client):
    assert factory.lat == 24
    assert factory.lng == 121

    put_body = {
        "lat": 24.5,
        "lng": 121.5,
    }
    resp = client.put(
        f"/api/factories/{factory.id}",
        data=put_body,
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.content == b"Factory position cannot be modified."


def test_get_single_factory(client, factory):
    resp = client.get(f"/api/factories/{factory.id}")
    resp_data = resp.json()
    assert resp_data["name"] == factory.name
    assert resp_data["lat"] == factory.lat
    assert resp_data["lng"] == factory.lng
    assert resp_data["cet_report_status"] == factory.cet_report_status


def test_get_single_factory_not_exist(client):
    not_existed_code = uuid4()
    resp = client.get(f"/api/factories/{not_existed_code}")

    assert resp.status_code == 400
