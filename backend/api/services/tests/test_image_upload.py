import pytest
from unittest.mock import patch, MagicMock, mock_open
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from api.services.image_upload import (
    DjangoStorageImageUploadService,
    LocalImageUploadService,
    S3ImageUploadService,
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


class TestDjangoStorageImageUploadService:
    """Test cases for DjangoStorageImageUploadService."""

    def test_upload_success(self, valid_image_file):
        """Test successful image upload."""
        mock_storage = MagicMock()
        mock_storage.save.return_value = 'images/test-image.png'
        mock_storage.url.return_value = '/media/images/test-image.png'
        mock_storage.__class__.__name__ = 'TestStorage'
        
        service = DjangoStorageImageUploadService()
        service.storage = mock_storage
        
        with override_settings(DOMAIN='https://example.com'):
            result = service.upload_image(valid_image_file, 'test-image.png')
        
        assert result.success is True
        assert result.url == 'https://example.com/media/images/test-image.png'
        assert result.metadata['filename'] == 'images/test-image.png'
        assert result.metadata['storage_backend'] == 'TestStorage'
        
        mock_storage.save.assert_called_once_with('images/test-image.png', valid_image_file)

    def test_upload_auto_filename(self, valid_image_file):
        """Test upload with auto-generated filename."""
        mock_storage = MagicMock()
        mock_storage.save.return_value = 'images/auto-generated.png'
        mock_storage.url.return_value = '/media/images/auto-generated.png'
        
        service = DjangoStorageImageUploadService()
        service.storage = mock_storage
        
        result = service.upload_image(valid_image_file)
        
        assert result.success is True
        assert result.metadata['filename'] == 'images/auto-generated.png'
        
        # Check that save was called with a filename starting with 'images/'
        call_args = mock_storage.save.call_args[0]
        assert call_args[0].startswith('images/')
        assert call_args[0].endswith('.png')

    def test_upload_absolute_url(self, valid_image_file):
        """Test upload with absolute URL from storage."""
        mock_storage = MagicMock()
        mock_storage.save.return_value = 'images/test-image.png'
        mock_storage.url.return_value = 'https://cdn.example.com/images/test-image.png'
        
        service = DjangoStorageImageUploadService()
        service.storage = mock_storage
        
        result = service.upload_image(valid_image_file, 'test-image.png')
        
        assert result.success is True
        assert result.url == 'https://cdn.example.com/images/test-image.png'

    def test_upload_failure(self, valid_image_file):
        """Test upload failure."""
        mock_storage = MagicMock()
        mock_storage.save.side_effect = Exception("Storage error")
        
        service = DjangoStorageImageUploadService()
        service.storage = mock_storage
        
        result = service.upload_image(valid_image_file)
        
        assert result.success is False
        assert 'Storage error' in result.error

    def test_delete_success(self):
        """Test successful image delete."""
        mock_storage = MagicMock()
        mock_storage.exists.return_value = True
        
        service = DjangoStorageImageUploadService()
        service.storage = mock_storage
        
        result = service.delete_image('/media/images/test-image.png')
        
        assert result is True
        mock_storage.exists.assert_called_once_with('images/test-image.png')
        mock_storage.delete.assert_called_once_with('images/test-image.png')

    def test_delete_absolute_url(self):
        """Test delete with absolute URL."""
        mock_storage = MagicMock()
        mock_storage.exists.return_value = True
        
        service = DjangoStorageImageUploadService()
        service.storage = mock_storage
        
        with override_settings(MEDIA_URL='/media/'):
            result = service.delete_image('https://example.com/media/images/test-image.png')
        
        assert result is True
        mock_storage.exists.assert_called_once_with('images/test-image.png')
        mock_storage.delete.assert_called_once_with('images/test-image.png')

    def test_delete_file_not_found(self):
        """Test delete when file doesn't exist."""
        mock_storage = MagicMock()
        mock_storage.exists.return_value = False
        
        service = DjangoStorageImageUploadService()
        service.storage = mock_storage
        
        result = service.delete_image('/media/images/nonexistent.png')
        
        assert result is False
        mock_storage.delete.assert_not_called()

    def test_delete_failure(self):
        """Test delete failure."""
        mock_storage = MagicMock()
        mock_storage.exists.return_value = True
        mock_storage.delete.side_effect = Exception("Delete error")
        
        service = DjangoStorageImageUploadService()
        service.storage = mock_storage
        
        result = service.delete_image('/media/images/test-image.png')
        
        assert result is False


class TestLocalImageUploadService:
    """Test cases for LocalImageUploadService."""

    @override_settings(
        MEDIA_ROOT='/tmp/test_media',
        MEDIA_URL='/media/',
        DOMAIN='https://localhost:8000'
    )
    def test_local_service_init(self):
        """Test LocalImageUploadService initialization."""
        with patch('django.core.files.storage.FileSystemStorage') as mock_fs:
            service = LocalImageUploadService()
            
            mock_fs.assert_called_once_with(
                location='/tmp/test_media',
                base_url='/media/'
            )

    @override_settings(MEDIA_ROOT='/tmp/test_media')
    def test_local_upload_success(self, valid_image_file):
        """Test successful local upload."""
        service = LocalImageUploadService()
        
        # Mock the storage
        service.storage = MagicMock()
        service.storage.save.return_value = 'images/test-image.png'
        service.storage.url.return_value = '/media/images/test-image.png'
        service.storage.__class__.__name__ = 'FileSystemStorage'
        
        with override_settings(DOMAIN='https://localhost:8000'):
            result = service.upload_image(valid_image_file, 'test-image.png')
        
        assert result.success is True
        assert result.url == 'https://localhost:8000/media/images/test-image.png'
        assert result.metadata['storage_backend'] == 'FileSystemStorage'


class TestS3ImageUploadService:
    """Test cases for S3ImageUploadService."""

    @override_settings(
        IMAGE_UPLOAD_BUCKET='test-bucket',
        IMAGE_UPLOAD_ACCESS_KEY='test-key',
        IMAGE_UPLOAD_SECRET_KEY='test-secret',
        IMAGE_UPLOAD_ENDPOINT_URL='https://s3.example.com',
        IMAGE_UPLOAD_PUBLIC_URL_BASE='https://cdn.example.com'
    )
    def test_s3_service_init(self):
        """Test S3ImageUploadService initialization."""
        with patch('storages.backends.s3boto3.S3Boto3Storage') as mock_s3:
            service = S3ImageUploadService()
            
            mock_s3.assert_called_once_with(
                bucket_name='test-bucket',
                region_name='auto',
                endpoint_url='https://s3.example.com',
                access_key='test-key',
                secret_key='test-secret',
                custom_domain='https://cdn.example.com',
                file_overwrite=False,
                default_acl='public-read'
            )

    def test_s3_service_import_error(self):
        """Test S3 service initialization with missing storages."""
        # Mock the import to fail at the module level
        import sys
        if 'storages.backends.s3boto3' in sys.modules:
            del sys.modules['storages.backends.s3boto3']
        
        with patch.dict('sys.modules', {'storages.backends.s3boto3': None}):
            with pytest.raises(ImportError, match="S3 storage requires 'django-storages"):
                S3ImageUploadService()

    def test_s3_upload_success(self, valid_image_file):
        """Test successful S3 upload using mocked storage."""
        # Create a mock storage instance
        mock_storage = MagicMock()
        mock_storage.save.return_value = 'images/test-image.png'
        mock_storage.url.return_value = 'https://cdn.example.com/images/test-image.png'
        mock_storage.__class__.__name__ = 'S3Boto3Storage'
        
        # Use DjangoStorageImageUploadService directly with the mock storage
        service = DjangoStorageImageUploadService(storage=mock_storage)
        result = service.upload_image(valid_image_file, 'test-image.png')
        
        assert result.success is True
        assert result.url == 'https://cdn.example.com/images/test-image.png'
        assert result.metadata['storage_backend'] == 'S3Boto3Storage'
        mock_storage.save.assert_called_once_with('images/test-image.png', valid_image_file)


class TestGetImageUploadService:
    """Test cases for get_image_upload_service factory function."""

    @override_settings(IMAGE_UPLOAD_SERVICE='s3')
    def test_get_s3_service(self):
        """Test getting S3 service."""
        with patch('api.services.image_upload.S3ImageUploadService') as mock_s3:
            service = get_image_upload_service()
            mock_s3.assert_called_once()

    @override_settings(IMAGE_UPLOAD_SERVICE='local')
    def test_get_local_service(self):
        """Test getting local service."""
        with patch('api.services.image_upload.LocalImageUploadService') as mock_local:
            service = get_image_upload_service()
            mock_local.assert_called_once()

    @override_settings(IMAGE_UPLOAD_SERVICE='invalid')
    def test_get_invalid_service(self):
        """Test getting invalid service type."""
        with pytest.raises(ValueError, match="Unknown image upload service type"):
            get_image_upload_service()

    def test_get_default_service(self):
        """Test getting default service (local)."""
        with override_settings():
            # Remove IMAGE_UPLOAD_SERVICE setting by using an empty dict
            from django.test.utils import override_settings as django_override
            with django_override(IMAGE_UPLOAD_SERVICE=None):
                with patch('api.services.image_upload.LocalImageUploadService') as mock_local:
                    service = get_image_upload_service()
                    mock_local.assert_called_once()