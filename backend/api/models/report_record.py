from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

from .mixins import SoftDeleteMixin
from .factory import Factory


class ReportRecord(SoftDeleteMixin):
    """Report records send by users.

    `ReportRecord` will be queried in advanced by admins from
    Citizen of the Earth, Taiwan. They will filter the most recent
    records out every a few weeks to catch the bad guys.
    """

    id = models.AutoField(primary_key=True)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, related_name="report_records")
    user_ip = models.GenericIPAddressField(default="192.168.0.1", blank=True, null=True)
    action_type = models.CharField(max_length=10)  # PUT, POST
    action_body = JSONField()  # request body
    created_at = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(max_length=64, blank=True, null=True)
    contact = models.CharField(max_length=64, blank=True, null=True)
    others = models.CharField(max_length=1024, blank=True)


class RecycledReportRecord(ReportRecord):
    class Meta:
        proxy = True

    objects = ReportRecord.recycle_objects
