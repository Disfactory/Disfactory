import random
from datetime import datetime

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from PIL import Image, ExifTags

from ..models import Factory


def _sample(objs, k):
    list_of_objs = list(objs)
    random.shuffle(list_of_objs)
    return list_of_objs[:k]


def _get_nearby_factories(latitude, longitude, radius):
    """Return nearby factories based on position and search range."""
    # NOTE: if we use h3 for geoencoding in the future, we can use h3.k_ring():
    # ref: https://observablehq.com/@nrabinowitz/h3-radius-lookup
    pnt = Point(x=longitude, y=latitude, srid=4326)
    pnt.transform(settings.POSTGIS_SRID)
    ids = Factory.objects.only("id").filter(point__distance_lte=(pnt, D(km=radius)))
    if len(ids) > settings.MAX_FACTORY_PER_GET:
        ids = _sample(ids, settings.MAX_FACTORY_PER_GET)
    return Factory.objects.filter(id__in=[obj.id for obj in ids])


def _get_client_ip(request):
    # ref: https://stackoverflow.com/a/30558984
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    elif request.META.get('HTTP_X_REAL_IP'):
        ip = request.META.get('HTTP_X_REAL_IP')
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _get_image_original_date(f_image):
    img = Image.open(f_image)

    exif_raw = img._getexif()
    if exif_raw is None:
        return None

    exif = {}
    for k, v in exif_raw.items():
        if k in ExifTags.TAGS:
            exif[ExifTags.TAGS[k]] = v

    try:
        return datetime.strptime(exif["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
    except:
        return None


def _is_image(f_image):
    try:
        Image.open(f_image)
        return True
    except IOError:
        return False
