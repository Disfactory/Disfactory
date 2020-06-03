import json
import logging
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

from api.models import Image
from .utils import _get_client_ip

LOGGER = logging.getLogger('django')


@api_view(['POST'])
def post_image_url(request):
    user_ip = _get_client_ip(request)

    try:
        post_body = json.loads(request.body)
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
            LOGGER.warning(f'post_image_url cannot parse DateTimeOriginal {orig_time_str}')
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

