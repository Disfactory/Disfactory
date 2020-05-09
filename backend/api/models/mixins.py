from django.contrib.gis.db import models
from django.db.models import query
from django.utils import timezone


class SoftDeleteQuerySet(query.QuerySet):
    def delete(self):
        self.update(deleted_at=timezone.now())


class RecycleBinQuerySet(query.QuerySet):
    def undelete(self):
        self.update(deleted_at=None)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(
            self.model,
            using=self._db
        ).filter(deleted_at__isnull=True)


class RecycleBinManager(models.Manager):
    def get_queryset(self):
        return RecycleBinQuerySet(
            self.model,
            using=self._db
        ).filter(deleted_at__isnull=False)


class SoftDeleteMixin(models.Model):
    class Meta:
        abstract = True

    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    raw_objects = models.Manager()
    recycle_objects = RecycleBinManager()

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def undelete(self):
        self.deleted_at = None
        self.save()
