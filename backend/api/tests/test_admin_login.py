import re

import pytest
from django.test import Client

from users.models import CustomUser

# Caddy terminates TLS and forwards plain HTTP to gunicorn, keeping the Host header
# and adding X-Forwarded-Proto.
PROXIED_HTTPS = {"HTTP_HOST": "testserver", "HTTP_X_FORWARDED_PROTO": "https"}


def _csrf_token(html: str) -> str:
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
    assert match, "login form has no CSRF token"
    return match.group(1)


@pytest.mark.django_db
def test_admin_login_over_https_behind_proxy():
    """Regression for #716: the browser sends `Origin: https://…` while gunicorn sees HTTP."""
    CustomUser.objects.create_superuser("admin", "admin@example.com", "pw-for-test")
    client = Client(enforce_csrf_checks=True)

    login_page = client.get("/admin/login/", **PROXIED_HTTPS)
    assert login_page.status_code == 200

    response = client.post(
        "/admin/login/?next=/admin/",
        {
            "username": "admin",
            "password": "pw-for-test",
            "csrfmiddlewaretoken": _csrf_token(login_page.content.decode()),
            "next": "/admin/",
        },
        HTTP_ORIGIN="https://testserver",
        HTTP_REFERER="https://testserver/admin/login/",
        **PROXIED_HTTPS,
    )

    assert response.status_code == 302, response.content[:300]
    assert response["Location"] == "/admin/"


@pytest.mark.django_db
def test_admin_login_rejects_cross_site_origin():
    client = Client(enforce_csrf_checks=True)
    login_page = client.get("/admin/login/", **PROXIED_HTTPS)

    response = client.post(
        "/admin/login/",
        {
            "username": "admin",
            "password": "whatever",
            "csrfmiddlewaretoken": _csrf_token(login_page.content.decode()),
        },
        HTTP_ORIGIN="https://evil.example",
        **PROXIED_HTTPS,
    )

    assert response.status_code == 403
