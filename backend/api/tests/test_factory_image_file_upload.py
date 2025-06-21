import io
from unittest.mock import patch, MagicMock
import pytest
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

from api.models import Factory, Image


@pytest.mark.django_db
class TestFactoryImageFileUpload:
    def setup_method(self):
        """Set up test data."""
        self.client = Client()
        self.factory = Factory.objects.create(
            name="Test Factory",
            lat=23.5,
            lng=120.5
        )
        
        # Create a simple test image
        self.image_data = b"fake_image_data_1234567890"
        self.image_file = SimpleUploadedFile(
            "test.jpg", 
            self.image_data, 
            content_type="image/jpeg"
        )

    def test_upload_image_file_success(self):
        """Test successful image file upload."""
        mock_upload_result = {
            "success": True,
            "url": "https://imgur.com/test.jpg",
            "delete_hash": "abc123",
            "backend_used": "imgur",
            "error": None
        }
        
        with patch("api.views.factory_image_c.ImageUploadService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.upload_image.return_value = mock_upload_result
            
            response = self.client.post(
                f"/api/factories/{self.factory.id}/images/upload",
                {
                    "image": self.image_file,
                    "nickname": "test_user",
                    "contact": "test@example.com",
                    "Latitude": "23.5",
                    "Longitude": "120.5",
                    "DateTimeOriginal": "2023:01:01 12:00:00"
                }
            )
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Check that image was created in database
        image = Image.objects.get(id=response_data["id"])
        assert image.image_path == "https://imgur.com/test.jpg"
        assert image.deletehash == "abc123"
        assert image.factory == self.factory
        assert image.orig_lat == 23.5
        assert image.orig_lng == 120.5
        assert image.report_record.nickname == "test_user"
        assert image.report_record.contact == "test@example.com"

    def test_upload_image_file_no_image(self):
        """Test upload without image file."""
        response = self.client.post(
            f"/api/factories/{self.factory.id}/images/upload",
            {
                "nickname": "test_user",
                "contact": "test@example.com"
            }
        )
        
        assert response.status_code == 400
        assert b"Image file is required" in response.content

    def test_upload_image_file_nonexistent_factory(self):
        """Test upload to nonexistent factory."""
        response = self.client.post(
            "/api/factories/999999/images/upload",
            {
                "image": self.image_file,
                "nickname": "test_user"
            }
        )
        
        assert response.status_code == 400
        assert b"Factory ID 999999 does not exist" in response.content

    def test_upload_image_file_empty_file(self):
        """Test upload with empty image file."""
        empty_image = SimpleUploadedFile("empty.jpg", b"", content_type="image/jpeg")
        
        response = self.client.post(
            f"/api/factories/{self.factory.id}/images/upload",
            {
                "image": empty_image,
                "nickname": "test_user"
            }
        )
        
        assert response.status_code == 400
        assert b"Empty image file" in response.content

    def test_upload_image_file_service_failure(self):
        """Test upload when image service fails."""
        mock_upload_result = {
            "success": False,
            "url": None,
            "delete_hash": None,
            "backend_used": None,
            "error": "All backends failed: imgur: API error; imagebb: Network error"
        }
        
        with patch("api.views.factory_image_c.ImageUploadService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.upload_image.return_value = mock_upload_result
            
            response = self.client.post(
                f"/api/factories/{self.factory.id}/images/upload",
                {
                    "image": self.image_file,
                    "nickname": "test_user"
                }
            )
        
        assert response.status_code == 500
        assert b"Image upload failed" in response.content

    def test_upload_image_file_invalid_datetime(self):
        """Test upload with invalid datetime format."""
        mock_upload_result = {
            "success": True,
            "url": "https://imgur.com/test.jpg",
            "delete_hash": "abc123",
            "backend_used": "imgur",
            "error": None
        }
        
        with patch("api.views.factory_image_c.ImageUploadService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.upload_image.return_value = mock_upload_result
            
            response = self.client.post(
                f"/api/factories/{self.factory.id}/images/upload",
                {
                    "image": self.image_file,
                    "nickname": "test_user",
                    "DateTimeOriginal": "invalid_datetime"
                }
            )
        
        # Should still succeed but ignore invalid datetime
        assert response.status_code == 200
        
        response_data = response.json()
        image = Image.objects.get(id=response_data["id"])
        assert image.orig_time is None

    def test_upload_image_file_minimal_data(self):
        """Test upload with only required data."""
        mock_upload_result = {
            "success": True,
            "url": "https://local.test/media/test.jpg",
            "delete_hash": None,
            "backend_used": "local",
            "error": None
        }
        
        with patch("api.views.factory_image_c.ImageUploadService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.upload_image.return_value = mock_upload_result
            
            response = self.client.post(
                f"/api/factories/{self.factory.id}/images/upload",
                {
                    "image": self.image_file
                }
            )
        
        assert response.status_code == 200
        
        response_data = response.json()
        image = Image.objects.get(id=response_data["id"])
        assert image.image_path == "https://local.test/media/test.jpg"
        assert image.deletehash is None
        assert image.report_record.nickname is None
        assert image.report_record.contact is None
        assert image.orig_lat is None
        assert image.orig_lng is None