from django.contrib import admin

from .models import Factory, Image, ReportRecord

# Register your models here.
@admin.register(Factory)
class FactoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'created_at',
        'lat',
        'lng',
        'landcode',
        'id',
    )
    list_filter = (
        'cet_report_status',
        'source',
        'factory_type',
    )
    ordering = ["-created_at"]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'image_path',
        'orig_time',
        'factory',
        'report_record',
        'id',
    )
    ordering = ['orig_time', '-created_at']


@admin.register(ReportRecord)
class ReportRecordAdmin(admin.ModelAdmin):
    list_display = (
        'factory',
        'action_type',
        'created_at',
        'user_ip',
        'nickname',
        'contact',
        'others',
        'id',
    )
    list_filter = (
        'action_type',
    )
    ordering = ["-created_at"]
