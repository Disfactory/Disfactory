from django.db import models

from .mixins import SoftDeleteMixin
from .factory import Factory

from users.models import CustomUser
from .const import DocumentDisplayStatusConst


class DocumentDisplayStatusEnum:

    CHOICES = list(enumerate(DocumentDisplayStatusConst.STATUS_LIST))
    INDICES = {val: idx for idx, val in CHOICES}


class CETReportStatus(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class CETNext(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class GovResponseStatus(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Document(SoftDeleteMixin):

    cet_staff = models.CharField(max_length=100, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    code = models.IntegerField(verbose_name="公文號")
    factory = models.ForeignKey(
        Factory,
        null=True,
        on_delete=models.SET_NULL,
        related_name="documents",
    )
    creator = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="documents",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    display_status = models.IntegerField(
        default=DocumentDisplayStatusEnum.INDICES[DocumentDisplayStatusConst.REPORTED],
        choices=DocumentDisplayStatusEnum.CHOICES,
        db_index=True,
    )

    cet_report_status_tags = models.ManyToManyField(CETReportStatus, blank=True)
    cet_next_tags = models.ManyToManyField(CETNext, blank=True)
    gov_response_status_tags = models.ManyToManyField(GovResponseStatus, blank=True)

class FollowUp(SoftDeleteMixin):
    document = models.ForeignKey(
        Document,
        on_delete=models.PROTECT,
        related_name="follow_ups",
        null=True,
    )

    staff = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="follow_ups",
    )
    note = models.TextField(help_text="此次進度追蹤備註")
    created_at = models.DateTimeField(auto_now_add=True)
    for_user = models.BooleanField(default=False)

    def __unicode__(self):
        return f"#{self.id}"

    def __str__(self):
        staff_name = self.staff.username if self.staff else "UNKNOWN"
        return f"#{self.id} - {staff_name} (created_at:{self.created_at})"

class RecycledDocument(Document):
    class Meta:
        proxy = True

    objects = Document.recycle_objects


class RecycledFollowUp(FollowUp):
    class Meta:
        proxy = True

    objects = FollowUp.recycle_objects
