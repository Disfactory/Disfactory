import csv
import json
import operator
from datetime import datetime
from functools import reduce
from io import BytesIO

import requests
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse

from api.models import Factory, GovAgency
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

    def gen_mailing_lists(self, factories: Factory):
        city_list, locations, location_list = [], [], []
        for item in factories:
            city = item.townname[:3]
            location = (('lng', item.lng), ('lat', item.lat))
            city_list.append(city)
            locations.append(location)
        for row in set(locations):
            location_list.append(dict((lng, lat) for lng, lat in row))
        sending_list = list(GovAgency.objects.filter(reduce(operator.or_, (Q(
            agency_name__startswith=x) for x in set(city_list)))).values('agency_name', 'zip_code', 'address'))
        print(f'request sent at {datetime.now()}')
        resp = requests.post(settings.TW_LEGISLATOR_API, json=location_list)
        print(f'response got at {datetime.now()}')
        legistors = []
        for row in json.loads(resp.text):
            for item in row:
                name = item['name']
                addr = item['通訊處']['國會研究室']
                legistors.append((name, addr))
        for name, addr in set(legistors):
            sending_list.append({
                'agency_name': f'立法委員{name}國會辦公室',
                'zip_code': addr[:4],
                'address': addr[5:]
            })
        return sending_list

    def export_labels_as_docx(self, request, queryset):
        sending_list = self.gen_mailing_lists(queryset)
        response = self.gen_post_office_files(sending_list)
        self.gen_label_file(sending_list)
        # return response

    def gen_post_office_files(self, mailing_data: dict):
        doc_main = DocxTemplate("doc_templates/post_office_doc_main.docx")
        doc_copy = DocxTemplate("doc_templates/post_office_doc_copy.docx")
        now = datetime.now()
        context = {
            'year': now.year - 1911,
            'month': now.month,
            'date': now.day,
            'data_len': len(mailing_data),
            'agencies': mailing_data
        }
        # doc_main.render(context)
        # doc_main.save(f'[{now.strftime("%Y%m%d")}]＿大宗交寄＿執據.docx')
        doc_copy.render(context)
        doc_io = BytesIO()
        # doc_copy.save(f'[{now.strftime("%Y%m%d")}]＿大宗交寄＿存根.docx')
        # doc_main.save(response)
        # doc_copy.render(context)
        doc_copy.save(doc_io)
        doc_io.seek(0)
        response = HttpResponse(doc_io.getvalue())
        response['content_type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        response['Content-Disposition'] = f'attachment; filename=[{now.strftime("%Y%m%d")}]＿大宗交寄＿存根.docx'
        response['Content-Length'] = doc_io.tell()
        # print(doc_io.read())
        return response

    def gen_label_file(self, mailing_data: dict):
        doc = DocxTemplate("doc_templates/mailing_labels.docx")
        now = datetime.now()
        context = {
            'agencies': mailing_data
        }
        # print(context['agencies'])
        # for agency in context['agencies'][::3]:
        #     print(agency)
        doc.render(context)
        doc.save(f'[{now.strftime("%Y%m%d")}]＿發文地址標籤.docx')

    export_labels_as_docx.short_description = '下載標籤及交寄執據'
