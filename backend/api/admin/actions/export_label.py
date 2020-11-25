from api.utils import set_function_attributes


class ExportLabelMixin:
    @set_function_attributes(short_description="下載標籤及交寄執據")
    def export_labels_as_docx(self, request, queryset):
        return
