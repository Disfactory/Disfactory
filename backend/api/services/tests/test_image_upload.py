import pytest
from unittest.mock import patch, MagicMock, mock_open
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from botocore.exceptions import ClientError

from api.services.image_upload import (
    S3ImageUploadService,
    LocalImageUploadService,
    get_image_upload_service,
    ImageUploadResult
)


@pytest.fixture
def valid_image_file():
    """Create a valid image file for testing."""
    image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    return SimpleUploadedFile(
        "test_image.png",
        image_content,
        content_type="image/png"
    )


class TestS3ImageUploadService:
    """Test cases for S3ImageUploadService."""

    @override_settings(
        IMAGE_UPLOAD_BUCKET='test-bucket',
        IMAGE_UPLOAD_ACCESS_KEY='test-key',
        IMAGE_UPLOAD_SECRET_KEY='test-secret',
        IMAGE_UPLOAD_ENDPOINT_URL='https://s3.example.com',
        IMAGE_UPLOAD_PUBLIC_URL_BASE='https://cdn.example.com'
    )
    def test_s3_service_init_success(self):
        """Test successful initialization of S3 service."""
        with patch('api.services.image_upload.boto3.client') as mock_boto3:
            service = S3ImageUploadService()
            assert service.bucket_name == 'test-bucket'
            assert service.access_key == 'test-key'
            assert service.secret_key == 'test-secret'
            assert service.endpoint_url == 'https://s3.example.com'
            assert service.public_url_base == 'https://cdn.example.com'
            mock_boto3.assert_called_once()

    def test_s3_service_init_missing_config(self):
        """Test S3 service initialization with missing configuration."""
        with override_settings():
            # Remove all settings
            del_attrs = ['IMAGE_UPLOAD_BUCKET', 'IMAGE_UPLOAD_ACCESS_KEY', 'IMAGE_UPLOAD_SECRET_KEY']
            for attr in del_attrs:
                if hasattr(pytest.settings, attr):
                    delattr(pytest.settings, attr)
            
            with pytest.raises(ValueError, match="Missing required S3 configuration"):
                S3ImageUploadService()

    @override_settings(
        IMAGE_UPLOAD_BUCKET='test-bucket',
        IMAGE_UPLOAD_ACCESS_KEY='test-key',
        IMAGE_UPLOAD_SECRET_KEY='test-secret',
        IMAGE_UPLOAD_PUBLIC_URL_BASE='https://cdn.example.com'
    )
    def test_s3_upload_success(self, valid_image_file):
        """Test successful S3 upload."""
        with patch('api.services.image_upload.boto3.client') as mock_boto3:
            mock_s3_client = MagicMock()
            mock_boto3.return_value = mock_s3_client
            
            service = S3ImageUploadService()
            result = service.upload_image(valid_image_file, 'test-image.png')
            
            assert result.success is True
            assert result.url == 'https://cdn.example.com/test-image.png'
            assert result.metadata['filename'] == 'test-image.png'
            assert result.metadata['bucket'] == 'test-bucket'
            
            mock_s3_client.upload_fileobj.assert_called_once()

    @override_settings(
        IMAGE_UPLOAD_BUCKET='test-bucket',
        IMAGE_UPLOAD_ACCESS_KEY='test-key',
        IMAGE_UPLOAD_SECRET_KEY='test-secret'
    )
    def test_s3_upload_auto_filename(self, valid_image_file):
        """Test S3 upload with auto-generated filename."""
        with patch('api.services.image_upload.boto3.client') as mock_boto3:
            mock_s3_client = MagicMock()
            mock_boto3.return_value = mock_s3_client
            
            service = S3ImageUploadService()
            result = service.upload_image(valid_image_file)
            
            assert result.success is True
            assert result.url.endswith('.png')  # Should preserve extension
            assert result.metadata['filename'].endswith('.png')

    @override_settings(
        IMAGE_UPLOAD_BUCKET='test-bucket',
        IMAGE_UPLOAD_ACCESS_KEY='test-key',
        IMAGE_UPLOAD_SECRET_KEY='test-secret'
    )
    def test_s3_upload_failure(self, valid_image_file):
        """Test S3 upload failure."""
        with patch('api.services.image_upload.boto3.client') as mock_boto3:
            mock_s3_client = MagicMock()
            mock_s3_client.upload_fileobj.side_effect = ClientError(
                {'Error': {'Code': 'NoSuchBucket', 'Message': 'Bucket does not exist'}},
                'upload_fileobj'
            )
            mock_boto3.return_value = mock_s3_client
            
            service = S3ImageUploadService()
            result = service.upload_image(valid_image_file)
            
            assert result.success is False
            assert 'S3 upload failed' in result.error

    @override_settings(
        IMAGE_UPLOAD_BUCKET='test-bucket',
        IMAGE_UPLOAD_ACCESS_KEY='test-key',
        IMAGE_UPLOAD_SECRET_KEY='test-secret'
    )
    def test_s3_delete_success(self):
        """Test successful S3 delete."""
        with patch('api.services.image_upload.boto3.client') as mock_boto3:
            mock_s3_client = MagicMock()
            mock_boto3.return_value = mock_s3_client
            
            service = S3ImageUploadService()
            result = service.delete_image('https://cdn.example.com/test-image.png')
            
            assert result is True
            mock_s3_client.delete_object.assert_called_once_with(
                Bucket='test-bucket',
                Key='test-image.png'
            )

    @override_settings(
        IMAGE_UPLOAD_BUCKET='test-bucket',
        IMAGE_UPLOAD_ACCESS_KEY='test-key',
        IMAGE_UPLOAD_SECRET_KEY='test-secret'
    )
    def test_s3_delete_failure(self):
        """Test S3 delete failure."""
        with patch('api.services.image_upload.boto3.client') as mock_boto3:
            mock_s3_client = MagicMock()
            mock_s3_client.delete_object.side_effect = ClientError(
                {'Error': {'Code': 'NoSuchKey', 'Message': 'Key does not exist'}},
                'delete_object'
            )
            mock_boto3.return_value = mock_s3_client
            
            service = S3ImageUploadService()
            result = service.delete_image('https://cdn.example.com/nonexistent.png')
            
            assert result is False


class TestLocalImageUploadService:
    """Test cases for LocalImageUploadService."""

    @override_settings(
        MEDIA_ROOT='/tmp/test_media',
        MEDIA_URL='/media/',
        DOMAIN='https://localhost:8000'
    )
    def test_local_upload_success(self, valid_image_file):
        """Test successful local upload."""
        with patch('builtins.open', mock_open()) as mock_file, \
             patch('os.makedirs') as mock_makedirs:
            
            service = LocalImageUploadService()
            result = service.upload_image(valid_image_file, 'test-image.png')
            
            assert result.success is True
            assert result.url == 'https://localhost:8000/media/test-image.png'
            assert result.metadata['filename'] == 'test-image.png'
            assert '/tmp/test_media/test-image.png' in result.metadata['path']
            
            mock_makedirs.assert_called_once_with('/tmp/test_media', exist_ok=True)
            mock_file.assert_called_once()

    @override_settings(MEDIA_ROOT='/tmp/test_media')
    def test_local_upload_auto_filename(self, valid_image_file):
        """Test local upload with auto-generated filename."""
        with patch('builtins.open', mock_open()) as mock_file, \
             patch('os.makedirs'):
            
            service = LocalImageUploadService()
            result = service.upload_image(valid_image_file)
            
            assert result.success is True
            assert result.metadata['filename'].endswith('.png')

    @override_settings(MEDIA_ROOT='/tmp/test_media')
    def test_local_upload_failure(self, valid_image_file):
        """Test local upload failure."""
        with patch('builtins.open', side_effect=IOError("Permission denied")), \
             patch('os.makedirs'):
            
            service = LocalImageUploadService()
            result = service.upload_image(valid_image_file)
            
            assert result.success is False
            assert 'Local upload failed' in result.error

    @override_settings(MEDIA_ROOT='/tmp/test_media')
    def test_local_delete_success(self):
        """Test successful local delete."""
        with patch('os.path.exists', return_value=True) as mock_exists, \
             patch('os.remove') as mock_remove:
            
            service = LocalImageUploadService()
            result = service.delete_image('https://localhost:8000/media/test-image.png')
            
            assert result is True
            mock_exists.assert_called_once_with('/tmp/test_media/test-image.png')
            mock_remove.assert_called_once_with('/tmp/test_media/test-image.png')

    @override_settings(MEDIA_ROOT='/tmp/test_media')
    def test_local_delete_file_not_found(self):
        """Test local delete when file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            
            service = LocalImageUploadService()
            result = service.delete_image('https://localhost:8000/media/nonexistent.png')
            
            assert result is False

    @override_settings(MEDIA_ROOT='/tmp/test_media')
    def test_local_delete_failure(self):
        """Test local delete failure."""
        with patch('os.path.exists', return_value=True), \
             patch('os.remove', side_effect=OSError("Permission denied")):
            
            service = LocalImageUploadService()
            result = service.delete_image('https://localhost:8000/media/test-image.png')
            
            assert result is False


class TestGetImageUploadService:
    """Test cases for get_image_upload_service factory function."""

    @override_settings(
        IMAGE_UPLOAD_SERVICE='s3',
        IMAGE_UPLOAD_BUCKET='test-bucket',
        IMAGE_UPLOAD_ACCESS_KEY='test-key',
        IMAGE_UPLOAD_SECRET_KEY='test-secret'
    )
    def test_get_s3_service(self):
        """Test getting S3 service."""
        with patch('api.services.image_upload.boto3.client'):
            service = get_image_upload_service()
            assert isinstance(service, S3ImageUploadService)

    @override_settings(IMAGE_UPLOAD_SERVICE='local')
    def test_get_local_service(self):
        """Test getting local service."""
        service = get_image_upload_service()
        assert isinstance(service, LocalImageUploadService)

    @override_settings(IMAGE_UPLOAD_SERVICE='invalid')
    def test_get_invalid_service(self):
        """Test getting invalid service type."""
        with pytest.raises(ValueError, match="Unknown image upload service type"):
            get_image_upload_service()

    def test_get_default_service(self):
        """Test getting default service (local)."""
        with override_settings():
            # Remove IMAGE_UPLOAD_SERVICE setting
            if hasattr(pytest.settings, 'IMAGE_UPLOAD_SERVICE'):
                delattr(pytest.settings, 'IMAGE_UPLOAD_SERVICE')
            
            service = get_image_upload_service()
            assert isinstance(service, LocalImageUploadService)