import os
import logging
import time

from urllib.parse import urljoin
from api.models.document import Document, FollowUp
from django.db.models import Max

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html

from api.models import ReportRecord, Image
from api.admin.actions import (
    ExportCsvMixin,
    RestoreMixin,
    ExportLabelMixin,
    GenerateDocsMixin,
    MergeFactoriesMixin
)
from api.utils import set_function_attributes
from api.admin.filters.duplicate_sect_land_filter import DuplicateSectLandFilter
from rangefilter.filter import DateRangeFilter
from import_export.admin import ImportExportModelAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe
import easymap

LOGGER = logging.getLogger("django")

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
    fields = ("created_at", "others")
    readonly_fields = ("created_at", "others")
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
        "id",
    )
    readonly_fields = (
        "created_at",
        "nickname",
        "contact",
        "others",
        "action_type",
        "action_body",
        "id",
    )
    extra = 0


class DocumentInline(admin.TabularInline):
    model = Document
    fields = ("code_link", "cet_staff", "display_status", "get_cet_next_tags")
    readonly_fields = ("code_link", "cet_staff", "display_status", "get_cet_next_tags")
    extra = 0

    def code_link(self, obj):
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse("admin:api_document_change", args=(obj.id,)), obj.code
            )
        )

    def get_cet_next_tags(self, obj):
        return ",".join([p.name for p in obj.cet_next_tags.all()])

    def display_status(self, obj):
        return ",".join([p.name for p in obj.display_status_tags.all()])


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


class FactoryAdmin(
    ImportExportModelAdmin,
    ExportCsvMixin,
    ExportLabelMixin,
    GenerateDocsMixin,
    MergeFactoriesMixin,
):
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
    search_fields = ["townname", "sectname", "display_number", "id"]
    list_filter = (
        # XXX: actually not using `factory.created_at` but `repordRecord.created_at`
        ("created_at", FactoryWithReportRecords),
        "cet_review_status",
        "source",
        "factory_type",
        "building_status",
        "usage_status",
        "highlight_category",
        FactoryFilteredByCounty,
        DuplicateSectLandFilter,
    )
    ordering = ["-created_at"]

    actions = [
        "export_as_csv",
        "export_labels_as_docx",
        "generate_docs",
        "merge_factories",
    ]

    readonly_fields = (
        "id",
        "display_number",
        "created_at",
        "updated_at",
        "google_map_link",
        "disfactory_map_link",
        "follow_ups_for_user",
    )
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
                    ("building_status", "usage_status", "highlight_category"),
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
                    "google_map_link",
                    "disfactory_map_link",
                    "factory_type",
                    "name",
                    ("created_at", "updated_at"),
                    # TODO: "cet_doc_number",
                    "follow_ups_for_user",
                ),
            },
        ),
    )

    inlines = [DescriptionInline, ImageInlineForFactory, ReportRecordInline, DocumentInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            reportrecord_latest_created_at=Max("report_records__created_at")
        )
        return queryset

    @set_function_attributes(admin_order_field="reportrecord_latest_created_at")
    def reportrecord_latest_created_at(self, obj):
        return obj.reportrecord_latest_created_at

    @set_function_attributes(short_description="Google Map 連結")
    def google_map_link(self, obj):
        html_template = (
            "<a href='http://www.google.com/maps/place/{lat},{lng}' target='_blank'>Link</a>"
        )

        return format_html(html_template.format(lat=obj.lat, lng=obj.lng))

    @set_function_attributes(short_description="Disfactory Map 連結")
    def disfactory_map_link(self, obj):
        disfactory_frontend_domain = os.environ.get(
            "DISFACTORY_FRONTEND_DOMAIN", "https://disfactory.tw/"
        )

        url = urljoin(disfactory_frontend_domain, f"/#map=16.00/{obj.lng}/{obj.lat}")

        html_template = f"<a href='{url}' target='_blank'>Link</a>"

        return format_html(html_template)

    @set_function_attributes(short_description="Follow ups for user")
    def follow_ups_for_user(self, obj):
        document_id_list = Document.objects.only("id").filter(factory=obj)
        follow_up_query_set = FollowUp.objects.filter(document__in=document_id_list, for_user=True)

        if follow_up_query_set:
            note_list = []
            for follow_up in follow_up_query_set:
                created_at = follow_up.created_at.strftime("%Y-%m-%d %H:%M:%S")
                note_list.append(f"<tr><td>{follow_up.note}</td><td>{created_at}</td><td>{follow_up.document_id}</td></tr>")

            return format_html(f"""
                <table>
                    <tr>
                        <th>Note</th>
                        <th>Created At</th>
                        <th>Document Id</th>
                    </tr>
                    {"".join(note_list)}
                </table>
            """)
        else:
            return ""

    def save_model(self, request, obj, form, change):
        try:
            landinfo = easymap.get_land_number(obj.lng, obj.lat)
            landcode = landinfo.get("landno")

            obj.landcode = landcode
            obj.sectno = landinfo.get("sectno")
            obj.sectname = landinfo.get("sectName")
            obj.towncode = landinfo.get("towncode")
            obj.townname = landinfo.get("townname")
        except Exception as e:
            LOGGER.error("Can't get landcode from easymap")
            LOGGER.error(e)


        super().save_model(request, obj, form, change)


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
