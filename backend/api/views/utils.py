from datetime import datetime

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
import requests
from PIL import Image, ExifTags

from ..models import Factory


def _upload_image(f_image, client_id):
    headers = {'Authorization': f'Client-ID {client_id}'}
    data = {'image': f_image.read()}
    resp = requests.post(
        'https://api.imgur.com/3/upload',
        data=data,
        headers=headers,
    )
    path = resp.json()['data']['link']
    return path


def _get_nearby_factories(latitude, longitude, radius):
    """Return nearby factories based on position and search range."""
    # NOTE: if we use h3 for geoencoding in the future, we can use h3.k_ring():
    # ref: https://observablehq.com/@nrabinowitz/h3-radius-lookup
    pnt = Point(x=longitude, y=latitude, srid=4326)
    pnt.transform(settings.POSTGIS_SRID)
    return Factory.objects.filter(point__distance_lte=(pnt, D(km=radius)))


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

    exif = {}
    for k, v in img._getexif().items():
        if k in ExifTags.TAGS:
            exif[ExifTags.TAGS[k]] = v

    try:
        return datetime.strptime(exif["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
    except:
        return None
