import os
from unittest.mock import patch, MagicMock
import pytest

from api.services.image_upload import (
    ImgurBackend, ImageBBBackend, LocalBackend, ImageUploadService
)
from django.conf import settings
from django.test import override_settings


class TestImgurBackend:
    def test_upload_success(self):
        """Test successful Imgur upload."""
        backend = ImgurBackend("test_client_id", {})
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "link": "https://imgur.com/test.jpg",
                "deletehash": "abc123"
            }
        }
        
        with patch('api.services.image_upload.requests.post', return_value=mock_response):
            result = backend.upload(b"fake_image_data")
            
        assert result["success"] is True
        assert result["url"] == "https://imgur.com/test.jpg"
        assert result["delete_hash"] == "abc123"
        assert result["error"] is None

    def test_upload_api_error(self):
        """Test Imgur API error handling."""
        backend = ImgurBackend("test_client_id", {})
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "errors": [{"detail": "Invalid image"}],
            "data": {"error": "Invalid image format"}
        }
        
        with patch('api.services.image_upload.requests.post', return_value=mock_response):
            result = backend.upload(b"invalid_data")
            
        assert result["success"] is False
        assert "Invalid image format" in result["error"]
        assert result["url"] is None

    def test_upload_no_client_id(self):
        """Test upload without client ID."""
        backend = ImgurBackend("", {})
        result = backend.upload(b"fake_image_data")
        
        assert result["success"] is False
        assert "client ID not configured" in result["error"]

    def test_get_name(self):
        """Test backend name."""
        backend = ImgurBackend("test_id", {})
        assert backend.get_name() == "imgur"

    def test_custom_timeout(self):
        """Test custom timeout configuration."""
        config = {'REQUEST_TIMEOUT': 60}
        backend = ImgurBackend("test_client_id", config)
        
        with patch('api.services.image_upload.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": {"link": "test.jpg", "deletehash": "abc"}}
            mock_post.return_value = mock_response
            
            backend.upload(b"fake_image_data")
            
            # Check that timeout was passed correctly
            mock_post.assert_called_once()
            assert mock_post.call_args[1]['timeout'] == 60


class TestImageBBBackend:
    def test_upload_success(self):
        """Test successful ImageBB upload."""
        backend = ImageBBBackend("test_api_key", {})
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "url": "https://ibb.co/test.jpg",
                "delete_url": "https://ibb.co/delete/abc123"
            }
        }
        
        with patch('api.services.image_upload.requests.post', return_value=mock_response):
            result = backend.upload(b"fake_image_data")
            
        assert result["success"] is True
        assert result["url"] == "https://ibb.co/test.jpg"
        assert result["delete_hash"] == "https://ibb.co/delete/abc123"
        assert result["error"] is None

    def test_upload_api_error(self):
        """Test ImageBB API error handling."""
        backend = ImageBBBackend("test_api_key", {})
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "success": False,
            "error": {"message": "Invalid API key"}
        }
        
        with patch('api.services.image_upload.requests.post', return_value=mock_response):
            result = backend.upload(b"fake_image_data")
            
        assert result["success"] is False
        assert "Invalid API key" in result["error"]

    def test_upload_no_api_key(self):
        """Test upload without API key."""
        backend = ImageBBBackend("", {})
        result = backend.upload(b"fake_image_data")
        
        assert result["success"] is False
        assert "API key not configured" in result["error"]

    def test_get_name(self):
        """Test backend name."""
        backend = ImageBBBackend("test_key", {})
        assert backend.get_name() == "imagebb"


class TestLocalBackend:
    @override_settings(
        MEDIA_ROOT="/tmp/test_media",
        MEDIA_URL="/media/",
        DOMAIN="https://test.com/"
    )
    def test_upload_success(self):
        """Test successful local upload."""
        backend = LocalBackend({})
        
        with patch('api.services.image_upload.os.makedirs'), \
             patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = backend.upload(b"fake_image_data")
            
        assert result["success"] is True
        assert result["url"].startswith("https://test.com/media/")
        assert result["url"].endswith(".jpg")
        assert result["delete_hash"] is None
        assert result["error"] is None

    def test_get_name(self):
        """Test backend name."""
        backend = LocalBackend({})
        assert backend.get_name() == "local"


class TestImageUploadService:
    @override_settings(
        IMGUR_CLIENT_ID="test_imgur", 
        IMAGEBB_API_KEY="test_imagebb",
        IMAGE_UPLOAD_CONFIG={
            'BACKEND_ORDER': ['imgur', 'imagebb', 'local'],
            'REQUEST_TIMEOUT': 30,
            'MAX_FILE_SIZE': 10 * 1024 * 1024,
        }
    )
    def test_service_initialization(self):
        """Test service initializes with configured backends."""
        service = ImageUploadService()
        
        # Should have Imgur, ImageBB, and Local backends
        assert len(service.backends) == 3
        backend_names = [b.get_name() for b in service.backends]
        assert "imgur" in backend_names
        assert "imagebb" in backend_names
        assert "local" in backend_names

    @override_settings(
        IMGUR_CLIENT_ID=None, 
        IMAGEBB_API_KEY=None,
        IMAGE_UPLOAD_CONFIG={'BACKEND_ORDER': ['local']}
    )
    def test_service_only_local(self):
        """Test service with only local backend when no keys configured."""
        service = ImageUploadService()
        
        # Should only have Local backend
        assert len(service.backends) == 1
        assert service.backends[0].get_name() == "local"

    @override_settings(
        IMGUR_CLIENT_ID="test_imgur", 
        IMAGEBB_API_KEY="test_imagebb",
        IMAGE_UPLOAD_CONFIG={
            'BACKEND_ORDER': ['imagebb', 'imgur', 'local'],  # Custom order
            'MAX_FILE_SIZE': 5 * 1024 * 1024,  # 5MB limit
        }
    )
    def test_custom_backend_order(self):
        """Test custom backend ordering."""
        service = ImageUploadService()
        
        # Should respect custom order
        backend_names = [b.get_name() for b in service.backends]
        assert backend_names == ['imagebb', 'imgur', 'local']

    @override_settings(
        IMAGE_UPLOAD_CONFIG={
            'MAX_FILE_SIZE': 1024,  # 1KB limit for testing
        }
    )
    def test_image_validation_file_size(self):
        """Test image validation for file size."""
        service = ImageUploadService()
        
        # Create large fake image data
        large_image_data = b"fake_image" * 200  # > 1KB
        
        result = service.validate_image(large_image_data)
        assert result['valid'] is False
        assert 'File size too large' in result['error']

    @override_settings(
        IMAGE_UPLOAD_CONFIG={
            'MAX_FILE_SIZE': 10 * 1024 * 1024,
        }
    )
    def test_image_validation_valid_headers(self):
        """Test image validation with valid headers."""
        service = ImageUploadService()
        
        # JPEG header
        jpeg_data = b'\xff\xd8\xff' + b'fake_jpeg_data'
        result = service.validate_image(jpeg_data)
        assert result['valid'] is True
        
        # PNG header
        png_data = b'\x89PNG\r\n\x1a\n' + b'fake_png_data'
        result = service.validate_image(png_data)
        assert result['valid'] is True

    def test_image_validation_invalid_headers(self):
        """Test image validation with invalid headers."""
        service = ImageUploadService()
        
        invalid_data = b'not_an_image_file'
        result = service.validate_image(invalid_data)
        assert result['valid'] is False
        assert 'Invalid image file format' in result['error']

    @override_settings(
        IMGUR_CLIENT_ID="test_imgur", 
        IMAGEBB_API_KEY="test_imagebb",
        IMAGE_UPLOAD_CONFIG={
            'RETRY_ATTEMPTS': 2,
            'RETRY_DELAY': 1,
        }
    )
    def test_upload_with_retry(self):
        """Test upload with retry logic."""
        service = ImageUploadService()
        
        # Mock first backend to fail twice then succeed
        call_count = 0
        def mock_upload(data):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return {"success": False, "error": "Temporary failure", "url": None, "delete_hash": None}
            else:
                return {"success": True, "url": "https://imgur.com/test.jpg", "delete_hash": "abc", "error": None}
        
        with patch.object(service.backends[0], 'upload', side_effect=mock_upload), \
             patch('api.services.image_upload.time.sleep'):  # Speed up test
            
            result = service.upload_image(b'\xff\xd8\xff' + b'fake_jpeg_data')
            
        assert result["success"] is True
        assert result["url"] == "https://imgur.com/test.jpg"
        assert call_count == 3  # Failed twice, succeeded on third try

    @override_settings(IMGUR_CLIENT_ID="test_imgur", IMAGEBB_API_KEY="test_imagebb")
    def test_upload_first_backend_success(self):
        """Test upload succeeds with first backend."""
        service = ImageUploadService()
        
        # Mock first backend (Imgur) to succeed
        with patch.object(service.backends[0], 'upload') as mock_upload:
            mock_upload.return_value = {
                "success": True,
                "url": "https://imgur.com/test.jpg",
                "delete_hash": "abc123",
                "error": None
            }
            
            result = service.upload_image(b'\xff\xd8\xff' + b'fake_jpeg_data')
            
        assert result["success"] is True
        assert result["url"] == "https://imgur.com/test.jpg"
        assert result["backend_used"] == "imgur"

    @override_settings(IMGUR_CLIENT_ID="test_imgur", IMAGEBB_API_KEY="test_imagebb")
    def test_upload_fallback_to_second_backend(self):
        """Test upload falls back to second backend when first fails."""
        service = ImageUploadService()
        
        # Mock first backend (Imgur) to fail
        with patch.object(service.backends[0], 'upload') as mock_imgur, \
             patch.object(service.backends[1], 'upload') as mock_imagebb:
            
            mock_imgur.return_value = {
                "success": False,
                "error": "Imgur API error",
                "url": None,
                "delete_hash": None
            }
            
            mock_imagebb.return_value = {
                "success": True,
                "url": "https://ibb.co/test.jpg",
                "delete_hash": "xyz789",
                "error": None
            }
            
            result = service.upload_image(b'\xff\xd8\xff' + b'fake_jpeg_data')
            
        assert result["success"] is True
        assert result["url"] == "https://ibb.co/test.jpg"
        assert result["backend_used"] == "imagebb"

    @override_settings(IMGUR_CLIENT_ID="test_imgur", IMAGEBB_API_KEY="test_imagebb")
    def test_upload_fallback_to_local(self):
        """Test upload falls back to local storage when external backends fail."""
        service = ImageUploadService()
        
        # Mock first two backends to fail, local to succeed
        with patch.object(service.backends[0], 'upload') as mock_imgur, \
             patch.object(service.backends[1], 'upload') as mock_imagebb, \
             patch.object(service.backends[2], 'upload') as mock_local:
            
            mock_imgur.return_value = {
                "success": False,
                "error": "Imgur down",
                "url": None,
                "delete_hash": None
            }
            
            mock_imagebb.return_value = {
                "success": False,
                "error": "ImageBB down",
                "url": None,
                "delete_hash": None
            }
            
            mock_local.return_value = {
                "success": True,
                "url": "https://api.disfactory.tw/media/test.jpg",
                "delete_hash": None,
                "error": None
            }
            
            result = service.upload_image(b'\xff\xd8\xff' + b'fake_jpeg_data')
            
        assert result["success"] is True
        assert result["backend_used"] == "local"

    def test_upload_validation_failure(self):
        """Test upload fails validation."""
        service = ImageUploadService()
        
        # Invalid image data
        invalid_data = b'not_an_image'
        result = service.upload_image(invalid_data)
        
        assert result["success"] is False
        assert "Image validation failed" in result["error"]
        assert result["backend_used"] is None

    def test_upload_all_backends_fail(self):
        """Test upload fails when all backends fail."""
        service = ImageUploadService()
        
        # Mock all backends to fail
        for i, backend in enumerate(service.backends):
            with patch.object(backend, 'upload') as mock_upload:
                mock_upload.return_value = {
                    "success": False,
                    "error": f"{backend.get_name()} failed",
                    "url": None,
                    "delete_hash": None
                }
        
        result = service.upload_image(b'\xff\xd8\xff' + b'fake_jpeg_data')
        
        assert result["success"] is False
        assert "All backends failed" in result["error"]
        assert result["backend_used"] is None