from datetime import datetime, timedelta

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import mark_safe

from api.models import ReportRecord, Image
from api.admin.actions import ExportCsvMixin, RestoreMixin, ExportLabelMixin, ExportDocMixin
from rangefilter.filter import DateRangeFilter


class FactoryWithReportRecords(DateRangeFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = "report_record created_at"

    def queryset(self, request, queryset):
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())

            query_params = super()._make_query_filter(request, validated_data)

            factory_ids = (
                ReportRecord.objects.only("factory_id", "created_at",)
                .filter(**query_params)
                .values("factory_id")
                .distinct()
            )
            factory_ids = [factory_id["factory_id"]
                           for factory_id in factory_ids]
            queryset = queryset.filter(id__in=factory_ids)

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
        county_dict = dict(self.county_mappings)

        if self.value():
            county = county_dict[self.value()]
            re_str = county
            if "臺" in county:
                re_str = county.replace("臺", "(台|臺)")

            queryset = queryset.filter(townname__iregex=re_str)

        return queryset


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

    def get_report_contact(self, obj):
        return obj.report_record.contact

    def get_report_nickname(self, obj):
        return obj.report_record.nickname

    def image_show(self, obj):
        return mark_safe(
            f'<img src="{obj.image_path}" style="max-width:500px; height:auto"/>'
        )

    image_show.short_description = "Image Preview"
    get_report_nickname.short_description = "Nickname"
    get_report_contact.short_description = "Contact"


class FactoryAdmin(admin.ModelAdmin, ExportCsvMixin, ExportLabelMixin, ExportDocMixin):

    list_display = (
        "id",
        "updated_at",
        "townname",
        "sectname",
        "sectcode",
        "landcode",
        "factory_type",
        "source",
        "name",
    )
    search_fields = ["townname", "sectname"]
    list_filter = (
        # XXX: actually not using `factory.created_at` but `repordRecord.created_at`
        ("created_at", FactoryWithReportRecords),
        "cet_report_status",
        "source",
        "factory_type",
        FactoryFilteredByCounty,
    )
    ordering = ["-created_at"]

    actions = ["export_as_csv", "export_labels_as_docx", "export_as_docx"]

    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": (
                # TODO: "factory_number",
                "id",
                ("cet_review_status", "cet_report_status"),
                # TODO: "gov_reply_summary",
                "cet_reviewer",
                # TODO: "cet_staff",
            ),
        }),
        ("Detail", {
            "classes": (),
            "fields": (
                ("townname", "landcode"),
                ("sectname", "sectcode"),
                ("lng", "lat"),
                "factory_type",
                "name",
                ("created_at", "updated_at"),
                # TODO: "cet_doc_number",
            ),
        }),
    )

    inlines = [ImageInlineForFactory, ReportRecordInline]

    def get_name(self, obj):
        return obj.name or "_"


class RecycledFactoryAdmin(admin.ModelAdmin, RestoreMixin):
    list_display = (
        "get_name",
        "deleted_at",
        "id",
    )

    actions = ["restore"]
    ordering = ["-deleted_at"]

    inlines = [ImageInlineForFactory, ReportRecordInline]

    def get_name(self, obj):
        return obj.name or "_"

    get_name.short_description = "name"
