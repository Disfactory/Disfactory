import re

import pytest
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management import call_command
from django.templatetags.static import static
from django.test import Client
from django.utils.functional import empty


@pytest.fixture
def collected_static(tmp_path, settings):
    """Run collectstatic into a temporary STATIC_ROOT, as start_prod.sh does."""
    settings.STATIC_ROOT = str(tmp_path)
    staticfiles_storage._wrapped = empty  # re-create the storage with the new root
    call_command("collectstatic", "--noinput", verbosity=0)
    # Simulate the hand-copied docx exporter bundle, which collectstatic never sees.
    (tmp_path / "docx").mkdir()
    (tmp_path / "docx" / "export-word-docx.js").write_text("// bundle")
    staticfiles_storage._wrapped = empty  # reload the manifest
    yield tmp_path
    staticfiles_storage._wrapped = empty


def test_collected_files_get_hashed_urls(collected_static):
    assert re.fullmatch(r"/static/admin/css/base\.[0-9a-f]{12}\.css", static("admin/css/base.css"))
    assert (collected_static / "staticfiles.json").exists()


def test_files_missing_from_manifest_keep_plain_name(collected_static):
    assert static("docx/export-word-docx.js") == "/static/docx/export-word-docx.js"


def test_without_manifest_falls_back_to_plain_names(tmp_path, settings):
    settings.STATIC_ROOT = str(tmp_path)
    staticfiles_storage._wrapped = empty
    try:
        assert static("admin/css/base.css") == "/static/admin/css/base.css"
    finally:
        staticfiles_storage._wrapped = empty


@pytest.mark.django_db
def test_admin_login_page_links_hashed_css(collected_static):
    html = Client().get("/admin/login/", HTTP_HOST="testserver").content.decode()
    assert re.search(r'href="/static/admin/css/base\.[0-9a-f]{12}\.css"', html)
