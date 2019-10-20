from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from ..models import Factory


def _upload_image(f_image):
    """Upload Image to certain service."""
    # TODO
    # image_binary = f_image.read()
    # resp = requests.post(...)
    path = "path to image cdn"
    return path


def _get_nearby_factories(latitude, longitude, radius):
    """Return nearby factories based on position and search range."""
    pass
