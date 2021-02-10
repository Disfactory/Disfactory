import random

from django.conf import settings
from django.db.models import Prefetch
from django.db.models.functions.math import Radians, Cos, ACos, Sin

from ..models import Factory, ReportRecord, Image, Document


def _sample(objs, k):
    list_of_objs = list(objs)
    random.shuffle(list_of_objs)
    return list_of_objs[:k]


def _get_nearby_factories(latitude, longitude, radius):
    """Return nearby factories based on position and search range."""

    distance = 6371 * ACos(
        Cos(Radians(latitude)) * Cos(Radians("lat")) * Cos(Radians("lng") - Radians(longitude))
        + Sin(Radians(latitude)) * Sin(Radians("lat"))
    )

    ids = Factory.objects.annotate(distance=distance).only("id").filter(distance__lt=radius).order_by("id")

    if len(ids) > settings.MAX_FACTORY_PER_GET:
        ids = _sample(ids, settings.MAX_FACTORY_PER_GET)

    return (
        Factory.objects.filter(id__in=[obj.id for obj in ids])
               .prefetch_related(Prefetch('report_records', queryset=ReportRecord.objects.only("created_at").all()))
               .prefetch_related(Prefetch('images', queryset=Image.objects.only("id").all()))
               .prefetch_related(Prefetch('documents', queryset=Document.objects.only('created_at', 'display_status').all()))
               .all()
    )


def _get_client_ip(request):
    # ref: https://stackoverflow.com/a/30558984
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[-1].strip()
    elif request.META.get("HTTP_X_REAL_IP"):
        return request.META.get("HTTP_X_REAL_IP")
    else:
        return request.META.get("REMOTE_ADDR")
