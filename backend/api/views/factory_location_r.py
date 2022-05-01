from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from ..models import Factory
from ..serializers import FactoryLocationSerializer


@swagger_auto_schema(
    method="get",
    operation_summary="取得工廠位置資訊",
    responses={200: openapi.Response(
        "工廠位置資料", FactoryLocationSerializer), 400: "request failed"},
)
@api_view(["GET"])
def get_factory_location(request, factory_id: str):
    try:
        factory = Factory.objects.get(pk=factory_id)
        serializer = FactoryLocationSerializer(factory)
        return JsonResponse(serializer.data, safe=False)
    except ObjectDoesNotExist:
        return HttpResponse(
            f"Factory id {factory_id} not existed.",
            status=400,
        )
