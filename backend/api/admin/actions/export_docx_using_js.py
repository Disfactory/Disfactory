from api.utils import set_function_attributes
from django.template.response import TemplateResponse
from api.models import Image
import json
import requests
import logging

"""
example
{
  sender: 'XXX',
  serialNumber: '00000000',
  location: '台北市中山區中山北路一段',
  legislator: 'XXX',
  townName: '台北市中山區',
  imageUrls: [
    // 'https://i.imgur.com/taKOy2v.png',
    // 'https://i.imgur.com/LrUki4U.jpg',
  ],
},
"""

CET_STAFF_EMAIL = {
    "蔡佳昇": "pisces@cet-taiwan.org",
    "賴沛蓮": "peii@cet-taiwan.org",
}

FIND_TAIWAN_LEGISLATOR_API = "https://ftl.disfactory.tw"
LOGGER = logging.getLogger('django')

def find_taiwan_legislator_name_by_location(lat, lng):
    try:
        resp = requests.get(
            FIND_TAIWAN_LEGISLATOR_API,
            params={"lat": lat, "lng": lng},
        )
        data = resp.json()
        return data[0]['name'] if (data and 'name' in data[0]) else "UNKNOWN"

    except Exception as e:
        LOGGER.error(
            f"Can't get the legislator information from {FIND_TAIWAN_LEGISLATOR_API} - {e}",
        )
        return "UNKNOWN"

class ExportDocUsingJSMixin:
    @set_function_attributes(short_description="輸出成 docx 檔(JS)")
    def export_docx_using_js(self, request, queryset):
        data = []
        for document_model in queryset:
            sender = document_model.cet_staff
            email = CET_STAFF_EMAIL.get(sender, "cet@cet-taiwan.org")

            if document_model.factory.townname:
                townname = document_model.factory.townname.replace('臺灣省', '').replace('台灣省', '')[:3]
            else:
                townname = "UNKNOWN"

            images = Image.objects.only("id").filter(factory=document_model.factory)
            image_urls = [image.image_path for image in images]
            legislator_name = find_taiwan_legislator_name_by_location(
                lat=document_model.factory.lat,
                lng=document_model.factory.lng,
            )


            data.append({
                "sender": sender,
                "email": email,
                "serialNumber": document_model.code,
                "location": f"{document_model.factory.townname}{document_model.factory.sectname} ({document_model.factory.sectcode}) {document_model.factory.landcode}",
                "legislator": legislator_name,
                "townName": townname,
                "imageUrls": image_urls,
            })


        data_json_str = json.dumps(data)
        return TemplateResponse(request, "admin/document/export_docx_using_js.html", {"data": data_json_str})
