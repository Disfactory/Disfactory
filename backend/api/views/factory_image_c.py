import uuid

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.db import transaction
import django_q.tasks

from rest_framework.decorators import api_view

from ..models import Image, Factory, ReportRecord
from ..serializers import ImageSerializer
from .utils import (
    _is_image,
    _get_image_original_date,
    _get_client_ip,
)


@api_view(['POST'])
def post_factory_image(request, factory_id):
    if not Factory.objects.filter(pk=factory_id).exists():
        return HttpResponse(
            f"Factory ID {factory_id} does not exist.",
            status=400,
        )
    f_image = request.FILES['image']
    if not _is_image(f_image):
        return HttpResponse(
            "The uploaded file cannot be parsed to Image",
            status=400,
        )

    f_image.seek(0)
    image_original_date = _get_image_original_date(f_image)

    client_ip = _get_client_ip(request)

    put_body = request.POST

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
            image_path='',
            orig_time=image_original_date,
            factory=factory,
            report_record=report_record,
        )
    img_serializer = ImageSerializer(img)
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
    return JsonResponse(img_serializer.data, safe=False)
