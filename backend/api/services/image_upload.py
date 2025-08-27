"""
Local image upload service for replacing Imgur API.

This service provides local filesystem-based image upload functionality
while maintaining API compatibility with minimal changes.
"""

import os
import uuid
import logging
from urllib.parse import urljoin
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS

LOGGER = logging.getLogger("django")


class ImageUploadService:
    """Service for handling local image uploads with EXIF processing."""
    
    ALLOWED_FORMATS = {'JPEG', 'JPG', 'PNG', 'WEBP'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        self.media_root = settings.MEDIA_ROOT
        self.media_url = settings.MEDIA_URL
        self.domain = settings.DOMAIN
        
        # Ensure media directory exists
        os.makedirs(self.media_root, exist_ok=True)
    
    def process_image(self, uploaded_file: UploadedFile) -> Dict[str, Any]:
        """
        Process uploaded image file and return Imgur-compatible response.
        
        Args:
            uploaded_file: Django UploadedFile instance
            
        Returns:
            Dict containing success/error response in Imgur format
        """
        try:
            # Validate file
            validation_error = self._validate_file(uploaded_file)
            if validation_error:
                return self._error_response(validation_error, 400)
            
            # Extract EXIF data before processing
            exif_data = self._extract_exif_data(uploaded_file)
            
            # Generate unique filename
            filename = f"{uuid.uuid4()}.jpg"
            file_path = os.path.join(self.media_root, filename)
            
            # Process and save image
            self._process_and_save_image(uploaded_file, file_path)
            
            # Construct response
            image_url = urljoin(self.domain, self.media_url.lstrip('/') + filename)
            deletehash = f"delete_{str(uuid.uuid4()).replace('-', '')}"
            
            response_data = {
                "data": {
                    "link": image_url,
                    "deletehash": deletehash,
                    **exif_data
                },
                "success": True,
                "status": 200
            }
            
            LOGGER.info(f"Successfully processed image: {filename}")
            return response_data
            
        except Exception as e:
            LOGGER.error(f"Image processing failed: {str(e)}")
            return self._error_response("Internal server error", 500)
    
    def _validate_file(self, uploaded_file: UploadedFile) -> Optional[str]:
        """Validate uploaded file format and size."""
        
        # Check file size
        if uploaded_file.size > self.MAX_FILE_SIZE:
            return "File too large"
        
        # Check if it's actually an image
        try:
            with Image.open(uploaded_file) as img:
                if img.format not in self.ALLOWED_FORMATS:
                    LOGGER.warning(f"Invalid image format: {img.format}")
                    return "Invalid image format"
        except Exception as e:
            LOGGER.warning(f"Failed to open image: {str(e)}")
            return "Invalid image format"
        
        # Reset file pointer after validation
        uploaded_file.seek(0)
        return None
    
    def _extract_exif_data(self, uploaded_file: UploadedFile) -> Dict[str, Any]:
        """Extract GPS coordinates and datetime from EXIF data."""
        exif_data = {}
        
        try:
            with Image.open(uploaded_file) as img:
                exif = img._getexif()
                
                if exif is not None:
                    # Extract GPS coordinates
                    lat, lng = self._extract_gps_coordinates(exif)
                    if lat is not None and lng is not None:
                        exif_data["Latitude"] = lat
                        exif_data["Longitude"] = lng
                    
                    # Extract datetime
                    datetime_original = self._extract_datetime(exif)
                    if datetime_original:
                        exif_data["DateTimeOriginal"] = datetime_original
                        
        except Exception as e:
            LOGGER.warning(f"Failed to extract EXIF data: {str(e)}")
        
        # Reset file pointer
        uploaded_file.seek(0)
        return exif_data
    
    def _extract_gps_coordinates(self, exif: Dict) -> Tuple[Optional[float], Optional[float]]:
        """Extract GPS coordinates from EXIF data."""
        try:
            gps_info = exif.get(34853)  # GPS IFD tag
            if not gps_info:
                return None, None
            
            def convert_to_degrees(value):
                """Convert GPS coordinate to decimal degrees."""
                d, m, s = value
                # Handle tuples like (23, 1) which represent fractions
                def fraction_to_float(frac):
                    if isinstance(frac, tuple) and len(frac) == 2:
                        return float(frac[0]) / float(frac[1])
                    return float(frac)
                
                return fraction_to_float(d) + fraction_to_float(m)/60 + fraction_to_float(s)/3600
            
            lat = lng = None
            
            # Latitude
            if 2 in gps_info and 1 in gps_info:  # GPSLatitude and GPSLatitudeRef
                lat = convert_to_degrees(gps_info[2])
                if gps_info[1] == 'S':
                    lat = -lat
            
            # Longitude 
            if 4 in gps_info and 3 in gps_info:  # GPSLongitude and GPSLongitudeRef
                lng = convert_to_degrees(gps_info[4])
                if gps_info[3] == 'W':
                    lng = -lng
            
            return lat, lng
            
        except Exception as e:
            LOGGER.warning(f"Failed to extract GPS coordinates: {str(e)}")
            return None, None
    
    def _extract_datetime(self, exif: Dict) -> Optional[str]:
        """Extract datetime from EXIF data."""
        try:
            # Try multiple datetime tags
            datetime_tags = [36867, 36868, 306]  # DateTimeOriginal, DateTimeDigitized, DateTime
            
            for tag in datetime_tags:
                if tag in exif:
                    datetime_str = exif[tag]
                    # Validate datetime format
                    try:
                        datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
                        return datetime_str
                    except ValueError:
                        continue
            
            return None
            
        except Exception as e:
            LOGGER.warning(f"Failed to extract datetime: {str(e)}")
            return None
    
    def _process_and_save_image(self, uploaded_file: UploadedFile, file_path: str):
        """Process image (strip EXIF) and save to filesystem."""
        
        with Image.open(uploaded_file) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save without EXIF data (strips metadata)
            img.save(file_path, 'JPEG', quality=85, optimize=True)
    
    def _error_response(self, error_message: str, status_code: int) -> Dict[str, Any]:
        """Create error response in Imgur format."""
        return {
            "data": {
                "error": error_message
            },
            "success": False,
            "status": status_code
        }