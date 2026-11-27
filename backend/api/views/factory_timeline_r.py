from itertools import groupby

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from ..models import Document, Factory, FollowUp, Image, ReportRecord
from ..serializers import FactoryTimelineSerializer

TIMELINE_USER_REPORT_ACTION_TYPES = ("UPDATE", "POST_IMAGE")
STATUS_TRANSITION_SEPARATOR = " -> "


def _to_local_date(dt):
    if timezone.is_aware(dt):
        return timezone.localdate(dt)
    return dt.date()


def _build_image_batches(images):
    sorted_images = sorted(
        images,
        key=lambda img: (_to_local_date(img.created_at), img.created_at, str(img.id)),
    )
    batches = []
    for upload_date, group in groupby(sorted_images, key=lambda img: _to_local_date(img.created_at)):
        batch_images = list(group)
        batches.append(
            {
                "date": upload_date.isoformat(),
                "count": len(batch_images),
                "images": batch_images,
            }
        )
    return batches


@swagger_auto_schema(
    method="get",
    operation_summary="取得指定 id 工廠的時間軸資訊",
    responses={
        200: openapi.Response("工廠時間軸資料", FactoryTimelineSerializer),
        400: "invalid factory id",
        404: "factory not found",
    },
)
@api_view(["GET"])
def get_factory_timeline(request, factory_id: str):
    try:
        factory = (
            Factory.objects.only("id", "display_number")
            .prefetch_related(
                Prefetch(
                    "documents",
                    queryset=Document.objects.only(
                        "id", "factory_id", "created_at", "display_status"
                    )
                    .order_by("created_at", "id")
                    .prefetch_related(
                        Prefetch(
                            "follow_ups",
                            queryset=FollowUp.objects.filter(
                                Q(for_user=True)
                                | Q(for_user=False, note__contains=STATUS_TRANSITION_SEPARATOR)
                            )
                            .only("id", "document_id", "note", "created_at", "for_user")
                            .order_by("created_at", "id"),
                            to_attr="timeline_follow_ups",
                        ),
                    ),
                ),
                Prefetch(
                    "report_records",
                    queryset=ReportRecord.objects.filter(
                        action_type__in=TIMELINE_USER_REPORT_ACTION_TYPES
                    )
                    .only("id", "factory_id", "action_type", "action_body", "created_at", "others")
                    .order_by("created_at", "id"),
                    to_attr="user_report_records",
                ),
                Prefetch(
                    "images",
                    queryset=Image.objects.only("id", "factory_id", "image_path", "created_at")
                    .order_by("created_at", "id"),
                    to_attr="ordered_images",
                ),
            )
            .get(pk=factory_id)
        )
    except (ValidationError, ValueError):
        return HttpResponse(
            f"Invalid factory id: {factory_id}.",
            status=400,
        )
    except ObjectDoesNotExist:
        return HttpResponse(
            f"Factory id {factory_id} does not exist.",
            status=404,
        )

    documents = list(factory.documents.all())
    all_follow_ups = [fu for doc in documents for fu in doc.timeline_follow_ups]
    status_transitions = sorted(
        (
            fu
            for fu in all_follow_ups
            if not fu.for_user and STATUS_TRANSITION_SEPARATOR in fu.note
        ),
        key=lambda fu: (fu.created_at, fu.id),
    )
    follow_ups_for_user = sorted(
        (fu for fu in all_follow_ups if fu.for_user),
        key=lambda fu: (fu.created_at, fu.id),
    )

    payload = {
        "factory_id": factory.id,
        "display_number": factory.display_number,
        "documents": documents,
        "status_transitions": status_transitions,
        "user_reports": factory.user_report_records,
        "follow_ups_for_user": follow_ups_for_user,
        "image_batches": _build_image_batches(factory.ordered_images),
    }
    serializer = FactoryTimelineSerializer(payload)
    return JsonResponse(serializer.data, safe=False)
