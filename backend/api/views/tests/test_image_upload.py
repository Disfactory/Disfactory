import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from api.services.image_upload import ImageUploadResult


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def valid_image_file():
    """Create a valid image file for testing."""
    image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    return SimpleUploadedFile(
        "test_image.png",
        image_content,
        content_type="image/png"
    )


@pytest.fixture
def invalid_file():
    """Create an invalid (non-image) file for testing."""
    return SimpleUploadedFile(
        "test_file.txt",
        b"This is not an image",
        content_type="text/plain"
    )


@pytest.fixture
def oversized_image_file():
    """Create an oversized image file for testing."""
    # Create a file larger than 10MB
    large_content = b'x' * (11 * 1024 * 1024)  # 11MB
    return SimpleUploadedFile(
        "large_image.jpg",
        large_content,
        content_type="image/jpeg"
    )


@pytest.mark.django_db
class TestImageUploadView:
    """Test cases for the image upload endpoint."""

    def test_upload_image_success(self, client, valid_image_file):
        """Test successful image upload."""
        mock_upload_result = ImageUploadResult(
            success=True,
            url="https://example.com/uploaded_image.png",
            metadata={"filename": "test_image.png"}
        )
        
        with patch('api.views.image_upload.get_image_upload_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.upload_image.return_value = mock_upload_result
            mock_get_service.return_value = mock_service
            
            response = client.post('/api/upload', {
                'image': valid_image_file
            })
            
            assert response.status_code == 200
            response_data = response.json()
            assert response_data['url'] == "https://example.com/uploaded_image.png"
            mock_service.upload_image.assert_called_once()

    def test_upload_image_missing_file(self, client):
        """Test upload with missing image file."""
        response = client.post('/api/upload', {})
        
        assert response.status_code == 400
        assert b"Image file is required" in response.content

    def test_upload_image_invalid_file_type(self, client, invalid_file):
        """Test upload with invalid file type."""
        response = client.post('/api/upload', {
            'image': invalid_file
        })
        
        assert response.status_code == 400
        assert b"File must be an image" in response.content

    def test_upload_image_oversized_file(self, client, oversized_image_file):
        """Test upload with oversized file."""
        response = client.post('/api/upload', {
            'image': oversized_image_file
        })
        
        assert response.status_code == 400
        assert b"File size must be less than 10MB" in response.content

    def test_upload_image_service_failure(self, client, valid_image_file):
        """Test upload when service fails."""
        mock_upload_result = ImageUploadResult(
            success=False,
            error="Storage service unavailable"
        )
        
        with patch('api.views.image_upload.get_image_upload_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.upload_image.return_value = mock_upload_result
            mock_get_service.return_value = mock_service
            
            response = client.post('/api/upload', {
                'image': valid_image_file
            })
            
            assert response.status_code == 500
            assert b"Upload failed: Storage service unavailable" in response.content

    def test_upload_image_unexpected_error(self, client, valid_image_file):
        """Test upload when unexpected error occurs."""
        with patch('api.views.image_upload.get_image_upload_service') as mock_get_service:
            mock_get_service.side_effect = Exception("Unexpected error")
            
            response = client.post('/api/upload', {
                'image': valid_image_file
            })
            
            assert response.status_code == 500
            assert b"Internal server error" in response.content

    def test_upload_image_logs_ip_address(self, client, valid_image_file):
        """Test that IP address is logged for requests."""
        mock_upload_result = ImageUploadResult(
            success=True,
            url="https://example.com/uploaded_image.png"
        )
        
        with patch('api.views.image_upload.get_image_upload_service') as mock_get_service, \
             patch('api.views.image_upload.LOGGER') as mock_logger:
            mock_service = MagicMock()
            mock_service.upload_image.return_value = mock_upload_result
            mock_get_service.return_value = mock_service
            
            response = client.post('/api/upload', {
                'image': valid_image_file
            }, HTTP_X_FORWARDED_FOR='192.168.1.1')
            
            assert response.status_code == 200
            # Verify that logging occurred (IP should be logged)
            assert mock_logger.info.called

    def test_upload_image_validates_content_type(self, client):
        """Test upload with missing content type."""
        # Create file without content type
        image_file = SimpleUploadedFile(
            "test_image.png",
            b"fake image content",
            content_type=None
        )
        
        response = client.post('/api/upload', {
            'image': image_file
        })
        
        assert response.status_code == 400
        assert b"File must be an image" in response.content