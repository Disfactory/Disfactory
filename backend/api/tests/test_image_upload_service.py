import os
from unittest.mock import patch, MagicMock
import pytest

from api.services.image_upload import (
    ImgurBackend, ImageBBBackend, LocalBackend, CloudflareR2Backend, ImageUploadService
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


class TestCloudflareR2Backend:
    def test_upload_success(self):
        """Test successful Cloudflare R2 upload."""
        backend = CloudflareR2Backend(
            account_id="test_account",
            access_key_id="test_access_key",
            secret_access_key="test_secret",
            bucket_name="test_bucket",
            config={}
        )
        
        # Mock boto3 client
        mock_client = MagicMock()
        mock_client.put_object.return_value = {}
        
        with patch('api.services.image_upload.BOTO3_AVAILABLE', True), \
             patch.object(backend, '_get_client', return_value=mock_client):
            result = backend.upload(b"fake_image_data")
            
        assert result["success"] is True
        assert result["url"].startswith("https://pub-test_account.r2.dev/")
        assert result["url"].endswith(".jpg")
        assert result["delete_hash"] is not None  # Should be the filename
        assert result["error"] is None
        
        # Verify S3 client was called correctly
        mock_client.put_object.assert_called_once()
        call_args = mock_client.put_object.call_args[1]
        assert call_args['Bucket'] == 'test_bucket'
        assert call_args['Body'] == b"fake_image_data"
        assert call_args['ContentType'] == 'image/jpeg'
        assert call_args['ACL'] == 'public-read'

    def test_upload_with_custom_domain(self):
        """Test Cloudflare R2 upload with custom domain."""
        backend = CloudflareR2Backend(
            account_id="test_account",
            access_key_id="test_access_key",
            secret_access_key="test_secret",
            bucket_name="test_bucket",
            config={'CUSTOM_DOMAIN': 'images.example.com'}
        )
        
        # Mock boto3 client
        mock_client = MagicMock()
        mock_client.put_object.return_value = {}
        
        with patch('api.services.image_upload.BOTO3_AVAILABLE', True), \
             patch.object(backend, '_get_client', return_value=mock_client):
            result = backend.upload(b"fake_image_data")
            
        assert result["success"] is True
        assert result["url"].startswith("https://images.example.com/")
        assert result["url"].endswith(".jpg")

    def test_upload_missing_credentials(self):
        """Test R2 backend with missing credentials."""
        backend = CloudflareR2Backend("", "", "", "", {})
        
        result = backend.upload(b"fake_image_data")
        
        assert result["success"] is False
        assert "not fully configured" in result["error"]
        assert result["url"] is None

    def test_upload_boto3_not_available(self):
        """Test R2 backend when boto3 is not available."""
        backend = CloudflareR2Backend(
            account_id="test_account",
            access_key_id="test_access_key",
            secret_access_key="test_secret",
            bucket_name="test_bucket",
            config={}
        )
        
        with patch('api.services.image_upload.BOTO3_AVAILABLE', False):
            result = backend.upload(b"fake_image_data")
            
        assert result["success"] is False
        assert "boto3 is required" in result["error"]
        assert result["url"] is None

    def test_upload_client_error(self):
        """Test R2 backend handling AWS ClientError."""
        from botocore.exceptions import ClientError
        
        backend = CloudflareR2Backend(
            account_id="test_account",
            access_key_id="test_access_key",
            secret_access_key="test_secret",
            bucket_name="test_bucket",
            config={}
        )
        
        # Mock boto3 client to raise ClientError
        mock_client = MagicMock()
        mock_client.put_object.side_effect = ClientError(
            error_response={
                'Error': {
                    'Code': 'NoSuchBucket',
                    'Message': 'The specified bucket does not exist'
                }
            },
            operation_name='PutObject'
        )
        
        with patch('api.services.image_upload.BOTO3_AVAILABLE', True), \
             patch.object(backend, '_get_client', return_value=mock_client):
            result = backend.upload(b"fake_image_data")
            
        assert result["success"] is False
        assert "NoSuchBucket" in result["error"]
        assert "The specified bucket does not exist" in result["error"]
        assert result["url"] is None

    def test_upload_no_credentials_error(self):
        """Test R2 backend handling NoCredentialsError."""
        from botocore.exceptions import NoCredentialsError
        
        backend = CloudflareR2Backend(
            account_id="test_account",
            access_key_id="test_access_key",
            secret_access_key="test_secret",
            bucket_name="test_bucket",
            config={}
        )
        
        # Mock boto3 client to raise NoCredentialsError
        mock_client = MagicMock()
        mock_client.put_object.side_effect = NoCredentialsError()
        
        with patch('api.services.image_upload.BOTO3_AVAILABLE', True), \
             patch.object(backend, '_get_client', return_value=mock_client):
            result = backend.upload(b"fake_image_data")
            
        assert result["success"] is False
        assert "Invalid Cloudflare R2 credentials" in result["error"]
        assert result["url"] is None

    def test_upload_generic_error(self):
        """Test R2 backend handling generic exceptions."""
        backend = CloudflareR2Backend(
            account_id="test_account",
            access_key_id="test_access_key",
            secret_access_key="test_secret",
            bucket_name="test_bucket",
            config={}
        )
        
        # Mock boto3 client to raise generic exception
        mock_client = MagicMock()
        mock_client.put_object.side_effect = Exception("Network error")
        
        with patch('api.services.image_upload.BOTO3_AVAILABLE', True), \
             patch.object(backend, '_get_client', return_value=mock_client):
            result = backend.upload(b"fake_image_data")
            
        assert result["success"] is False
        assert "Unexpected error uploading to Cloudflare R2" in result["error"]
        assert "Network error" in result["error"]
        assert result["url"] is None

    def test_get_name(self):
        """Test backend name."""
        backend = CloudflareR2Backend("", "", "", "", {})
        assert backend.get_name() == "cloudflare_r2"

    def test_get_client_initialization(self):
        """Test S3 client initialization with correct configuration."""
        backend = CloudflareR2Backend(
            account_id="test_account",
            access_key_id="test_access_key",
            secret_access_key="test_secret",
            bucket_name="test_bucket",
            config={'RETRY_ATTEMPTS': 2}
        )
        
        with patch('api.services.image_upload.BOTO3_AVAILABLE', True), \
             patch('api.services.image_upload.boto3.client') as mock_boto3_client:
            
            backend._get_client()
            
            # Verify boto3.client was called with correct parameters
            mock_boto3_client.assert_called_once()
            call_args = mock_boto3_client.call_args
            assert call_args[1]['endpoint_url'] == 'https://test_account.r2.cloudflarestorage.com'
            assert call_args[1]['aws_access_key_id'] == 'test_access_key'
            assert call_args[1]['aws_secret_access_key'] == 'test_secret'


class TestImageUploadService:
    @override_settings(
        IMGUR_CLIENT_ID="test_imgur", 
        IMAGEBB_API_KEY="test_imagebb",
        CLOUDFLARE_R2_ACCOUNT_ID="test_account",
        CLOUDFLARE_R2_ACCESS_KEY_ID="test_access_key",
        CLOUDFLARE_R2_SECRET_ACCESS_KEY="test_secret",
        CLOUDFLARE_R2_BUCKET_NAME="test_bucket",
        MEDIA_ROOT="/tmp/test_media",
        MEDIA_URL="/media/",
        DOMAIN="https://test.example.com",
        IMAGE_UPLOAD_CONFIG={
            'BACKEND_ORDER': ['imgur', 'imagebb', 'cloudflare_r2', 'local'],
            'REQUEST_TIMEOUT': 30,
            'MAX_FILE_SIZE': 10 * 1024 * 1024,
        }
    )
    def test_service_initialization(self):
        """Test service initializes with configured backends."""
        service = ImageUploadService()
        
        # Should have Imgur, ImageBB, CloudflareR2, and Local backends
        assert len(service.backends) == 4
        backend_names = [b.get_name() for b in service.backends]
        assert "imgur" in backend_names
        assert "imagebb" in backend_names
        assert "cloudflare_r2" in backend_names
        assert "local" in backend_names

    @override_settings(
        IMGUR_CLIENT_ID=None, 
        IMAGEBB_API_KEY=None,
        MEDIA_ROOT="/tmp/test_media",
        MEDIA_URL="/media/",
        DOMAIN="https://test.example.com",
        IMAGE_UPLOAD_CONFIG={'BACKEND_ORDER': ['local']}
    )
    def test_service_only_local(self):
        """Test service with only local backend when explicitly configured."""
        service = ImageUploadService()
        
        # Should only have Local backend
        assert len(service.backends) == 1
        assert service.backends[0].get_name() == "local"

    @override_settings(
        IMGUR_CLIENT_ID="test_imgur", 
        IMAGEBB_API_KEY="test_imagebb",
        MEDIA_ROOT="/tmp/test_media",
        MEDIA_URL="/media/",
        DOMAIN="https://test.example.com",
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
        IMGUR_CLIENT_ID=None, 
        IMAGEBB_API_KEY=None,
        CLOUDFLARE_R2_ACCOUNT_ID=None,
        IMAGE_UPLOAD_CONFIG={'BACKEND_ORDER': ['imgur', 'imagebb', 'cloudflare_r2']}
    )
    def test_service_no_backends_configured(self):
        """Test service when no backends have proper configuration."""
        service = ImageUploadService()
        
        # Should have no backends since none are configured
        assert len(service.backends) == 0

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

    @override_settings(
        IMGUR_CLIENT_ID="test_imgur", 
        IMAGEBB_API_KEY="test_imagebb",
        MEDIA_ROOT="/tmp/test_media",
        MEDIA_URL="/media/",
        DOMAIN="https://api.disfactory.tw",
        IMAGE_UPLOAD_CONFIG={'BACKEND_ORDER': ['imgur', 'imagebb', 'local']}
    )
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

    @override_settings(IMGUR_CLIENT_ID="test_imgur")
    def test_upload_validation_failure(self):
        """Test upload fails validation."""
        service = ImageUploadService()
        
        # Invalid image data
        invalid_data = b'not_an_image'
        result = service.upload_image(invalid_data)
        
        assert result["success"] is False
        assert "Image validation failed" in result["error"]
        assert result["backend_used"] is None

    @override_settings(IMGUR_CLIENT_ID="test_imgur")
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
        assert "All configured backends failed" in result["error"]
        assert result["backend_used"] is None