from django.db import models

from .mixins import SoftDeleteMixin
from .factory import Factory

from users.models import CustomUser


class Review(SoftDeleteMixin):

    reviewer = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviews",
    )
    factory = models.ForeignKey(
        Factory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviews",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(help_text="")
