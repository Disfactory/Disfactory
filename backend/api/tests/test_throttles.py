"""
Tests for rate limiting throttles.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.http import HttpRequest
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, throttle_classes

from api.throttles import (
    ImageUploadAnonThrottle,
    ImageUploadBurstAnonThrottle,
    ImageUploadUserThrottle,
    ImageUploadBurstUserThrottle,
)


class TestImageUploadThrottles(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'image_upload': '10/hour',
                'image_upload_burst': '3/min',
            }
        }
    )
    def test_anon_throttle_initialization(self):
        """Test anonymous throttle initialization."""
        throttle = ImageUploadAnonThrottle()
        assert throttle.scope == 'image_upload'

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'image_upload': '10/hour',
                'image_upload_burst': '3/min',
            }
        }
    )
    def test_burst_throttle_initialization(self):
        """Test burst throttle initialization."""
        throttle = ImageUploadBurstAnonThrottle()
        assert throttle.scope == 'image_upload_burst'

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'image_upload': '10/hour',
                'image_upload_burst': '3/min',
            }
        }
    )
    def test_user_throttle_initialization(self):
        """Test user throttle initialization."""
        throttle = ImageUploadUserThrottle()
        assert throttle.scope == 'image_upload'

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'image_upload': '10/hour',
                'image_upload_burst': '3/min',
            }
        }
    )
    def test_burst_user_throttle_initialization(self):
        """Test burst user throttle initialization."""
        throttle = ImageUploadBurstUserThrottle()
        assert throttle.scope == 'image_upload_burst'

    def test_throttle_allow_request(self):
        """Test throttle allows initial requests."""
        request = self.factory.post('/test')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        throttle = ImageUploadAnonThrottle()
        
        # Mock the rate to allow testing without actual rate limiting
        with patch.object(throttle, 'get_rate', return_value='10/min'):
            # First request should be allowed
            allowed = throttle.allow_request(request, None)
            assert allowed is True

    def test_throttle_cache_key_generation(self):
        """Test throttle generates cache keys correctly."""
        request = self.factory.post('/test')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        throttle = ImageUploadAnonThrottle()
        cache_key = throttle.get_cache_key(request, None)
        
        # Should generate a cache key for anonymous requests
        assert cache_key is not None
        assert 'throttle_anon' in cache_key
        assert '127.0.0.1' in cache_key