from django.contrib import admin

from api.admin.actions import ExportCsvMixin, RestoreMixin


class ReportRecordAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        "factory",
        "action_type",
        "created_at",
        "nickname",
        "contact",
        "others",
        "id",
    )
    raw_id_fields = ("factory",)
    list_filter = ("action_type",)
    ordering = ["-created_at"]
    actions = ["export_as_csv"]


class RecycledReportRecordAdmin(admin.ModelAdmin, RestoreMixin):
    list_display = (
        "deleted_at",
        "factory",
        "action_type",
        "id",
    )
    list_filter = ("action_type",)
    ordering = ["-deleted_at"]
    actions = ["restore"]
