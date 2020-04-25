import json
import logging
from datetime import datetime
from tempfile import mkstemp
import uuid

from django.conf import settings
from django.http import HttpResponse, JsonResponse
import django_q.tasks
from rest_framework.decorators import api_view

from .utils import _get_client_ip
from ..models import Image
from .utils import (
    _is_image,
    _get_image_original_date,
)
LOGGER = logging.getLogger('django')

@api_view(['POST'])
def post_image(request):
    client_ip = _get_client_ip(request)
    req_body = request.POST.get('json')
    if req_body is not None:
        img_info = json.loads(req_body)['data']
        try:
            path = img_info['path']
        except KeyError:
            return HttpResponse(
                "If json body is provided, then a image url path should be provided",
                status=400,
            )
        LOGGER.info(f"{client_ip} : <post_image> bypass file uploading with url: {path}")
        orig_time_str = img_info.get('exif', {}).get('DateTimeOriginal')
        orig_time = None if orig_time_str is None else datetime.strptime(orig_time_str, "%Y:%m:%d %H:%M:%S")
        orig_lat = img_info.get('exif', {}).get('Latitude')
        orig_lng = img_info.get('exif', {}).get('Longitude')
        img = Image.objects.create(
            image_path=path,
            orig_time=orig_time,
            orig_lat=orig_lat,
            orig_lng=orig_lng,
        )
        return JsonResponse({"token": img.id})
    else:
        f_image = request.FILES['image']
        if _is_image(f_image):
            f_image.seek(0)
            image_original_date = _get_image_original_date(f_image)
            kwargs = {
                'image_path': '',
                'orig_time': image_original_date,
            }
            img = Image.objects.create(**kwargs)
            f_image.seek(0)

            temp_fname = uuid.uuid4()
            temp_image_path = f"/tmp/{temp_fname}.jpg"
            with open(temp_image_path, 'wb') as fw:
                fw.write(f_image.read())
            django_q.tasks.async_task(
                'api.tasks.upload_image',
                temp_image_path,
                settings.IMGUR_CLIENT_ID,
                img.id,
            )
            LOGGER.info(f"{client_ip} : <post_image> img.id:{img.id} {image_original_date} ")
            return JsonResponse({"token": img.id})
        LOGGER.warning(f" {client_ip} : <uploaded file cannot be parsed to Image> ")
        return HttpResponse(
            "The uploaded file cannot be parsed to Image",
            status=400,
        )
