from django.contrib import admin
from django.utils.html import format_html
from api.models import Document, DocumentDisplayStatusEnum, FollowUp, Image
from api.admin.actions import ExportDocMixin
from api.utils import set_function_attributes
from import_export.admin import ImportExportModelAdmin
from import_export import resources


class FollowUpInline(admin.StackedInline):
    model = FollowUp
    extra = 0
    ordering = ['-created_at']
    exclude = ['deleted_at']
    fields = ['note']

class DocumentResource(resources.ModelResource):
    class Meta:
        model = Document


class DocumentAdmin(ImportExportModelAdmin, ExportDocMixin):
    resource_class = DocumentResource
    class Media:
        js = []
        css = {"all": ["/static/css/document.css"]}

    change_form_template = "admin/document/change_form.html"

    raw_id_fields = ('factory', )

    actions = ["export_as_docx"]

    list_filter = ["cet_next_tags", "display_status"]

    inlines = (FollowUpInline, )

    list_display = (
        "code",
        "cet_staff",
        "display_status",
        "factory_townname",
        "get_cet_next_tags"
    )

    search_fields = ("factory__townname", )

    autocomplete_fields = [
        'cet_report_status_tags',
        'cet_next_tags',
        'gov_response_status_tags',
    ]

    fieldsets = (
        (
            None,
            {
                'fields': ('code', )
            },
        ),
        (
            'Tags',
            {
                'fields': (
                    'display_status',
                    'cet_report_status_tags',
                    'cet_next_tags',
                    'gov_response_status_tags',
                ),
            }
        ),
        (
            'Factory',
            {
                'fields': (
                    "factory_display_number",
                    "factory_townname",
                    "factory_name",

                    ("factory_lat", "factory_lng"),
                    "factory_map_link",
                    "images",
                ),
            },
        ),
    )

    readonly_fields = [
        "factory_townname",
        "factory_name",
        "images",
        "factory_display_number",
        "factory_map_link",
        "factory_lat",
        "factory_lng",
    ]

    @set_function_attributes(short_description="工廠號碼")
    def factory_display_number(self, obj):
        return obj.factory.display_number

    @set_function_attributes(short_description="鄉鎮市")
    def factory_townname(self, obj):
        return obj.factory.townname

    @set_function_attributes(short_description="工廠名稱")
    def factory_name(self, obj):
        return obj.factory.name

    @set_function_attributes(short_description="Google Map 連結")
    def factory_map_link(self, obj):
        html_template = (
            "<a href='http://www.google.com/maps/place/{lat},{lng}' target='_blank'>Link</a>"
        )
        return format_html(html_template.format(lat=obj.factory.lat, lng=obj.factory.lng))

    @set_function_attributes(short_description="Lat")
    def factory_lat(self, obj):
        return obj.factory.lat

    @set_function_attributes(short_description="Lng")
    def factory_lng(self, obj):
        return obj.factory.lng

    @set_function_attributes(allow_tags=True, short_description="工廠照片")
    def images(self, obj):
        images = Image.objects.filter(factory_id=obj.factory.id)
        image_html_template = """
            <div class="imgbox">
                <a href="{image_path}" target='_blank' class="center-fit">
                    <img src={image_path} class="center-fit"/>
                </a>
            </div>
        """

        urls = [
            image_html_template.format(image_path=img.image_path)
            for img in images
        ]
        return format_html("\n".join(urls))

    def get_cet_next_tags(self, obj):
        return ",".join([p.name for p in obj.cet_next_tags.all()])

    def display_status(self, obj):
        return ",".join([p.name for p in obj.display_status_tags.all()])

    def save_formset(self, request, form, formset, change):
        if formset.model == FollowUp:
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.staff:
                    instance.staff = request.user
                instance.save()

            formset.save_m2m()
            return instances
        else:
            return formset.save()

    def save_model(self, request, obj, form, change):
        old_obj = Document.objects.get(id=obj.id)
        if obj.display_status != old_obj.display_status:
            ods, ds = old_obj.display_status, obj.display_status
            FollowUp.objects.create(
                document=obj,
                note=f"{DocumentDisplayStatusEnum.CHOICES[ods][1]} -> "
                     f"{DocumentDisplayStatusEnum.CHOICES[ds][1]}",
            )

        super().save_model(request, obj, form, change)


class CETReportStatusAdmin(ImportExportModelAdmin):
    search_fields = ['name', ]
    list_display = ['id', 'name', 'description']


class CETNextAdmin(ImportExportModelAdmin):
    search_fields = ['name', ]
    list_display = ['id', 'name', 'description']


class GovResponseStatusAdmin(ImportExportModelAdmin):
    search_fields = ['name', ]
    list_display = ['id', 'name', 'description']

class FollowUpAdmin(ImportExportModelAdmin):
    pass
