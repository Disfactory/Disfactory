import csv
import json
import operator
from datetime import datetime
from functools import reduce
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

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
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(
            meta)
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
    now = datetime.now()

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
        return self.gen_files(sending_list)

    def gen_files(self, mailing_data: dict):
        files = [{
            'template': DocxTemplate("doc_templates/post_office_doc_main.docx"),
            'name': f'[{self.now.strftime("%Y%m%d")}]＿大宗交寄＿執據.docx'
        }, {
            'template': DocxTemplate("doc_templates/post_office_doc_copy.docx"),
            'name': f'[{self.now.strftime("%Y%m%d")}]＿大宗交寄＿存根.docx'
        }, {
            'template': DocxTemplate("doc_templates/mailing_labels.docx"),
            'name': f'[{self.now.strftime("%Y%m%d")}]＿發文地址標籤.docx'
        }]

        content = {
            'year': self.now.year - 1911,
            'month': self.now.month,
            'date': self.now.day,
            'data_len': len(mailing_data),
            'agencies': mailing_data
        }

        io = BytesIO()
        with ZipFile(io, 'w') as zip_obj:
            for file in files:
                file['template'].render(content)
                file['template'].save(io)
                zip_obj.writestr(file['name'], io.getvalue())
        io.seek(0)
        filename = '標籤及交寄執據'
        response = HttpResponse(io.getvalue())
        response['Content-Type'] = 'application/zip'
        response['Content-Disposition'] = f"attachment; filename={filename.encode('utf-8').decode('ISO-8859-1')}"
        return response

    export_labels_as_docx.short_description = '下載標籤及交寄執據'
