from unittest.mock import patch
from tempfile import NamedTemporaryFile

import pytest

from ..models import Image
from ..tasks import _upload_image_to_imgur, _upload_image_with_service, upload_image


FAKE_IMAGE_URI = "https://ingur.fake/12i34uhoi2"


class MockResponse:
    def __init__(self, json_data):
        self.json_data = json_data

    def json(self):
        return self.json_data


def test_upload_image_to_imgur():
    """Test legacy Imgur upload function for backward compatibility."""
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


def test_upload_image_with_service():
    """Test new multi-backend upload service."""
    image_byte_content = b"1234567890"
    
    mock_result = {
        "success": True,
        "url": FAKE_IMAGE_URI,
        "delete_hash": "abc123",
        "backend_used": "imgur",
        "error": None
    }
    
    with patch("api.tasks.ImageUploadService") as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.upload_image.return_value = mock_result
        
        url, delete_hash = _upload_image_with_service(image_byte_content)
        
        assert url == FAKE_IMAGE_URI
        assert delete_hash == "abc123"
        mock_service.upload_image.assert_called_once_with(image_byte_content)


@pytest.mark.django_db
@patch("api.tasks._upload_image_with_service", return_value=(FAKE_IMAGE_URI, "delete123"))
def test_upload_image(mock_upload):
    """Test main upload_image function with new service."""
    img = Image.objects.create(image_path="")
    with NamedTemporaryFile(delete=False) as f:
        upload_image(f.name, "some_client_id", img.id)

    new_img = Image.objects.get(pk=img.id)
    assert new_img.image_path == FAKE_IMAGE_URI
    assert new_img.deletehash == "delete123"
