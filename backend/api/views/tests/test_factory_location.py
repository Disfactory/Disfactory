from datetime import datetime, timezone

import pytest

from api.models import Factory


pytestmark = pytest.mark.django_db


@pytest.fixture
def factory(db):
    return Factory.objects.create(
        name="test_factory",
        lat=24,
        lng=121,
        landcode="test_landcode",
        townname="test_townname",
        sectname="test_sectname",
        sectcode="test_sectcode",
        status_time=datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc),
        display_number=666,
    )


def test_get_factory_location(client, factory):
    resp = client.get(
        f"/api/factories/{factory.id}/location"
    )
    assert resp.status_code == 200

    resp_data = resp.json()
    assert resp_data["lat"] == factory.lat
    assert resp_data["lng"] == factory.lng

    assert resp_data["landcode"] == factory.landcode
    assert resp_data["townname"] == factory.townname
    assert resp_data["sectname"] == factory.sectname
    assert resp_data["sectcode"] == factory.sectcode
