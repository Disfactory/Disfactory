"""Smoke tests that render every admin page through the real admin site.

These guard the third-party admin integrations (django-import-export,
django-admin-rangefilter) across Django upgrades, which unit tests of
admin actions don't exercise.
"""

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse

from api.models import Factory

REGISTERED_MODELS = sorted(
    admin.site._registry, key=lambda m: (m._meta.app_label, m._meta.model_name)
)


def _url(model, action, *args):
    return reverse(f"admin:{model._meta.app_label}_{model._meta.model_name}_{action}", args=args)


@pytest.fixture
def factory(db):
    return Factory.objects.create(
        name="admin smoke", lat=23.234, lng=120.1, factory_type="2-3", display_number=666
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "model", REGISTERED_MODELS, ids=lambda m: f"{m._meta.app_label}.{m._meta.model_name}"
)
def test_changelist_and_add_pages_render(admin_client, admin_user, rf, factory, model):
    assert admin_client.get(_url(model, "changelist")).status_code == 200
    request = rf.get("/")
    request.user = admin_user
    if admin.site._registry[model].has_add_permission(request):
        assert admin_client.get(_url(model, "add")).status_code == 200


@pytest.mark.django_db
def test_user_add_form_creates_user(admin_client):
    response = admin_client.post(
        _url(get_user_model(), "add"),
        {
            "username": "new-volunteer",
            "usable_password": "true",
            "password1": "a-Long-test-passw0rd",
            "password2": "a-Long-test-passw0rd",
        },
    )
    assert response.status_code == 302, response.content.decode()[:2000]
    user = get_user_model().objects.get(username="new-volunteer")
    assert user.check_password("a-Long-test-passw0rd")


@pytest.mark.django_db
def test_factory_change_page_renders(admin_client, factory):
    assert admin_client.get(_url(Factory, "change", factory.pk)).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [
        {"created_at__range__gte": "2020-01-01", "created_at__range__lte": "2030-12-31"},
        {"created_at__range__gte": "2020-01-01"},
        {"created_at__range__lte": "2030-12-31"},
    ],
    ids=["both-bounds", "from-only", "to-only"],
)
def test_factory_report_record_date_range_filter(admin_client, factory, params):
    response = admin_client.get(_url(Factory, "changelist"), params)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("action", ["import", "export"])
def test_factory_import_export_pages_render(admin_client, factory, action):
    response = admin_client.get(_url(Factory, action))
    assert response.status_code == 200
    # Spreadsheet formats come from the tablib extras pinned in pyproject.toml
    if action == "export":
        content = response.content.decode()
        assert "xlsx" in content
        assert "xls" in content


@pytest.mark.django_db
def test_factory_export_csv_download(admin_client, factory):
    response = admin_client.post(
        _url(Factory, "export"),
        {"format": "0", "export_items": [factory.pk], **_all_resource_fields()},
    )
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    assert "admin smoke" in response.content.decode()


def _all_resource_fields():
    """import-export 4 requires the selected field checkboxes in the export POST."""
    model_admin = admin.site._registry[Factory]
    resource = model_admin.get_export_resource_classes(None)[0]()
    prefix = resource.__class__.__name__.lower()
    return {f"{prefix}_{field.column_name}": "on" for field in resource.get_export_fields()}


@pytest.mark.django_db
def test_swagger_schema_renders(client):
    response = client.get("/swagger/", {"format": "openapi"})
    assert response.status_code == 200
