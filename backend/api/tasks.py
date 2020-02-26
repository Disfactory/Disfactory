import os
import logging

import requests

import easymap
from .models import Factory, Image

LOGGER = logging.getLogger(__name__)


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
    LOGGER.info(f"Factory {factory_id} retrieved land number {land_number}")
    Factory.objects.filter(pk=factory_id).update(landcode=land_number)


def upload_image(image_path, client_id, image_id):
    with open(image_path, 'rb') as f:
        image_buffer = f.read()
    try:
        path = _upload_image_to_imgur(image_buffer, client_id)
    except Exception:
        LOGGER.warning(f"Upload {image_path} to Imgur failed")
    Image.objects.filter(pk=image_id).update(image_path=path)
    os.remove(image_path)
