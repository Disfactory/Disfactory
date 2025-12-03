import io
import os
import tempfile

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage


def create_test_image(format="PNG", size=(100, 100)):
    """Create a test image file."""
    image = PILImage.new("RGB", size, color="red")
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer


@pytest.mark.django_db
def test_upload_image_success(client, settings):
    """Test successful image upload."""
    # Create a temporary media root for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        settings.MEDIA_ROOT = temp_dir
        settings.DOMAIN = "https://api.disfactory.tw/"

        image_buffer = create_test_image()
        image_file = SimpleUploadedFile(
            name="test_image.png",
            content=image_buffer.read(),
            content_type="image/png",
        )

        resp = client.post(
            "/api/upload",
            data={"image": image_file},
            format="multipart",
        )

        assert resp.status_code == 200

        resp_data = resp.json()
        assert resp_data["success"] is True
        assert resp_data["status"] == 200
        assert "data" in resp_data
        assert "link" in resp_data["data"]
        assert "deletehash" in resp_data["data"]

        # Verify URL format
        link = resp_data["data"]["link"]
        assert link.startswith("https://api.disfactory.tw/media/uploads/")
        assert link.endswith(".png")

        # Verify file was actually created
        filename = link.split("/")[-1]
        file_path = os.path.join(temp_dir, "uploads", filename)
        assert os.path.exists(file_path)


@pytest.mark.django_db
def test_upload_image_jpeg(client, settings):
    """Test successful JPEG image upload."""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings.MEDIA_ROOT = temp_dir
        settings.DOMAIN = "https://api.disfactory.tw/"

        image_buffer = create_test_image(format="JPEG")
        image_file = SimpleUploadedFile(
            name="test_image.jpg",
            content=image_buffer.read(),
            content_type="image/jpeg",
        )

        resp = client.post(
            "/api/upload",
            data={"image": image_file},
            format="multipart",
        )

        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data["success"] is True
        assert resp_data["data"]["link"].endswith(".jpg")


@pytest.mark.django_db
def test_upload_image_no_file(client):
    """Test upload with no image file."""
    resp = client.post(
        "/api/upload",
        data={},
        format="multipart",
    )

    assert resp.status_code == 400
    resp_data = resp.json()
    assert resp_data["success"] is False
    assert resp_data["status"] == 400
    assert "error" in resp_data["data"]


@pytest.mark.django_db
def test_upload_image_invalid_extension(client, settings):
    """Test upload with invalid file extension."""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings.MEDIA_ROOT = temp_dir

        # Create a fake file with invalid extension
        fake_file = SimpleUploadedFile(
            name="test_file.txt",
            content=b"not an image",
            content_type="text/plain",
        )

        resp = client.post(
            "/api/upload",
            data={"image": fake_file},
            format="multipart",
        )

        assert resp.status_code == 400
        resp_data = resp.json()
        assert resp_data["success"] is False
        assert "Invalid file type" in resp_data["data"]["error"]


@pytest.mark.django_db
def test_upload_image_invalid_content(client, settings):
    """Test upload with valid extension but invalid image content."""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings.MEDIA_ROOT = temp_dir

        # Create a fake file with valid image extension but invalid content
        fake_file = SimpleUploadedFile(
            name="fake_image.png",
            content=b"this is not a valid image content",
            content_type="image/png",
        )

        resp = client.post(
            "/api/upload",
            data={"image": fake_file},
            format="multipart",
        )

        assert resp.status_code == 400
        resp_data = resp.json()
        assert resp_data["success"] is False
        assert "not a valid image" in resp_data["data"]["error"]


@pytest.mark.django_db
def test_upload_image_file_too_large(client, settings, monkeypatch):
    """Test upload with file exceeding size limit."""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings.MEDIA_ROOT = temp_dir

        # Monkeypatch MAX_FILE_SIZE to a small value for testing
        from api.views import image_upload

        monkeypatch.setattr(image_upload, "MAX_FILE_SIZE", 100)  # 100 bytes

        image_buffer = create_test_image(size=(500, 500))  # Larger image
        image_file = SimpleUploadedFile(
            name="large_image.png",
            content=image_buffer.read(),
            content_type="image/png",
        )

        resp = client.post(
            "/api/upload",
            data={"image": image_file},
            format="multipart",
        )

        assert resp.status_code == 413
        resp_data = resp.json()
        assert resp_data["success"] is False
        assert "File too large" in resp_data["data"]["error"]


@pytest.mark.django_db
def test_upload_image_webp(client, settings):
    """Test successful WebP image upload."""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings.MEDIA_ROOT = temp_dir
        settings.DOMAIN = "https://api.disfactory.tw/"

        image_buffer = create_test_image(format="WEBP")
        image_file = SimpleUploadedFile(
            name="test_image.webp",
            content=image_buffer.read(),
            content_type="image/webp",
        )

        resp = client.post(
            "/api/upload",
            data={"image": image_file},
            format="multipart",
        )

        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data["success"] is True
        assert resp_data["data"]["link"].endswith(".webp")


@pytest.mark.django_db
def test_upload_image_gif(client, settings):
    """Test successful GIF image upload."""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings.MEDIA_ROOT = temp_dir
        settings.DOMAIN = "https://api.disfactory.tw/"

        image_buffer = create_test_image(format="GIF")
        image_file = SimpleUploadedFile(
            name="test_image.gif",
            content=image_buffer.read(),
            content_type="image/gif",
        )

        resp = client.post(
            "/api/upload",
            data={"image": image_file},
            format="multipart",
        )

        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data["success"] is True
        assert resp_data["data"]["link"].endswith(".gif")


@pytest.mark.django_db
def test_upload_image_without_domain_setting(client, settings):
    """Test upload when DOMAIN setting is not configured."""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings.MEDIA_ROOT = temp_dir
        # Remove or set DOMAIN to None
        if hasattr(settings, "DOMAIN"):
            delattr(settings, "DOMAIN")

        image_buffer = create_test_image()
        image_file = SimpleUploadedFile(
            name="test_image.png",
            content=image_buffer.read(),
            content_type="image/png",
        )

        resp = client.post(
            "/api/upload",
            data={"image": image_file},
            format="multipart",
        )

        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data["success"] is True
        # URL should still be generated from request
        assert "/media/uploads/" in resp_data["data"]["link"]
