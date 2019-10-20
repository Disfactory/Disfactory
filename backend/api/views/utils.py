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
    # NOTE: if we use h3 for geoencoding in the future, we can use h3.k_ring():
    # ref: https://observablehq.com/@nrabinowitz/h3-radius-lookup
    pnt = Point(x=longitude, y=latitude, srid=4326)
    pnt.transform(settings.POSTGIS_SRID)
    return Factory.objects.filter(point__distance_lte=(pnt, D(km=radius)))
