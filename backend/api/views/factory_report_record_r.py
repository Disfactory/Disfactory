from rest_framework.decorators import api_view

from django.http import JsonResponse

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import ReportRecord
from ..serializers import ReportRecordSerializer


@swagger_auto_schema(
    method="get",
    operation_summary='取得指定 id 工廠的 Report',
    responses={
        200: openapi.Response('Report 資料', ReportRecordSerializer),
    }
)
@api_view(['GET'])
def get_factory_report(request, factory_id):
    if request.method == "GET":
        report_records = ReportRecord.objects.filter(
            factory__id=factory_id).order_by('created_at')
        serializer = ReportRecordSerializer(report_records, many=True)
        return JsonResponse(serializer.data, safe=False)
