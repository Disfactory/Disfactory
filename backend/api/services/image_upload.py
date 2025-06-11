import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from urllib.parse import urljoin
from uuid import uuid4

from django.conf import settings
import requests

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
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        
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
        
        try:
            resp = requests.post(
                "https://api.imgur.com/3/image",
                data={"image": image_buffer},
                headers=headers,
                timeout=30
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
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def upload(self, image_buffer: bytes) -> Dict[str, Any]:
        """Upload image to ImageBB."""
        if not self.api_key:
            return {
                "success": False,
                "error": "ImageBB API key not configured",
                "url": None,
                "delete_hash": None
            }
            
        try:
            import base64
            image_b64 = base64.b64encode(image_buffer).decode('utf-8')
            
            resp = requests.post(
                "https://api.imgbb.com/1/upload",
                data={
                    "key": self.api_key,
                    "image": image_b64,
                },
                timeout=30
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
        self.backends = self._initialize_backends()
        
    def _initialize_backends(self):
        """Initialize available backends based on configuration."""
        backends = []
        
        # Add Imgur if configured
        imgur_client_id = getattr(settings, 'IMGUR_CLIENT_ID', None)
        if imgur_client_id:
            backends.append(ImgurBackend(imgur_client_id))
            
        # Add ImageBB if configured
        imagebb_api_key = getattr(settings, 'IMAGEBB_API_KEY', None)
        if imagebb_api_key:
            backends.append(ImageBBBackend(imagebb_api_key))
            
        # Always add local as fallback
        backends.append(LocalBackend())
        
        return backends
    
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
        if not self.backends:
            return {
                "success": False,
                "error": "No image upload backends configured",
                "url": None,
                "delete_hash": None,
                "backend_used": None
            }
        
        errors = []
        
        for backend in self.backends:
            LOGGER.info(f"Attempting image upload with {backend.get_name()} backend")
            
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
                    errors.append(error_msg)
                    LOGGER.warning(f"Upload failed with {backend.get_name()}: {result['error']}")
                    
            except Exception as e:
                error_msg = f"{backend.get_name()}: Unexpected error: {str(e)}"
                errors.append(error_msg)
                LOGGER.error(f"Unexpected error with {backend.get_name()}: {str(e)}")
        
        # All backends failed
        return {
            "success": False,
            "error": f"All backends failed: {'; '.join(errors)}",
            "url": None,
            "delete_hash": None,
            "backend_used": None
        }