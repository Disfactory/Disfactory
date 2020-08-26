from django.db import models

from .mixins import SoftDeleteMixin
from .factory import Factory

from users.models import CustomUser


class Document(SoftDeleteMixin):

    cet_staff = models.CharField(max_length=100, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=100, help_text='公文號')
    factory = models.ForeignKey(
        Factory,
        on_delete=models.PROTECT,
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



class FollowUp(SoftDeleteMixin):

    document = models.ForeignKey(
        Factory,
        on_delete=models.PROTECT,
        related_name="follow_ups",
    )
    staff = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="follow_ups",
    )
    note = models.TextField(help_text='此次進度追蹤備註')
    created_at = models.DateTimeField(auto_now_add=True)


class RecycledDocument(Document):

    class Meta:
        proxy = True

    objects = Document.recycle_objects


class RecycledFollowUp(FollowUp):

    class Meta:
        proxy = True

    objects = FollowUp.recycle_objects
