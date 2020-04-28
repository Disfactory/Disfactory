import csv
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import mark_safe

from .models import Factory, Image, ReportRecord


class FactoryWithReportRecords(SimpleListFilter):
    title = '有舉報紀錄'
    parameter_name = 'has_report_record_within'

    def lookups(self, request, model_admin):
        return (
            ('all', '不限'),
            ('7d', '最近一週'),
            ('30d', '最近一個月'),
        )

    def queryset(self, request, queryset):
        now = datetime.now()
        if self.value() == 'all':
            factory_ids = ReportRecord.objects.only('factory_id').values('factory_id').distinct()
            factory_ids = [factory_id['factory_id'] for factory_id in factory_ids]
            queryset = queryset.filter(id__in=factory_ids)
        elif self.value() == '7d':
            factory_ids = ReportRecord.objects.only(
                'factory_id',
                'created_at',
            ).filter(created_at__range=[now - timedelta(days=7), now]).values('factory_id').distinct()
            factory_ids = [factory_id['factory_id'] for factory_id in factory_ids]
            queryset = queryset.filter(id__in=factory_ids)
        elif self.value() == '30d':
            factory_ids = ReportRecord.objects.only(
                'factory_id',
                'created_at',
            ).filter(created_at__range=[now - timedelta(days=30), now]).values('factory_id').distinct()
            factory_ids = [factory_id['factory_id'] for factory_id in factory_ids]
            queryset = queryset.filter(id__in=factory_ids)
        return queryset


class ExportCsvMixin:

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field for field in self.list_display]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = '輸出成 csv 檔'


class ReportRecordInline(admin.TabularInline):
    model = ReportRecord
    fields = (
        'created_at',
        'nickname',
        'contact',
        'others',
        'action_type',
        'action_body',
        'user_ip',
        'id',
    )
    readonly_fields = (
        'created_at',
        'nickname',
        'contact',
        'others',
        'action_type',
        'action_body',
        'user_ip',
        'id',
    )
    extra = 0


class ImageInlineForFactory(admin.TabularInline):
    model = Image
    fields = (
        'image_show',
        'created_at',
        'get_report_nickname',
        'get_report_contact',
        'id',
        'image_path',
        'report_record',
    )
    readonly_fields = (
        'id',
        'report_record',
        'image_path',
        'image_show',
        'created_at',
        'get_report_nickname',
        'get_report_contact',
    )
    extra = 0

    def get_report_contact(self, obj):
        return obj.report_record.contact

    def get_report_nickname(self, obj):
        return obj.report_record.nickname

    def image_show(self, obj):
        return mark_safe(f'<img src="{obj.image_path}" style="max-width:500px; height:auto"/>')

    image_show.short_description = 'Image Preview'
    get_report_nickname.short_description = 'Nickname'
    get_report_contact.short_description = 'Contact'


# Register your models here.
@admin.register(Factory)
class FactoryAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        'name',
        'created_at',
        'lat',
        'lng',
        'landcode',
        'sectcode',
        'sectname',
        'towncode',
        'townname',
        'id',
    )
    list_filter = (
        'cet_report_status',
        'source',
        'factory_type',
        FactoryWithReportRecords,
    )
    ordering = ["-created_at"]
    actions = ["export_as_csv"]

    inlines = [ImageInlineForFactory, ReportRecordInline]


@admin.register(Image)
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


@admin.register(ReportRecord)
class ReportRecordAdmin(admin.ModelAdmin, ExportCsvMixin):
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
    actions = ["export_as_csv"]
