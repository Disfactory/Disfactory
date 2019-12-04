from django.conf import settings
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

from ..models import Image
from .utils import (
    _is_image,
    _upload_image,
    _get_image_original_date,
    _get_client_ip,
)

import logging
logger = logging.getLogger('django')


@api_view(['POST'])
def post_image(request):
    f_image = request.FILES['image']
    
    client_ip = _get_client_ip(request)
    
    if _is_image(f_image):
        f_image.seek(0)
        path = _upload_image(f_image, settings.IMGUR_CLIENT_ID)
        f_image.seek(0)
        image_original_date = _get_image_original_date(f_image)
        args = {
            'image_path': path,
            'orig_time': image_original_date,
        }
        img = Image.objects.create(**args)
        logger.info(f" {client_ip} : <post_image>  {args}  ")
        return JsonResponse({"token": img.id})
    logger.warning(f" {client_ip} : <uploaded file cannot be parsed to Image> ")
    return HttpResponse(
        "The uploaded file cannot be parsed to Image",
        status=400,
    )
