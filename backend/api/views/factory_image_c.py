import json
import logging
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.db import transaction
from rest_framework.decorators import api_view

from api.models import Image, Factory, ReportRecord
from api.serializers import ImageSerializer
from .utils import _get_client_ip

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

LOGGER = logging.getLogger('django')


@swagger_auto_schema(
    method="post",
    operation_summary='上傳指定 id 的工廠圖片',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'url': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='image url',
            ),
            'DateTimeOriginal': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='YYYY:mm:dd HH:MM:SS',
            )
        }
    ),
    responses={
        200: openapi.Response('圖片資料', ImageSerializer),
        400: "request failed"
    }
)
@api_view(['POST'])
def post_factory_image_url(request, factory_id):
    user_ip = _get_client_ip(request)

    try:
        post_body = request.data
    except json.JSONDecodeError:
        LOGGER.error(
            f'post_factory_image_url received non-json body from {user_ip}')
        return HttpResponse('Post body should be JSON', status=400)

    if 'url' not in post_body:
        LOGGER.error(f'post_factory_image_url received no url from {user_ip}')
        return HttpResponse('`url` should be in post body', status=400)

    if not Factory.objects.filter(pk=factory_id).exists():
        LOGGER.warning(
            f"post_factory_image_url receiving {factory_id} that does not exist from {user_ip}")
        return HttpResponse(
            f"Factory ID {factory_id} does not exist.",
            status=400,
        )

    img_url = post_body['url']
    LOGGER.info(f'post_image_url {img_url} from {user_ip}')

    if 'DateTimeOriginal' in post_body:
        try:
            orig_time_str = post_body['DateTimeOriginal']
            orig_time = datetime.strptime(
                orig_time_str,
                "%Y:%m:%d %H:%M:%S",
            )
        except ValueError:
            LOGGER.warning(
                f'post_image_url cannot parse DateTimeOriginal {orig_time_str}')
            orig_time = None
    else:
        orig_time = None

    with transaction.atomic():
        factory = Factory.objects.only("id").get(pk=factory_id)
        report_record = ReportRecord.objects.create(
            factory=factory,
            user_ip=user_ip,
            action_type="POST_IMAGE",
            action_body={},
            nickname=post_body.get("nickname"),
            contact=post_body.get("contact"),
        )
        image = Image.objects.create(
            image_path=img_url,
            orig_lat=post_body.get('Latitude'),
            orig_lng=post_body.get('Longitude'),
            orig_time=orig_time,
            report_record=report_record,
            factory=factory,
        )

    img_serializer = ImageSerializer(image)
    return JsonResponse(img_serializer.data, safe=False)
