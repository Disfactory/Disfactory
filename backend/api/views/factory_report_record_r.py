from rest_framework.decorators import api_view

from django.http import JsonResponse

from ..models import ReportRecord
from ..serializers import ReportRecordSerializer


@api_view(['GET'])
def get_factory_report(request, factory_id):
    if request.method=="GET":
        report_records = ReportRecord.objects.filter(factory__id=factory_id).order_by('created_at')
        serializer = ReportRecordSerializer(report_records, many=True)
        return JsonResponse(serializer.data, safe=False)
