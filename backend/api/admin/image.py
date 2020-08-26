from django.contrib import admin
from api.admin.actions import ExportCsvMixin, RestoreMixin


class ImageAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        'created_at',
        'image_path',
        'orig_time',
        'factory',
        'report_record',
        'id',
    )
    ordering = ['orig_time', '-created_at']
    actions = ["export_as_csv"]


class RecycledImageAdmin(admin.ModelAdmin, RestoreMixin):
    list_display = (
        'deleted_at',
        'image_path',
        'factory',
        'report_record',
        'id',
    )
    actions = ["restore"]
    ordering = ['-deleted_at']
