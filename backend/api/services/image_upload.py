import os
import logging
import base64
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
from uuid import uuid4
from io import BytesIO

from django.conf import settings
import requests

# Optional PIL import for image validation
try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

LOGGER = logging.getLogger("django")


class ImageUploadBackend(ABC):
    """Abstract base class for image upload backends."""
    
    @abstractmethod
    def upload(self, image_buffer: bytes) -> Dict[str, Any]:
        """
        Upload image buffer to the backend.
        
        Args:
            image_buffer: Raw image data as bytes
            
        Returns:
            Dict containing:
                - url: The public URL of the uploaded image
                - delete_hash: Optional delete token for the image
                - success: Boolean indicating success
                - error: Error message if success is False
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of this backend."""
        pass


class ImgurBackend(ImageUploadBackend):
    """Imgur image upload backend."""
    
    def __init__(self, client_id: str, config: Dict[str, Any] = None):
        self.client_id = client_id
        self.config = config or {}
        
    def upload(self, image_buffer: bytes) -> Dict[str, Any]:
        """Upload image to Imgur."""
        if not self.client_id:
            return {
                "success": False,
                "error": "Imgur client ID not configured",
                "url": None,
                "delete_hash": None
            }
            
        headers = {"Authorization": f"Client-ID {self.client_id}"}
        timeout = self.config.get('REQUEST_TIMEOUT', 30)
        
        try:
            resp = requests.post(
                "https://api.imgur.com/3/image",
                data={"image": image_buffer},
                headers=headers,
                timeout=timeout
            )
            resp_data = resp.json()
            
            if "errors" in resp_data or resp.status_code != 200:
                # Log credits remaining if available
                try:
                    credit_resp = requests.get(
                        "https://api.imgur.com/3/credits",
                        headers=headers,
                        timeout=10
                    )
                    LOGGER.error(f"Imgur upload failed. Credits remaining: {credit_resp.json()}")
                except Exception:
                    pass
                    
                error_msg = resp_data.get("data", {}).get("error", "Unknown Imgur error")
                return {
                    "success": False,
                    "error": f"Imgur API error: {error_msg}",
                    "url": None,
                    "delete_hash": None
                }
            
            data = resp_data["data"]
            return {
                "success": True,
                "url": data["link"],
                "delete_hash": data.get("deletehash"),
                "error": None
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error uploading to Imgur: {str(e)}",
                "url": None,
                "delete_hash": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error uploading to Imgur: {str(e)}",
                "url": None,
                "delete_hash": None
            }
    
    def get_name(self) -> str:
        return "imgur"


class ImageBBBackend(ImageUploadBackend):
    """ImageBB image upload backend."""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        self.api_key = api_key
        self.config = config or {}
        
    def upload(self, image_buffer: bytes) -> Dict[str, Any]:
        """Upload image to ImageBB."""
        if not self.api_key:
            return {
                "success": False,
                "error": "ImageBB API key not configured",
                "url": None,
                "delete_hash": None
            }
            
        timeout = self.config.get('REQUEST_TIMEOUT', 30)
        
        try:
            image_b64 = base64.b64encode(image_buffer).decode('utf-8')
            
            resp = requests.post(
                "https://api.imgbb.com/1/upload",
                data={
                    "key": self.api_key,
                    "image": image_b64,
                },
                timeout=timeout
            )
            resp_data = resp.json()
            
            if not resp_data.get("success", False) or resp.status_code != 200:
                error_msg = resp_data.get("error", {}).get("message", "Unknown ImageBB error")
                return {
                    "success": False,
                    "error": f"ImageBB API error: {error_msg}",
                    "url": None,
                    "delete_hash": None
                }
            
            data = resp_data["data"]
            return {
                "success": True,
                "url": data["url"],
                "delete_hash": data.get("delete_url"),  # ImageBB provides delete_url instead
                "error": None
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error uploading to ImageBB: {str(e)}",
                "url": None,
                "delete_hash": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error uploading to ImageBB: {str(e)}",
                "url": None,
                "delete_hash": None
            }
    
    def get_name(self) -> str:
        return "imagebb"


class LocalBackend(ImageUploadBackend):
    """Local file storage backend as fallback."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    def upload(self, image_buffer: bytes) -> Dict[str, Any]:
        """Save image locally and return URL."""
        try:
            # Create temp file path
            filename = f"{uuid4()}.jpg"
            local_path = os.path.join(settings.MEDIA_ROOT, filename)
            
            # Ensure media directory exists
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            
            # Write image data
            with open(local_path, "wb") as f:
                f.write(image_buffer)
            
            # Generate public URL
            url = urljoin(
                urljoin(settings.DOMAIN, settings.MEDIA_URL), 
                filename
            )
            
            return {
                "success": True,
                "url": url,
                "delete_hash": None,  # Local storage doesn't provide delete hash
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error saving image locally: {str(e)}",
                "url": None,
                "delete_hash": None
            }
    
    def get_name(self) -> str:
        return "local"


class ImageUploadService:
    """Service for uploading images with multiple backend support and fallback."""
    
    def __init__(self):
        self.config = getattr(settings, 'IMAGE_UPLOAD_CONFIG', {})
        self.backends = self._initialize_backends()
        
    def _initialize_backends(self):
        """Initialize available backends based on configuration."""
        backends = []
        backend_order = self.config.get('BACKEND_ORDER', ['imgur', 'imagebb', 'local'])
        
        # Create backend instances based on order preference
        backend_map = {
            'imgur': self._create_imgur_backend,
            'imagebb': self._create_imagebb_backend,
            'local': self._create_local_backend,
        }
        
        for backend_name in backend_order:
            backend_name = backend_name.strip().lower()
            if backend_name in backend_map:
                backend = backend_map[backend_name]()
                if backend:
                    backends.append(backend)
        
        return backends
    
    def _create_imgur_backend(self) -> Optional['ImgurBackend']:
        """Create Imgur backend if configured."""
        imgur_client_id = getattr(settings, 'IMGUR_CLIENT_ID', None)
        if imgur_client_id:
            return ImgurBackend(imgur_client_id, self.config)
        return None
    
    def _create_imagebb_backend(self) -> Optional['ImageBBBackend']:
        """Create ImageBB backend if configured."""
        imagebb_api_key = getattr(settings, 'IMAGEBB_API_KEY', None)
        if imagebb_api_key:
            return ImageBBBackend(imagebb_api_key, self.config)
        return None
    
    def _create_local_backend(self) -> 'LocalBackend':
        """Create local backend (always available)."""
        return LocalBackend(self.config)
    
    def validate_image(self, image_buffer: bytes) -> Dict[str, Any]:
        """
        Validate image file before upload.
        
        Args:
            image_buffer: Raw image data as bytes
            
        Returns:
            Dict with validation result: {'valid': bool, 'error': str}
        """
        try:
            # Check file size
            max_size = self.config.get('MAX_FILE_SIZE', 10 * 1024 * 1024)  # 10MB default
            if len(image_buffer) > max_size:
                return {
                    'valid': False,
                    'error': f'File size too large. Maximum allowed: {max_size / 1024 / 1024:.1f}MB'
                }
            
            # Basic validation - check for common image file headers
            if not self._has_image_header(image_buffer):
                return {
                    'valid': False,
                    'error': 'Invalid image file format'
                }
            
            # Enhanced validation with PIL if available
            if PIL_AVAILABLE and self.config.get('VALIDATE_DIMENSIONS', False):
                try:
                    with PILImage.open(BytesIO(image_buffer)) as img:
                        # Check format
                        allowed_formats = self.config.get('ALLOWED_FORMATS', ['jpg', 'jpeg', 'png', 'gif', 'webp'])
                        if img.format.lower() not in [fmt.lower() for fmt in allowed_formats]:
                            return {
                                'valid': False,
                                'error': f'Invalid image format. Allowed: {", ".join(allowed_formats)}'
                            }
                        
                        # Check dimensions
                        max_width = self.config.get('MAX_WIDTH', 4096)
                        max_height = self.config.get('MAX_HEIGHT', 4096)
                        
                        if img.width > max_width or img.height > max_height:
                            return {
                                'valid': False,
                                'error': f'Image dimensions too large. Maximum: {max_width}x{max_height}px'
                            }
                
                except Exception as e:
                    return {
                        'valid': False,
                        'error': f'Invalid image file: {str(e)}'
                    }
            
            return {'valid': True, 'error': None}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}'
            }
    
    def _has_image_header(self, image_buffer: bytes) -> bool:
        """Check if the buffer starts with common image file headers."""
        if len(image_buffer) < 8:
            return False
        
        # Common image file signatures
        image_signatures = [
            b'\xff\xd8\xff',        # JPEG
            b'\x89PNG\r\n\x1a\n',   # PNG
            b'GIF87a',              # GIF87a
            b'GIF89a',              # GIF89a
            b'RIFF',                # WebP (RIFF container)
            b'BM',                  # BMP
        ]
        
        for signature in image_signatures:
            if image_buffer.startswith(signature):
                return True
        
        return False
    
    def upload_image(self, image_buffer: bytes) -> Dict[str, Any]:
        """
        Upload image using available backends with fallback.
        
        Args:
            image_buffer: Raw image data as bytes
            
        Returns:
            Dict containing:
                - url: The public URL of the uploaded image
                - delete_hash: Optional delete token for the image  
                - backend_used: Name of the backend that succeeded
                - success: Boolean indicating success
                - error: Error message if success is False
        """
        # Validate image first
        validation_result = self.validate_image(image_buffer)
        if not validation_result['valid']:
            return {
                "success": False,
                "error": f"Image validation failed: {validation_result['error']}",
                "url": None,
                "delete_hash": None,
                "backend_used": None
            }
        
        if not self.backends:
            return {
                "success": False,
                "error": "No image upload backends configured",
                "url": None,
                "delete_hash": None,
                "backend_used": None
            }
        
        errors = []
        retry_attempts = self.config.get('RETRY_ATTEMPTS', 1)
        retry_delay = self.config.get('RETRY_DELAY', 2)
        
        for backend in self.backends:
            LOGGER.info(f"Attempting image upload with {backend.get_name()} backend")
            
            # Try with retry logic
            for attempt in range(retry_attempts + 1):
                try:
                    result = backend.upload(image_buffer)
                    
                    if result["success"]:
                        LOGGER.info(f"Image uploaded successfully using {backend.get_name()}")
                        return {
                            **result,
                            "backend_used": backend.get_name()
                        }
                    else:
                        error_msg = f"{backend.get_name()}: {result['error']}"
                        if attempt == retry_attempts:  # Last attempt
                            errors.append(error_msg)
                            LOGGER.warning(f"Upload failed with {backend.get_name()} after {retry_attempts + 1} attempts: {result['error']}")
                        else:
                            LOGGER.info(f"Upload attempt {attempt + 1} failed with {backend.get_name()}, retrying in {retry_delay}s")
                            time.sleep(retry_delay)
                        
                except Exception as e:
                    error_msg = f"{backend.get_name()}: Unexpected error: {str(e)}"
                    if attempt == retry_attempts:  # Last attempt
                        errors.append(error_msg)
                        LOGGER.error(f"Unexpected error with {backend.get_name()} after {retry_attempts + 1} attempts: {str(e)}")
                    else:
                        LOGGER.info(f"Upload attempt {attempt + 1} had error with {backend.get_name()}, retrying in {retry_delay}s")
                        time.sleep(retry_delay)
        
        # All backends failed
        return {
            "success": False,
            "error": f"All backends failed: {'; '.join(errors)}",
            "url": None,
            "delete_hash": None,
            "backend_used": None
        }