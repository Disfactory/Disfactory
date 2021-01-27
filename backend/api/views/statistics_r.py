from django.http import HttpResponse, JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from ..models import Factory, Document, Image, ReportRecord
from ..models.document import DocumentDisplayStatusEnum


def _generate_factories_query_set(townname, source, display_status):
    # display_status
    if display_status is not None:

        docs = Document.objects\
            .prefetch_related("factory")\
            .order_by("factory__id", "-created_at")\
            .distinct('factory__id')

        display_status_options = map((lambda item: item[1]),DocumentDisplayStatusEnum.CHOICES)
        if display_status == "處理中":
            display_status = [
                DocumentDisplayStatusEnum.INDICES["陳述意見期"],
                DocumentDisplayStatusEnum.INDICES["已排程稽查"],
                DocumentDisplayStatusEnum.INDICES["已勒令停工"],
            ]
            docs = Document.objects.filter(pk__in=docs).filter(display_status__in=display_status)
        else:
            if display_status not in display_status_options:
                display_status_choices = ",".join(display_status_options)
                return HttpResponse(
                    f"display_status: [{display_status_choices}]",
                    status=400
                )
            display_status = DocumentDisplayStatusEnum.INDICES[display_status]
            docs = Document.objects.filter(pk__in=docs).filter(display_status=display_status)

        queryset = Factory.objects.filter(id__in=[obj.factory.id for obj in docs])
    else:
        queryset = Factory.objects


    # townname
    if townname:
        townname = townname.replace("台", "臺")
        queryset = queryset.filter(
            townname__startswith=townname)

    # source
    if source is not None:
        if source not in ["G", "U"]:
            return HttpResponse(
                f"source: ['G' or 'U']",
                status=400
            )

        queryset = queryset.filter(source=source)

    return queryset


@swagger_auto_schema(
    method="get",
    operation_summary="取得某個地區的工廠數量",
    responses={
        200: openapi.Response(
            "工廠數量",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "count": openapi.Schema(type=openapi.TYPE_STRING, description="統計數量"),
                },
            ),
        ),
        400: "request failed"
    },
    manual_parameters=[
        openapi.Parameter(
            name="townname",
            in_=openapi.IN_QUERY,
            description=f"可以只輸入縣市名稱，例如 (臺南市) 或者更詳細一點，例如 (臺南市善化區)，不輸入的話會回傳全台灣的統計",
            type=openapi.TYPE_STRING,
            required=False,
            example="臺南市",
        ),
        openapi.Parameter(
            name="source",
            in_=openapi.IN_QUERY,
            description=f"U or G",
            enum=["U", "G"],
            type=openapi.TYPE_STRING,
            required=False,
            example="u",
        ),
        openapi.Parameter(
            name="display_status",
            in_=openapi.IN_QUERY,
            description="""
            除了 document 預設的 display_status 之外，還有一個 "處理中" 的選項可以用，這個代表
            "已排程稽查", "陳述意見期", "已勒令停工" 這三種 display_status
            """,
            enum=[
                "已檢舉",
                "已排程稽查",
                "陳述意見期",
                "已勒令停工",
                "已發函斷電",
                "已排程拆除",
                "已拆除",
                "不再追蹤",
                "處理中",
            ],
            type=openapi.TYPE_STRING,
            required=False,
            example="u",
        ),
    ]
)
@api_view(["GET"])
def get_factories_count_by_townname(request):
    townname = request.GET.get("townname", None)
    source = request.GET.get("source", None)
    display_status = request.GET.get("display_status", None)

    queryset = _generate_factories_query_set(townname, source, display_status)

    return JsonResponse({
        "count": queryset.count()
    })


@swagger_auto_schema(
    method="get",
    operation_summary="取得某個地區的照片的數量",
    responses={
        200: openapi.Response(
            "照片數量",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "count": openapi.Schema(type=openapi.TYPE_STRING, description="統計數量"),
                },
            ),
        ),
        400: "request failed"
    },
    manual_parameters=[
        openapi.Parameter(
            name="townname",
            in_=openapi.IN_QUERY,
            description=f"可以只輸入縣市名稱，例如 (臺南市) 或者更詳細一點，例如 (臺南市善化區)，不輸入的話會回傳全台灣的統計",
            type=openapi.TYPE_STRING,
            required=False,
            example="臺南市",
        ),
        openapi.Parameter(
            name="source",
            in_=openapi.IN_QUERY,
            description=f"U or G",
            enum=["U", "G"],
            type=openapi.TYPE_STRING,
            required=False,
            example="u",
        ),
        openapi.Parameter(
            name="display_status",
            in_=openapi.IN_QUERY,
            description="""
            除了 document 預設的 display_status 之外，還有一個 "處理中" 的選項可以用，這個代表
            "已排程稽查", "陳述意見期", "已勒令停工" 這三種 display_status
            """,
            enum=[
                "已檢舉",
                "已排程稽查",
                "陳述意見期",
                "已勒令停工",
                "已發函斷電",
                "已排程拆除",
                "已拆除",
                "不再追蹤",
                "處理中",
            ],
            type=openapi.TYPE_STRING,
            required=False,
            example="u",
        ),
    ]
)
@api_view(["GET"])
def get_images_count_by_townname(request):
    townname = request.GET.get("townname", None)
    source = request.GET.get("source", None)
    display_status = request.GET.get("display_status", None)

    factories_queryset = _generate_factories_query_set(townname, source, display_status)
    id_list = factories_queryset.values_list('id', flat=True)
    queryset = Image.objects.prefetch_related('factory').filter(factory__id__in=id_list)

    return JsonResponse({
        "count": queryset.count()
    })

@swagger_auto_schema(
    method="get",
    operation_summary="取得某個地區的回報紀錄數量",
    responses={
        200: openapi.Response(
            "回報紀錄數量",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "count": openapi.Schema(type=openapi.TYPE_STRING, description="統計數量"),
                },
            ),
        ),
        400: "request failed"
    },
    manual_parameters=[
        openapi.Parameter(
            name="townname",
            in_=openapi.IN_QUERY,
            description=f"可以只輸入縣市名稱，例如 (臺南市) 或者更詳細一點，例如 (臺南市善化區)，不輸入的話會回傳全台灣的統計",
            type=openapi.TYPE_STRING,
            required=False,
            example="臺南市",
        ),
        openapi.Parameter(
            name="source",
            in_=openapi.IN_QUERY,
            description=f"U or G",
            enum=["U", "G"],
            type=openapi.TYPE_STRING,
            required=False,
            example="u",
        ),
        openapi.Parameter(
            name="display_status",
            in_=openapi.IN_QUERY,
            description="""
            除了 document 預設的 display_status 之外，還有一個 "處理中" 的選項可以用，這個代表
            "已排程稽查", "陳述意見期", "已勒令停工" 這三種 display_status
            """,
            enum=[
                "已檢舉",
                "已排程稽查",
                "陳述意見期",
                "已勒令停工",
                "已發函斷電",
                "已排程拆除",
                "已拆除",
                "不再追蹤",
                "處理中",
            ],
            type=openapi.TYPE_STRING,
            required=False,
            example="u",
        ),
    ]
)
@api_view(["GET"])
def get_report_records_count_by_townname(request):
    townname = request.GET.get("townname", None)
    source = request.GET.get("source", None)
    display_status = request.GET.get("display_status", None)

    factories_queryset = _generate_factories_query_set(townname, source, display_status)
    id_list = factories_queryset.values_list('id', flat=True)
    queryset = ReportRecord.objects.prefetch_related('factory').filter(factory__id__in=id_list)

    return JsonResponse({
        "count": queryset.count()
    })
