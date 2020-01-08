import requests

import easymap
from .models import Factory, Image



def _upload_image_to_imgur(image_buffer, client_id):
    headers = {'Authorization': f'Client-ID {client_id}'}
    data = {'image': image_buffer}
    resp = requests.post(
        'https://api.imgur.com/3/upload',
        data=data,
        headers=headers,
    )
    path = resp.json()['data']['link']
    return path


def update_landcode(factory_id):
    factory = Factory.objects.get(pk=factory_id)
    land_number = easymap.get_land_number(factory.lng, factory.lat)['landno']
    Factory.objects.filter(pk=factory_id).update(landcode=land_number)


def upload_image(image_buffer, client_id, image_id):
    path = _upload_image_to_imgur(image_buffer, client_id)
    Image.objects.filter(pk=image_id).update(image_path=path)
