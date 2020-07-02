import csv
import operator
from datetime import datetime
from functools import reduce

from django.db.models import Q
from django.http import HttpResponse

from api.models import GovAgency
from docxtpl import DocxTemplate


def _modify(field_name):
    if field_name == 'get_name':
        return 'name'
    return field_name


class ExportCsvMixin:

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [_modify(field) for field in self.list_display]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = '輸出成 csv 檔'


class RestoreMixin:

    def restore(self, request, queryset):
        queryset.undelete()

    restore.short_description = '復原'


class ExportLabelMixin:
    def export_labels_as_docx(self, request, queryset):
        city_list = []
        for item in queryset:
            city = item.townname[:3]
            city_list.append(city)
        # print(set(city_list))
        sending_list = GovAgency.objects.filter(reduce(operator.or_, (Q(
            agency_name__startswith=x) for x in set(city_list)))).values('agency_name', 'zip_code', 'address')
        print(sending_list)
        self.gen_post_office_files(sending_list)
        self.gen_label_file(sending_list)
        return

    def gen_post_office_files(self, mailing_data: dict):
        doc_main = DocxTemplate("doc_templates/post_office_doc_main.docx")
        doc_copy = DocxTemplate("doc_templates/post_office_doc_copy.docx")
        now = datetime.now()
        context = {
            'year': now.year - 1911,
            'month': now.month,
            'date': now.day,
            'agencies': mailing_data
        }
        doc_main.render(context)
        doc_main.save(f'[{now.strftime("%y%m%d")}]＿大宗交寄＿執據.docx')
        doc_copy.render(context)
        doc_copy.save(f'[{now.strftime("%y%m%d")}]＿大宗交寄＿存根.docx')

    def gen_label_file(self, mailing_data: dict):
        doc = DocxTemplate("doc_templates/mailing_labels.docx")
        now = datetime.now()
        context = {
            'address': mailing_data
        }
        doc.render(context)
        doc.save(f'[{now.strftime("%y%m%d")}]＿發文地址標籤.docx')
        pass

    export_labels_as_docx.short_description = '下載標籤及交寄執據'
