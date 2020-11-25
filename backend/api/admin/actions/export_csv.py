import csv
from django.http import HttpResponse

from api.utils import set_function_attributes


class ExportCsvMixin:
    @set_function_attributes(short_description="輸出成 csv 檔")
    def export_as_csv(self, request, queryset):
        meta = self.model._meta

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={meta}.csv"
        response.write("\ufeff".encode("utf8"))
        writer = csv.writer(response)

        field_names = [field.name for field in meta.fields]
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response
