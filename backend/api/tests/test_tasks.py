from unittest.mock import patch
from tempfile import NamedTemporaryFile

import pytest

from ..models import Image
from ..tasks import _upload_image_to_imgur, upload_image, update_landcode


FAKE_IMAGE_URI = "https://ingur.fake/12i34uhoi2"


class MockResponse:
    def __init__(self, json_data):
        self.json_data = json_data

    def json(self):
        return self.json_data


def test_upload_image_to_imgur():
    image_byte_content = b"1234567890"
    mock_imgur_return = MockResponse(
        {
            "data": {
                "link": FAKE_IMAGE_URI,
            }
        }
    )
    fake_client_id = "1234"
    with patch("api.tasks.requests.post", return_value=mock_imgur_return) as mock_post:
        path = _upload_image_to_imgur(image_byte_content, fake_client_id)
        mock_post.assert_called_once_with(
            "https://api.imgur.com/3/image",
            data={"image": image_byte_content},
            headers={"Authorization": f"Client-ID {fake_client_id}"},
        )
        assert path == mock_imgur_return.json()["data"]["link"]


@pytest.mark.django_db
@patch("api.tasks._upload_image_to_imgur", return_value=FAKE_IMAGE_URI)
def test_upload_image(_):
    img = Image.objects.create(image_path="")
    with NamedTemporaryFile(delete=False) as f:
        upload_image(f.name, "some_client_id", img.id)

    new_img = Image.objects.get(pk=img.id)
    assert new_img.image_path == FAKE_IMAGE_URI


def test_upload_image_to_imgur_with_errors_falls_back_to_local(settings, tmp_path):
    """Imgur 'errors' response triggers the credits fallback path."""
    settings.MEDIA_ROOT = str(tmp_path)
    settings.DOMAIN = "https://api.disfactory.tw/"
    mock_post_return = MockResponse({"errors": [{"code": 1}]})
    mock_get_return = MockResponse({"data": {"UserLimit": 0}})
    with (
        patch("api.tasks.requests.post", return_value=mock_post_return),
        patch("api.tasks.requests.get", return_value=mock_get_return),
    ):
        path = _upload_image_to_imgur(b"1234567890", "1234")
    assert path.startswith("https://api.disfactory.tw/media/")
    assert path.endswith(".jpg")


def test_upload_image_to_imgur_bad_json_falls_back_to_local(settings, tmp_path):
    """Unparseable imgur response triggers the exception fallback path."""
    settings.MEDIA_ROOT = str(tmp_path)
    settings.DOMAIN = "https://api.disfactory.tw/"

    class BadJsonResponse:
        def json(self):
            raise ValueError("No JSON could be decoded")

    with patch("api.tasks.requests.post", return_value=BadJsonResponse()):
        path = _upload_image_to_imgur(b"1234567890", "1234")
    assert path.startswith("https://api.disfactory.tw/media/")
    assert path.endswith(".jpg")


@pytest.mark.django_db
@patch("api.tasks.easymap.get_land_number")
def test_update_landcode_success(mock_get_land_number):
    from ..models import Factory

    factory = Factory.objects.create(
        name="test_factory",
        lat=24.0,
        lng=121.0,
        display_number=667,
    )
    mock_get_land_number.return_value = {
        "landno": "00820018",
        "sectno": "5212",
        "sectname": "新生段",
        "towncode": "D24",
        "townname": "臺北市中山區",
    }
    update_landcode(factory.id)

    factory.refresh_from_db()
    assert factory.landcode == "00820018"
    assert factory.sectcode == "5212"
    assert factory.sectname == "新生段"
    assert factory.towncode == "D24"
    assert factory.townname == "臺北市中山區"
    mock_get_land_number.assert_called_once_with(lng=121.0, lat=24.0)


@pytest.mark.django_db
@patch("api.tasks.easymap.get_land_number", side_effect=Exception("easymap down"))
def test_update_landcode_easymap_failure(_):
    from ..models import Factory

    factory = Factory.objects.create(
        name="test_factory",
        lat=24.0,
        lng=121.0,
        display_number=668,
    )
    # must not raise; failure is only logged
    update_landcode(factory.id)

    factory.refresh_from_db()
    assert factory.landcode is None


def test_upload_image_missing_file_returns_false():
    assert upload_image("/nonexistent/path/image.jpg", "some_client_id", 1) is False


@pytest.mark.django_db
@patch("api.tasks._upload_image_to_imgur", return_value=FAKE_IMAGE_URI)
def test_upload_image_db_update_failure_returns_false(mock_upload, monkeypatch):
    """DB failure after a successful upload returns False."""
    import api.tasks as tasks_module

    def boom(*args, **kwargs):
        raise Exception("db down")

    monkeypatch.setattr(tasks_module.Image.objects, "filter", boom)
    img = Image.objects.create(image_path="")
    with NamedTemporaryFile(delete=False) as f:
        assert upload_image(f.name, "some_client_id", img.id) is False


@pytest.mark.django_db
@patch("api.tasks._upload_image_to_imgur", return_value=FAKE_IMAGE_URI)
def test_upload_image_remove_failure_returns_true(mock_upload, monkeypatch):
    """Unremovable tempfile after success still returns True (warning only)."""
    import os as os_module

    def boom(path):
        raise OSError("cannot remove")

    monkeypatch.setattr(os_module, "remove", boom)
    img = Image.objects.create(image_path="")
    with NamedTemporaryFile(delete=False) as f:
        assert upload_image(f.name, "some_client_id", img.id) is True

    new_img = Image.objects.get(pk=img.id)
    assert new_img.image_path == FAKE_IMAGE_URI
