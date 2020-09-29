from django.contrib import admin
from easy_select2 import select2_modelform
from api.models import Document, FollowUp, Factory, Image
from django.utils.html import format_html
from api.admin.actions import (
    ExportDocMixin
)


DocumentForm = select2_modelform(Document, attrs={'width': '250px'})


class FollowUpInline(admin.StackedInline):
    model = FollowUp
    extra = 0
    ordering = ['-created_at']
    exclude = ['deleted_at']
    fields = ['note']

class DocumentAdmin(
    admin.ModelAdmin,
    ExportDocMixin,
    ):
    class Media:
        js = []
        css = {
            "all": ["/static/css/document.css"]
        }
    change_form_template = "admin/document/change_form.html"

    autocomplete_fields = (
        #'cet_report_status_tags',
        #'cet_next_tags',
        #'gov_response_status_tags',
        #'display_status_tags',
    )
    raw_id_fields = ('factory',)

    actions = [
        "export_as_docx"
    ]

    inlines = (FollowUpInline, )

    list_display = (
        "code",
        "cet_staff",
        #"cet_report_status",
        #"cet_next",
        #"gov_response_status",
        "display_status",
        "factory_townname",
    )
    search_fields = (
        "factory__townname",
    )

    fieldsets = (
        (None, {
            'fields': ('code',)
        }),
        ('Tags', {
            'fields': (
                #'cet_report_status_tags',
                #'cet_next_tags',
                #'gov_response_status_tags',
                'display_status',
            ),
        }),
        ('Factory', {
            'fields': (
                "factory_display_number",
                "factory_townname",
                "factory_name",
                ("factory_lat", "factory_lng"),
                "factory_map_link",
                "images",
            ),
        }),
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

    def factory_display_number(self, obj):
        return obj.factory.display_number
    factory_display_number.short_description = '工廠號碼'

    def factory_townname(self, obj):
        return obj.factory.townname
    factory_townname.short_description = '鄉鎮市'

    def factory_name(self, obj):
        return obj.factory.name
    factory_name.short_description = '工廠名稱'

    def factory_map_link(self, obj):
        return format_html("<a href='http://www.google.com/maps/place/{lat},{lng}' target='_blank'>Link</a>".format(
            lat=obj.factory.lat,
            lng=obj.factory.lng,
        ))
    factory_map_link.short_description = 'Google Map 連結'

    def factory_lat(self, obj):
        return obj.factory.lat
    factory_lat.short_description = "Lat"

    def factory_lng(self, obj):
        return obj.factory.lng
    factory_lng.short_description = "Lng"


    def images(self, obj):
        images = Image.objects.filter(factory_id=obj.factory.id)
        urls = []

        image_html_template = """
            <div class="imgbox">
                <a href="{image_path}" target='_blank' class="center-fit">
                    <img src={image_path} class="center-fit"/>
                </a>
            </div>
        """

        for image in images:
            urls.append(image_html_template.format(image_path=image.image_path))

        return format_html("\n".join(urls))
    images.allow_tags = True
    images.short_description = "工廠照片"

    def cet_report_status(self, obj):
        return ",".join([p.name for p in obj.cet_report_status_tags.all()])

    def cet_next(self, obj):
        return ",".join([p.name for p in obj.cet_next_tags.all()])

    def gov_response_status(self, obj):
        return ",".join([p.name for p in obj.gov_response_status_tags.all()])

    def display_status(self, obj):
        return ",".join([p.name for p in obj.display_status_tags.all()])


    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.staff:
                instance.staff = request.user
            instance.save()

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


class CetReportStatusTagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ['name']


class CetNextTagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ['name']


class GovResponseStatusTagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ['name']


class DisplayStatusTagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ['name']