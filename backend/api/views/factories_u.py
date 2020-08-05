import logging
import json
from datetime import datetime

from rest_framework.decorators import api_view

from django.db import transaction
from django.http import JsonResponse, HttpResponse

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import Factory, ReportRecord
from ..serializers import FactorySerializer

from .utils import _get_client_ip

from django.core.exceptions import ObjectDoesNotExist

LOGGER = logging.getLogger('django')


def _handle_get_factory_attributes(request, factory_id):
    try:
        factory = Factory.objects.get(pk=factory_id)
        serializer = FactorySerializer(factory)
        return JsonResponse(serializer.data, safe=False)
    except ObjectDoesNotExist:
        return HttpResponse(
            f"Factory id {factory_id} not existed.",
            status=400,
        )


def _handle_update_factory_attributes(request, factory_id):
    client_ip = _get_client_ip(request)
    put_body = request.data
    serializer = FactorySerializer(data=put_body, partial=True)

    if not serializer.is_valid():
        LOGGER.warning(f"{client_ip} : <serializer errors> ")
        return JsonResponse(
            serializer.errors,
            status=400,
        )

    updated_factory_fields = put_body.copy()
    updated_factory_fields.pop("others", None)
    updated_factory_fields.pop("contact", None)

    new_lng = put_body.get("lng")
    new_lat = put_body.get("lat")
    if (new_lat is not None) or (new_lng is not None):
        # factory = Factory.objects.only("lat", "lng").get(pk=factory_id)
        # new_lng = new_lng or factory.lng
        # new_lat = new_lat or factory.lat
        # new_point = Point(new_lng, new_lat, srid=4326)
        # new_point.transform(settings.POSTGIS_SRID)
        # updated_factory_fields["point"] = new_point
        LOGGER.warning(
            f"{client_ip} : <Factory position cannot be modified> ")
        return HttpResponse(
            "Factory position cannot be modified.",
            status=400,
        )

    if "status" in put_body:
        updated_factory_fields["status_time"] = datetime.now()

    new_report_record_fields = {
        "factory_id": factory_id,
        "user_ip": _get_client_ip(request),
        "action_type": "UPDATE",
        "action_body": put_body,
        "contact": put_body.get("contact"),
        "others": put_body.get("others", ""),
    }

    with transaction.atomic():
        Factory.objects.filter(pk=factory_id).update(
            **updated_factory_fields)
        ReportRecord.objects.create(**new_report_record_fields)
        factory = Factory.objects.get(pk=factory_id)

    serializer = FactorySerializer(factory)
    LOGGER.info(f"{client_ip} : <Update factory> {factory_id} {put_body} ")
    return JsonResponse(serializer.data, safe=False)


@swagger_auto_schema(
    method="get",
    operation_summary='取得指定 id 的工廠資料',
    responses={
        200: openapi.Response('工廠資料', FactorySerializer),
        400: "request failed"
    }
)
@swagger_auto_schema(
    method="put",
    operation_summary='更新指定 id 的工廠資料',
    request_body=FactorySerializer,
    responses={
        200: openapi.Response('更新後的工廠資料', FactorySerializer),
        400: "request failed"
    }
)
@api_view(['PUT', 'GET'])
def update_factory_attribute(request, factory_id):
    if request.method == "PUT":
        return _handle_update_factory_attributes(request, factory_id)
    elif request.method == "GET":
        return _handle_get_factory_attributes(request, factory_id)
