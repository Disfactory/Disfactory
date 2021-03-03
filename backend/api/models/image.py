import uuid

from django.db import models

from .mixins import SoftDeleteMixin
from .factory import Factory
from .report_record import ReportRecord


class Image(SoftDeleteMixin):
    """Images of factories that are uploaded by user."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    factory = models.ForeignKey(
        Factory,
        on_delete=models.CASCADE,
        related_name="images",
        blank=True,
        null=True,
    )
    report_record = models.ForeignKey(
        ReportRecord,
        on_delete=models.CASCADE,
        related_name="images",
        blank=True,
        null=True,
    )
    image_path = models.URLField(max_length=256)  # get from Imgur
    created_at = models.DateTimeField(auto_now_add=True)
    # the DB saving time

    orig_time = models.DateTimeField(blank=True, null=True)
    orig_lat = models.FloatField(blank=True, null=True)
    orig_lng = models.FloatField(blank=True, null=True)
    # the actual photo taken time


class RecycledImage(Image):
    class Meta:
        proxy = True

    objects = Image.recycle_objects
