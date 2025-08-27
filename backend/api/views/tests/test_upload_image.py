import os
import tempfile
import uuid
from io import BytesIO
from unittest.mock import patch, Mock

import pytest
from PIL import Image as PILImage
from django.test import Client
from django.conf import settings

from api.services.image_upload import ImageUploadService


@pytest.mark.django_db
class TestImageUploadService:
    """Test the ImageUploadService class."""

    def test_process_image_success(self):
        """Test successful image processing."""
        # Create a simple test image
        img = PILImage.new('RGB', (100, 100), color='red')
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        # Mock uploaded file
        uploaded_file = Mock()
        uploaded_file.size = len(img_buffer.getvalue())
        uploaded_file.seek = img_buffer.seek
        uploaded_file.read = img_buffer.read
        
        # Patch PIL Image.open to return our test image
        with patch('api.services.image_upload.Image.open') as mock_open:
            mock_open.return_value.__enter__.return_value = img
            mock_open.return_value.__exit__.return_value = None
            
            service = ImageUploadService()
            with tempfile.TemporaryDirectory() as temp_dir:
                service.media_root = temp_dir
                result = service.process_image(uploaded_file)
        
        assert result['success'] is True
        assert result['status'] == 200
        assert 'link' in result['data']
        assert 'deletehash' in result['data']
        assert result['data']['link'].endswith('.jpg')
        assert result['data']['deletehash'].startswith('delete_')

    def test_process_image_file_too_large(self):
        """Test handling of files that are too large."""
        uploaded_file = Mock()
        uploaded_file.size = ImageUploadService.MAX_FILE_SIZE + 1
        
        service = ImageUploadService()
        result = service.process_image(uploaded_file)
        
        assert result['success'] is False
        assert result['status'] == 400
        assert 'File too large' in result['data']['error']

    def test_process_image_invalid_format(self):
        """Test handling of invalid image formats."""
        uploaded_file = Mock()
        uploaded_file.size = 1000
        uploaded_file.seek = Mock()
        
        # Mock PIL to raise exception for invalid format
        with patch('api.services.image_upload.Image.open') as mock_open:
            mock_open.side_effect = Exception("Invalid format")
            
            service = ImageUploadService()
            result = service.process_image(uploaded_file)
        
        assert result['success'] is False
        assert result['status'] == 400
        assert 'Invalid image format' in result['data']['error']

    def test_extract_gps_coordinates(self):
        """Test GPS coordinate extraction from EXIF."""
        service = ImageUploadService()
        
        # Mock EXIF data with GPS info
        exif_data = {
            34853: {  # GPS IFD tag
                1: 'N',  # GPSLatitudeRef
                2: [(23, 1), (30, 1), (0, 1)],  # GPSLatitude (23°30'0")
                3: 'E',  # GPSLongitudeRef
                4: [(121, 1), (30, 1), (0, 1)],  # GPSLongitude (121°30'0")
            }
        }
        
        lat, lng = service._extract_gps_coordinates(exif_data)
        
        assert lat == 23.5
        assert lng == 121.5

    def test_extract_datetime(self):
        """Test datetime extraction from EXIF."""
        service = ImageUploadService()
        
        # Mock EXIF data with datetime
        exif_data = {
            36867: "2023:08:27 15:30:45"  # DateTimeOriginal
        }
        
        datetime_str = service._extract_datetime(exif_data)
        
        assert datetime_str == "2023:08:27 15:30:45"


@pytest.mark.django_db 
class TestUploadImageView:
    """Test the upload_image view."""

    def test_upload_image_success(self, client):
        """Test successful image upload via API."""
        # Create a test image file
        img = PILImage.new('RGB', (100, 100), color='blue')
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        # Create a proper file-like object for the test
        img_buffer.name = 'test.jpg'
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('django.conf.settings.MEDIA_ROOT', temp_dir):
                response = client.post(
                    '/api/upload-image',
                    {'image': img_buffer},
                    format='multipart'
                )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['success'] is True
        assert 'link' in response_data['data']
        assert 'deletehash' in response_data['data']

    def test_upload_image_no_file(self, client):
        """Test upload without file."""
        response = client.post('/api/upload-image', {})
        
        assert response.status_code == 400
        response_data = response.json()
        assert response_data['success'] is False
        assert 'No image file provided' in response_data['data']['error']

    def test_upload_image_empty_file(self, client):
        """Test upload with empty file."""
        empty_file = BytesIO(b'')
        empty_file.name = 'empty.jpg'
        
        response = client.post(
            '/api/upload-image',
            {'image': empty_file},
            format='multipart'
        )
        
        assert response.status_code == 400
        response_data = response.json()
        assert response_data['success'] is False
        assert 'Empty file provided' in response_data['data']['error']

    def test_upload_image_with_exif_data(self, client):
        """Test upload preserves EXIF GPS and datetime data."""
        # This test would need a real image with EXIF data
        # For now, we'll mock the EXIF extraction
        img = PILImage.new('RGB', (100, 100), color='green')
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        img_buffer.name = 'test_with_exif.jpg'
        
        # Mock the EXIF extraction to return test data
        mock_exif_data = {
            "Latitude": 23.5,
            "Longitude": 121.5,
            "DateTimeOriginal": "2023:08:27 15:30:45"
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('django.conf.settings.MEDIA_ROOT', temp_dir):
                with patch('api.services.image_upload.ImageUploadService._extract_exif_data', return_value=mock_exif_data):
                    response = client.post(
                        '/api/upload-image',
                        {'image': img_buffer},
                        format='multipart'
                    )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['success'] is True
        assert response_data['data']['Latitude'] == 23.5
        assert response_data['data']['Longitude'] == 121.5
        assert response_data['data']['DateTimeOriginal'] == "2023:08:27 15:30:45"