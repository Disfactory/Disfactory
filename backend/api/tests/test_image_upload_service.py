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
        backend = ImgurBackend("test_client_id")
        
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
        backend = ImgurBackend("test_client_id")
        
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
        backend = ImgurBackend("")
        result = backend.upload(b"fake_image_data")
        
        assert result["success"] is False
        assert "client ID not configured" in result["error"]

    def test_get_name(self):
        """Test backend name."""
        backend = ImgurBackend("test_id")
        assert backend.get_name() == "imgur"


class TestImageBBBackend:
    def test_upload_success(self):
        """Test successful ImageBB upload."""
        backend = ImageBBBackend("test_api_key")
        
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
        backend = ImageBBBackend("test_api_key")
        
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
        backend = ImageBBBackend("")
        result = backend.upload(b"fake_image_data")
        
        assert result["success"] is False
        assert "API key not configured" in result["error"]

    def test_get_name(self):
        """Test backend name."""
        backend = ImageBBBackend("test_key")
        assert backend.get_name() == "imagebb"


class TestLocalBackend:
    @override_settings(
        MEDIA_ROOT="/tmp/test_media",
        MEDIA_URL="/media/",
        DOMAIN="https://test.com/"
    )
    def test_upload_success(self):
        """Test successful local upload."""
        backend = LocalBackend()
        
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
        backend = LocalBackend()
        assert backend.get_name() == "local"


class TestImageUploadService:
    @override_settings(IMGUR_CLIENT_ID="test_imgur", IMAGEBB_API_KEY="test_imagebb")
    def test_service_initialization(self):
        """Test service initializes with configured backends."""
        service = ImageUploadService()
        
        # Should have Imgur, ImageBB, and Local backends
        assert len(service.backends) == 3
        backend_names = [b.get_name() for b in service.backends]
        assert "imgur" in backend_names
        assert "imagebb" in backend_names
        assert "local" in backend_names

    @override_settings(IMGUR_CLIENT_ID=None, IMAGEBB_API_KEY=None)
    def test_service_only_local(self):
        """Test service with only local backend when no keys configured."""
        service = ImageUploadService()
        
        # Should only have Local backend
        assert len(service.backends) == 1
        assert service.backends[0].get_name() == "local"

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
            
            result = service.upload_image(b"fake_image_data")
            
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
            
            result = service.upload_image(b"fake_image_data")
            
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
            
            result = service.upload_image(b"fake_image_data")
            
        assert result["success"] is True
        assert result["backend_used"] == "local"

    def test_upload_all_backends_fail(self):
        """Test upload fails when all backends fail."""
        service = ImageUploadService()
        
        # Mock all backends to fail
        for backend in service.backends:
            with patch.object(backend, 'upload') as mock_upload:
                mock_upload.return_value = {
                    "success": False,
                    "error": f"{backend.get_name()} failed",
                    "url": None,
                    "delete_hash": None
                }
        
        result = service.upload_image(b"fake_image_data")
        
        assert result["success"] is False
        assert "All backends failed" in result["error"]
        assert result["backend_used"] is None