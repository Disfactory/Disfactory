import json
import logging
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.models import Image
from .utils import _get_client_ip

LOGGER = logging.getLogger('django')


@swagger_auto_schema(
    method="post",
    operation_summary='上傳圖片',
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
        200: openapi.Response('圖片資料', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='image id'
                ),
            }
        )),
        400: "request failed"
    }
)
@api_view(['POST'])
def post_image_url(request):
    user_ip = _get_client_ip(request)

    try:
        post_body = request.data
    except json.JSONDecodeError:
        LOGGER.error(f'post_image_url received non-json body from {user_ip}')
        return HttpResponse('Post body should be JSON', status=400)

    if 'url' not in post_body:
        LOGGER.error(f'post_image_url received no url from {user_ip}')
        return HttpResponse('`url` should be in post body', status=400)

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

    image = Image.objects.create(
        image_path=img_url,
        orig_lat=post_body.get('Latitude'),
        orig_lng=post_body.get('Longitude'),
        orig_time=orig_time,
    )

    return JsonResponse({'token': image.id})
