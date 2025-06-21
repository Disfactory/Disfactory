"""
Custom throttle classes for API rate limiting.
"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class ImageUploadAnonThrottle(AnonRateThrottle):
    """Rate limiting for anonymous users uploading images."""
    scope = 'image_upload'


class ImageUploadBurstAnonThrottle(AnonRateThrottle):
    """Burst protection for anonymous users uploading images."""
    scope = 'image_upload_burst'


class ImageUploadUserThrottle(UserRateThrottle):
    """Rate limiting for authenticated users uploading images."""
    scope = 'image_upload'


class ImageUploadBurstUserThrottle(UserRateThrottle):
    """Burst protection for authenticated users uploading images."""
    scope = 'image_upload_burst'