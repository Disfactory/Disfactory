from django.db.models import Max

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import mark_safe
from django.contrib.gis.db import models

from api.models import ReportRecord, Image
from api.admin.actions import (
    ExportCsvMixin,
    RestoreMixin,
    ExportLabelMixin,
    GenerateDocsMixin,
)
from api.utils import set_function_attributes
from rangefilter.filter import DateRangeFilter
from mapwidgets.widgets import GooglePointFieldWidget


class FactoryWithReportRecords(DateRangeFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = "report_record created_at"

    def queryset(self, request, queryset):
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            query_params = super()._make_query_filter(request, validated_data)

            queryset = queryset.filter(
                reportrecord_latest_created_at__gte=query_params["created_at__gte"],
                reportrecord_latest_created_at__lte=query_params["created_at__lte"],
            )

        return queryset


class FactoryFilteredByCounty(SimpleListFilter):
    title = "By county"
    parameter_name = "county"
    county_mappings = [
        ("Taipei", "臺北市"),
        ("New_Taipei", "新北市"),
        ("Taoyuan", "桃園市"),
        ("Taichung", "臺中市"),
        ("Tainan", "臺南市"),
        ("Kaohsiung", "高雄市"),
        ("Yilan", "宜蘭縣"),
        ("Hsinchu_County", "新竹縣"),
        ("Hsinchu_City", "新竹市"),
        ("Miaoli", "苗栗縣"),
        ("Changhua", "彰化縣"),
        ("Nantou", "南投縣"),
        ("Yunlin", "雲林縣"),
        ("Chiayi_County", "嘉義縣"),
        ("Chiayi_City", "嘉義市"),
        ("Pingtung", "屏東縣"),
        ("Taitung", "臺東縣"),
        ("Hualien", "花蓮縣"),
        ("Penghu", "澎湖縣"),
        ("Keelung", "基隆市"),
        ("Lienchiang", "連江縣"),
        ("Kinmen", "金門縣"),
    ]

    def lookups(self, _, __):
        return self.county_mappings

    def queryset(self, request, queryset):
        if self.value():
            county_dict = dict(self.county_mappings)
            county = county_dict[self.value()]
            standardized_county = county.replace("臺", "(台|臺)")
            return queryset.filter(townname__iregex=standardized_county)
        else:
            return queryset


class DescriptionInline(admin.TabularInline):
    model = ReportRecord
    verbose_name = "Description"
    verbose_name_plural = "Description"
    can_delete = False
    show_change_link = False
    max_num = 0
    fields = ("created_at", "others", "user_ip")
    readonly_fields = ("created_at", "others", "user_ip")
    extra = 0


class ReportRecordInline(admin.TabularInline):
    model = ReportRecord
    fields = (
        "created_at",
        "nickname",
        "contact",
        "others",
        "action_type",
        "action_body",
        "user_ip",
        "id",
    )
    readonly_fields = (
        "created_at",
        "nickname",
        "contact",
        "others",
        "action_type",
        "action_body",
        "user_ip",
        "id",
    )
    extra = 0


class ImageInlineForFactory(admin.TabularInline):
    model = Image
    fields = (
        "image_show",
        "created_at",
        "get_report_nickname",
        "get_report_contact",
        "id",
        "image_path",
        "report_record",
    )
    readonly_fields = (
        "id",
        "report_record",
        "image_path",
        "image_show",
        "created_at",
        "get_report_nickname",
        "get_report_contact",
    )
    extra = 0

    @set_function_attributes(short_description="Contact")
    def get_report_contact(self, obj):
        return obj.report_record.contact

    @set_function_attributes(short_description="Nickname")
    def get_report_nickname(self, obj):
        return obj.report_record.nickname

    @set_function_attributes(short_description="Image Preview")
    def image_show(self, obj):
        return mark_safe(f'<img src="{obj.image_path}" style="max-width:500px; height:auto"/>')


class FactoryAdmin(admin.ModelAdmin, ExportCsvMixin, ExportLabelMixin, GenerateDocsMixin):

    list_display = (
        "id",
        "display_number",
        "updated_at",
        "reportrecord_latest_created_at",
        "townname",
        "sectname",
        "sectcode",
        "landcode",
        "factory_type",
        "source",
        "name",
    )
    search_fields = ["townname", "sectname", "display_number"]
    list_filter = (
        # XXX: actually not using `factory.created_at` but `repordRecord.created_at`
        ("created_at", FactoryWithReportRecords),
        "cet_report_status",
        "source",
        "factory_type",
        FactoryFilteredByCounty,
    )
    ordering = ["-created_at"]

    actions = [
        "export_as_csv",
        "export_labels_as_docx",
        "generate_docs",
    ]

    formfield_overrides = {models.PointField: {"widget": GooglePointFieldWidget}}

    readonly_fields = ("id", "display_number", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("id", "display_number"),
                    ("cet_review_status", "cet_report_status"),
                    # TODO: "gov_reply_summary",
                    "cet_reviewer",
                    # TODO: "cet_staff",
                ),
            },
        ),
        (
            "DETAIL",
            {
                "classes": (),
                "fields": (
                    ("townname", "landcode"),
                    ("sectname", "sectcode"),
                    ("lng", "lat"),
                    "point",
                    "factory_type",
                    "name",
                    ("created_at", "updated_at"),
                    # TODO: "cet_doc_number",
                ),
            },
        ),
    )

    inlines = [DescriptionInline, ImageInlineForFactory, ReportRecordInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            reportrecord_latest_created_at=Max("report_records__created_at")
        )
        return queryset

    @set_function_attributes(admin_order_field="reportrecord_latest_created_at")
    def reportrecord_latest_created_at(self, obj):
        return obj.reportrecord_latest_created_at


class RecycledFactoryAdmin(admin.ModelAdmin, RestoreMixin):
    list_display = (
        "get_name",
        "deleted_at",
        "id",
    )

    actions = ["restore"]
    ordering = ["-deleted_at"]

    inlines = [ImageInlineForFactory, ReportRecordInline]

    @set_function_attributes(short_description="name")
    def get_name(self, obj):
        return obj.name or "_"
