import json
from datetime import datetime
import logging
import uuid

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.db import transaction
import django_q.tasks

from rest_framework.decorators import api_view

from api.models import Image, Factory, ReportRecord
from api.serializers import ImageSerializer
from ..utils import _get_client_ip
from .utils import (
    _is_image,
    _get_image_original_date,
)

LOGGER = logging.getLogger('django')


@api_view(['POST'])
def post_factory_image(request, factory_id):
    client_ip = _get_client_ip(request)
    if not Factory.objects.filter(pk=factory_id).exists():
        LOGGER.warning(f"{client_ip} : <{factory_id} does not exist.> ")
        return HttpResponse(
            f"Factory ID {factory_id} does not exist.",
            status=400,
        )
    put_body = request.POST

    if 'json' in put_body:
        img_info = json.loads(put_body['json'])['data']
        try:
            image_path = img_info['path']
        except KeyError:
            return HttpResponse(
                "If json body is provided, then a image url path should be provided",
                status=400,
            )
        LOGGER.info(f"{client_ip} : <post_factory_image> upload image for Factory({factory_id}) bypass file uploading with url: {image_path}")
        orig_time_str = img_info.get('exif', {}).get('DateTimeOriginal')
        image_original_date = None if orig_time_str is None else datetime.strptime(orig_time_str, "%Y:%m:%d %H:%M:%S")
        orig_lat = img_info.get('exif', {}).get('Latitude')
        orig_lng = img_info.get('exif', {}).get('Longitude')
    else:
        f_image = request.FILES['image']
        if not _is_image(f_image):
            LOGGER.warning(f"{client_ip} : <The uploaded file cannot be parsed to Image> ")
            return HttpResponse(
                "The uploaded file cannot be parsed to Image",
                status=400,
            )

        f_image.seek(0)
        image_original_date = _get_image_original_date(f_image)
        orig_lat = None
        orig_lng = None
        # upload to imgur
        f_image.seek(0)
        temp_fname = uuid.uuid4()
        temp_image_path = f"/tmp/{temp_fname}.jpg"
        with open(temp_image_path, 'wb') as fw:
            fw.write(f_image.read())
        image_path = ''

    with transaction.atomic():
        factory = Factory.objects.only("id").get(pk=factory_id)
        report_record = ReportRecord.objects.create(
            factory=factory,
            user_ip=client_ip,
            action_type="POST_IMAGE",
            action_body={},
            nickname=put_body.get("nickname"),
            contact=put_body.get("contact"),
        )
        img = Image.objects.create(
            image_path=image_path,
            orig_time=image_original_date,
            orig_lat=orig_lat,
            orig_lng=orig_lng,
            factory=factory,
            report_record=report_record,
        )
    if 'json' not in put_body:  # user upload the image directly
        django_q.tasks.async_task(
            'api.tasks.upload_image',
            temp_image_path,
            settings.IMGUR_CLIENT_ID,
            img.id,
        )
        LOGGER.info(f"{client_ip} : <Post Factory Image> {factory} {factory_id} {temp_image_path} ")
    else:
        LOGGER.info(f"{client_ip} : <Post Factory Image> {factory} {factory_id} {image_path} ")
    img_serializer = ImageSerializer(img)
    return JsonResponse(img_serializer.data, safe=False)
