import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from dataclasses import dataclass

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import default_storage, get_storage_class

LOGGER = logging.getLogger("django")


@dataclass
class ImageUploadResult:
    """Result of image upload operation."""
    success: bool
    url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ImageUploadService(ABC):
    """Abstract base class for image upload services."""

    @abstractmethod
    def upload_image(self, image_file: InMemoryUploadedFile, filename: Optional[str] = None) -> ImageUploadResult:
        """
        Upload an image file to the storage service.
        
        Args:
            image_file: The uploaded image file
            filename: Optional custom filename (will generate UUID if not provided)
            
        Returns:
            ImageUploadResult with success status, URL, and any error information
        """
        pass

    @abstractmethod
    def delete_image(self, url: str) -> bool:
        """
        Delete an image from the storage service.
        
        Args:
            url: The URL of the image to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass


class DjangoStorageImageUploadService(ImageUploadService):
    """Image upload service using Django storage backends."""

    def __init__(self, storage=None):
        """
        Initialize with a specific storage instance or use default.
        
        Args:
            storage: Django storage instance to use. If None, uses default_storage.
        """
        if storage:
            self.storage = storage
        else:
            self.storage = default_storage

    def upload_image(self, image_file: InMemoryUploadedFile, filename: Optional[str] = None) -> ImageUploadResult:
        """Upload image using Django storage backend."""
        try:
            # Generate filename if not provided
            if not filename:
                file_extension = self._get_file_extension(image_file.name)
                filename = f"images/{uuid.uuid4()}{file_extension}"
            elif not filename.startswith('images/'):
                # Ensure images are stored in images/ directory
                filename = f"images/{filename}"

            # Save file using Django storage
            saved_name = self.storage.save(filename, image_file)
            
            # Get public URL
            url = self.storage.url(saved_name)
            
            # Handle relative URLs by making them absolute
            if url.startswith('/') and hasattr(settings, 'DOMAIN'):
                url = f"{settings.DOMAIN.rstrip('/')}{url}"

            LOGGER.info(f"Successfully uploaded image: {saved_name}")
            return ImageUploadResult(
                success=True,
                url=url,
                metadata={
                    'filename': saved_name,
                    'storage_backend': self.storage.__class__.__name__
                }
            )

        except Exception as e:
            error_msg = f"Image upload failed: {str(e)}"
            LOGGER.error(error_msg)
            return ImageUploadResult(success=False, error=error_msg)

    def delete_image(self, url: str) -> bool:
        """Delete image from storage backend."""
        try:
            # Extract filename from URL
            # Handle both absolute and relative URLs
            if url.startswith('http'):
                # Extract path from full URL
                from urllib.parse import urlparse
                parsed = urlparse(url)
                filename = parsed.path.lstrip('/')
            else:
                # Relative URL, strip leading slash
                filename = url.lstrip('/')
            
            # Remove media URL prefix if present
            media_url = getattr(settings, 'MEDIA_URL', '/media/').lstrip('/')
            if filename.startswith(media_url):
                filename = filename[len(media_url):]
            
            if self.storage.exists(filename):
                self.storage.delete(filename)
                LOGGER.info(f"Successfully deleted image: {filename}")
                return True
            else:
                LOGGER.warning(f"Image file not found for deletion: {filename}")
                return False
                
        except Exception as e:
            LOGGER.error(f"Image delete failed: {str(e)}")
            return False

    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        if '.' in filename:
            return '.' + filename.split('.')[-1].lower()
        return '.jpg'  # Default extension


class LocalImageUploadService(DjangoStorageImageUploadService):
    """Image upload service for local file storage."""
    
    def __init__(self):
        from django.core.files.storage import FileSystemStorage
        # Use local filesystem storage
        storage = FileSystemStorage(
            location=getattr(settings, 'MEDIA_ROOT', '/tmp'),
            base_url=getattr(settings, 'MEDIA_URL', '/media/')
        )
        super().__init__(storage)


class S3ImageUploadService(DjangoStorageImageUploadService):
    """Image upload service using S3-compatible storage via django-storages."""
    
    def __init__(self):
        try:
            from storages.backends.s3boto3 import S3Boto3Storage
        except ImportError:
            raise ImportError(
                "S3 storage requires 'django-storages[boto3]' to be installed. "
                "Install with: pip install 'django-storages[boto3]'"
            )
        
        # Create S3 storage with settings
        storage = S3Boto3Storage(
            bucket_name=getattr(settings, 'IMAGE_UPLOAD_BUCKET', None),
            region_name=getattr(settings, 'IMAGE_UPLOAD_REGION', 'auto'),
            endpoint_url=getattr(settings, 'IMAGE_UPLOAD_ENDPOINT_URL', None),
            access_key=getattr(settings, 'IMAGE_UPLOAD_ACCESS_KEY', None),
            secret_key=getattr(settings, 'IMAGE_UPLOAD_SECRET_KEY', None),
            custom_domain=getattr(settings, 'IMAGE_UPLOAD_PUBLIC_URL_BASE', None),
            file_overwrite=False,
            default_acl='public-read'
        )
        super().__init__(storage)


def get_image_upload_service() -> ImageUploadService:
    """
    Factory function to get the configured image upload service.
    
    Returns:
        Configured ImageUploadService instance
    """
    service_type = getattr(settings, 'IMAGE_UPLOAD_SERVICE', 'local')
    if service_type is None:
        service_type = 'local'
    service_type = service_type.lower()
    
    if service_type == 's3':
        return S3ImageUploadService()
    elif service_type == 'local':
        return LocalImageUploadService()
    else:
        raise ValueError(f"Unknown image upload service type: {service_type}")