import pytest
from django.test import RequestFactory

from api.views.tests.test_factories_u import factory  # noqa: F401 (shared fixture)
from api.views.utils import _get_client_ip, _sample, _get_nearby_factories


pytestmark = pytest.mark.django_db


def test_get_client_ip_prefers_forwarded_for():
    rf = RequestFactory()
    request = rf.get("/", HTTP_X_FORWARDED_FOR="1.1.1.1, 2.2.2.2")
    assert _get_client_ip(request) == "2.2.2.2"


def test_get_client_ip_falls_back_to_real_ip():
    rf = RequestFactory()
    request = rf.get("/", HTTP_X_REAL_IP="3.3.3.3")
    assert _get_client_ip(request) == "3.3.3.3"


def test_get_client_ip_falls_back_to_remote_addr():
    rf = RequestFactory()
    request = rf.get("/", REMOTE_ADDR="4.4.4.4")
    assert _get_client_ip(request) == "4.4.4.4"


def test_sample_returns_at_most_k_items():
    assert len(_sample(range(100), 5)) == 5
    assert len(_sample(range(3), 5)) == 3


def test_get_nearby_factories_samples_when_radius_exceeds_max(client, factory, settings):
    """Radius above MAX_FACTORY_RADIUS_PER_GET goes through the sampling path."""
    settings.MAX_FACTORY_RADIUS_PER_GET = 0
    factories = _get_nearby_factories(factory.lat, factory.lng, 5, source="U")
    assert {f.id for f in factories} == {factory.id}
