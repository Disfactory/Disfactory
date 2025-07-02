import logging
import uuid
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Dict, Optional, Any
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

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


class S3ImageUploadService(ImageUploadService):
    """Image upload service using AWS S3 or S3-compatible storage (like Cloudflare R2)."""

    def __init__(self):
        self.bucket_name = getattr(settings, 'IMAGE_UPLOAD_BUCKET', None)
        self.region = getattr(settings, 'IMAGE_UPLOAD_REGION', 'auto')
        self.endpoint_url = getattr(settings, 'IMAGE_UPLOAD_ENDPOINT_URL', None)
        self.access_key = getattr(settings, 'IMAGE_UPLOAD_ACCESS_KEY', None)
        self.secret_key = getattr(settings, 'IMAGE_UPLOAD_SECRET_KEY', None)
        self.public_url_base = getattr(settings, 'IMAGE_UPLOAD_PUBLIC_URL_BASE', None)

        if not all([self.bucket_name, self.access_key, self.secret_key]):
            raise ValueError("Missing required S3 configuration: bucket_name, access_key, secret_key")

        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )

    def upload_image(self, image_file: InMemoryUploadedFile, filename: Optional[str] = None) -> ImageUploadResult:
        """Upload image to S3-compatible storage."""
        try:
            # Generate filename if not provided
            if not filename:
                file_extension = self._get_file_extension(image_file.name)
                filename = f"{uuid.uuid4()}{file_extension}"

            # Upload to S3
            self.s3_client.upload_fileobj(
                image_file,
                self.bucket_name,
                filename,
                ExtraArgs={
                    'ContentType': image_file.content_type or 'image/jpeg',
                    'ACL': 'public-read'  # Make image publicly accessible
                }
            )

            # Generate public URL
            if self.public_url_base:
                url = f"{self.public_url_base.rstrip('/')}/{filename}"
            else:
                url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"

            LOGGER.info(f"Successfully uploaded image to S3: {filename}")
            return ImageUploadResult(
                success=True,
                url=url,
                metadata={'filename': filename, 'bucket': self.bucket_name}
            )

        except ClientError as e:
            error_msg = f"S3 upload failed: {str(e)}"
            LOGGER.error(error_msg)
            return ImageUploadResult(success=False, error=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during S3 upload: {str(e)}"
            LOGGER.error(error_msg)
            return ImageUploadResult(success=False, error=error_msg)

    def delete_image(self, url: str) -> bool:
        """Delete image from S3-compatible storage."""
        try:
            # Extract filename from URL
            filename = url.split('/')[-1]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            
            LOGGER.info(f"Successfully deleted image from S3: {filename}")
            return True
            
        except ClientError as e:
            LOGGER.error(f"S3 delete failed: {str(e)}")
            return False
        except Exception as e:
            LOGGER.error(f"Unexpected error during S3 delete: {str(e)}")
            return False

    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        if '.' in filename:
            return '.' + filename.split('.')[-1].lower()
        return '.jpg'  # Default extension


class LocalImageUploadService(ImageUploadService):
    """Image upload service for local file storage (fallback/development)."""

    def __init__(self):
        self.upload_dir = getattr(settings, 'MEDIA_ROOT', '/tmp')
        self.public_url_base = getattr(settings, 'MEDIA_URL', '/media/')

    def upload_image(self, image_file: InMemoryUploadedFile, filename: Optional[str] = None) -> ImageUploadResult:
        """Upload image to local storage."""
        try:
            import os
            
            # Generate filename if not provided
            if not filename:
                file_extension = self._get_file_extension(image_file.name)
                filename = f"{uuid.uuid4()}{file_extension}"

            # Create upload directory if it doesn't exist
            os.makedirs(self.upload_dir, exist_ok=True)
            
            # Write file to local storage
            file_path = os.path.join(self.upload_dir, filename)
            with open(file_path, 'wb') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)

            # Generate public URL
            url = f"{settings.DOMAIN.rstrip('/')}{self.public_url_base.rstrip('/')}/{filename}"

            LOGGER.info(f"Successfully uploaded image locally: {filename}")
            return ImageUploadResult(
                success=True,
                url=url,
                metadata={'filename': filename, 'path': file_path}
            )

        except Exception as e:
            error_msg = f"Local upload failed: {str(e)}"
            LOGGER.error(error_msg)
            return ImageUploadResult(success=False, error=error_msg)

    def delete_image(self, url: str) -> bool:
        """Delete image from local storage."""
        try:
            import os
            
            # Extract filename from URL
            filename = url.split('/')[-1]
            file_path = os.path.join(self.upload_dir, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                LOGGER.info(f"Successfully deleted local image: {filename}")
                return True
            else:
                LOGGER.warning(f"Image file not found for deletion: {filename}")
                return False
                
        except Exception as e:
            LOGGER.error(f"Local delete failed: {str(e)}")
            return False

    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        if '.' in filename:
            return '.' + filename.split('.')[-1].lower()
        return '.jpg'  # Default extension


def get_image_upload_service() -> ImageUploadService:
    """
    Factory function to get the configured image upload service.
    
    Returns:
        Configured ImageUploadService instance
    """
    service_type = getattr(settings, 'IMAGE_UPLOAD_SERVICE', 'local').lower()
    
    if service_type == 's3':
        return S3ImageUploadService()
    elif service_type == 'local':
        return LocalImageUploadService()
    else:
        raise ValueError(f"Unknown image upload service type: {service_type}")