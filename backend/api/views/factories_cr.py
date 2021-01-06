import logging
from typing import List
import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.db import transaction
from django_q.tasks import async_task
from rest_framework.decorators import api_view
from django.db.models import Max

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .utils import _get_nearby_factories, _get_client_ip
from ..models import Factory, Image, ReportRecord
from ..serializers import FactorySerializer

LOGGER = logging.getLogger("django")


def _in_taiwan(lat, lng):
    return (
        settings.TAIWAN_MIN_LATITUDE <= lat <= settings.TAIWAN_MAX_LATITUDE
        and settings.TAIWAN_MIN_LONGITUDE <= lng <= settings.TAIWAN_MAX_LONGITUDE
    )


def _in_reasonable_radius_range(radius):
    # NOTE: need discussion about it
    return 0.01 <= radius <= 100


def _all_image_id_exist(image_ids: List[str]) -> bool:
    images = Image.objects.only("id").filter(id__in=image_ids)
    return len(images) == len(image_ids)


def _handle_get_factories(request):
    try:
        latitude = request.GET["lat"]  # 緯度: y
        longitude = request.GET["lng"]  # 經度: x
        radius = request.GET["range"]  # km
    except MultiValueDictKeyError:
        missing_params = [p for p in ("lat", "lng", "range") if p not in request.GET]
        missing_params = ", ".join(missing_params)
        return HttpResponse(
            f"Missing query parameter: {missing_params}.",
            status=400,
        )

    latitude, longitude = float(latitude), float(longitude)
    if not _in_taiwan(latitude, longitude):
        return HttpResponse(
            "The query position is not in the range of Taiwan."
            "Valid query parameters should be: "
            f"{settings.TAIWAN_MIN_LONGITUDE} < lng < {settings.TAIWAN_MAX_LONGITUDE}, "
            f"{settings.TAIWAN_MIN_LATITUDE} < lat < {settings.TAIWAN_MAX_LATITUDE}.",
            status=400,
        )

    radius = float(radius)
    if not _in_reasonable_radius_range(radius):
        return HttpResponse(
            f"`range` should be within 0.01 to 100 km, but got {radius}",
            status=400,
        )

    nearby_factories = _get_nearby_factories(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
    )

    serializer = FactorySerializer(nearby_factories, many=True)
    return JsonResponse(serializer.data, safe=False)


def _handle_create_factory(request):
    post_body = request.data
    user_ip = _get_client_ip(request)

    LOGGER.debug(f"Received request body: {post_body} to create factory")

    serializer = FactorySerializer(data=post_body)
    if not serializer.is_valid():
        LOGGER.warning(f"{user_ip} : <serializer errors> ")
        return JsonResponse(
            serializer.errors,
            status=400,
        )

    image_ids = post_body.get("images", [])
    if not _all_image_id_exist(image_ids):
        LOGGER.warning(f"{user_ip} : <please check if every image id exist> ")
        return HttpResponse(
            "please check if every image id exist",
            status=400,
        )

    num = Factory.objects.aggregate(Max("display_number"))

    new_factory_field = {
        "name": post_body["name"],
        "lat": post_body["lat"],
        "lng": post_body["lng"],
        "factory_type": post_body.get("type"),
        "status_time": datetime.datetime.now(),
        "display_number": num["display_number__max"] + 1,
    }

    new_report_record_field = {
        "user_ip": user_ip,
        "action_type": "POST",
        "action_body": post_body,
        "nickname": post_body.get("nickname"),
        "contact": post_body.get("contact"),
        "others": post_body.get("others", ""),
    }

    with transaction.atomic():
        new_factory = Factory.objects.create(**new_factory_field)
        report_record = ReportRecord.objects.create(
            factory=new_factory,
            **new_report_record_field,
        )
        Image.objects.filter(id__in=image_ids).update(
            factory=new_factory, report_record=report_record
        )
    serializer = FactorySerializer(new_factory)
    LOGGER.info(
        f"{user_ip}: <Create new factory> at {(post_body['lng'], post_body['lat'])} "
        f"id:{new_factory.id} {new_factory_field['name']} {new_factory_field['factory_type']}",
    )
    async_task("api.tasks.update_landcode", new_factory.id)
    return JsonResponse(serializer.data, safe=False)


@swagger_auto_schema(
    method="get",
    operation_summary="得到中心座標往外指定範圍的已有工廠資料",
    responses={200: openapi.Response("工廠資料", FactorySerializer), 400: "request failed"},
    manual_parameters=[
        openapi.Parameter(
            name="lng",
            in_=openapi.IN_QUERY,
            description=f"{settings.TAIWAN_MIN_LONGITUDE} < lng < {settings.TAIWAN_MAX_LONGITUDE}",
            type=openapi.TYPE_NUMBER,
            required=True,
            example="Custom Example Data",
        ),
        openapi.Parameter(
            name="lat",
            in_=openapi.IN_QUERY,
            description=f"{settings.TAIWAN_MIN_LATITUDE} < lat < {settings.TAIWAN_MAX_LATITUDE}",
            type=openapi.TYPE_NUMBER,
            required=True,
        ),
        openapi.Parameter(
            name="range",
            in_=openapi.IN_QUERY,
            description="km",
            type=openapi.TYPE_NUMBER,
            required=True,
        ),
    ],
)
@swagger_auto_schema(
    method="post",
    operation_summary="新增指定 id 的工廠欄位資料",
    request_body=FactorySerializer,
    responses={200: openapi.Response("新增的工廠資料", FactorySerializer), 400: "request failed"},
    auto_schema=None
)
@api_view(["GET", "POST"])
def get_nearby_or_create_factories(request):
    if request.method == "GET":
        return _handle_get_factories(request)
    elif request.method == "POST":
        return _handle_create_factory(request)
