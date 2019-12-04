from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from rest_framework.decorators import api_view

from ..models import Image, Factory, ReportRecord
from ..serializers import ImageSerializer
from .utils import (
    _is_image,
    _upload_image,
    _get_image_original_date,
    _get_client_ip,
)
import logging
logger = logging.getLogger('django')


@api_view(['POST'])
def post_factory_image(request, factory_id):
    client_ip = _get_client_ip(request)
    if not Factory.objects.filter(pk=factory_id).exists():
        logger.warning(f" {client_ip} : <{factory_id} does not exist.> ")
        return HttpResponse(
            f"Factory ID {factory_id} does not exist.",
            status=400,
        )
    f_image = request.FILES['image']
    if not _is_image(f_image):
        logger.warning(f" {client_ip} : <The uploaded file cannot be parsed to Image> ")
        return HttpResponse(
            "The uploaded file cannot be parsed to Image",
            status=400,
        )

    f_image.seek(0)
    path = _upload_image(f_image, settings.IMGUR_CLIENT_ID)
    f_image.seek(0)
    image_original_date = _get_image_original_date(f_image)

    with transaction.atomic():
        factory = Factory.objects.only("id").get(pk=factory_id)
        report_record = ReportRecord.objects.create(
            factory=factory,
            user_ip=client_ip,
            action_type="POST_IMAGE",
            action_body={},
        )
        img = Image.objects.create(
            image_path=path,
            orig_time=image_original_date,
            factory=factory,
            report_record=report_record,
        )
    logger.info(f" {client_ip} : <Post Factory Image> {factory} {factory_id} {path} ")
    img_serializer = ImageSerializer(img)
    return JsonResponse(img_serializer.data, safe=False)
