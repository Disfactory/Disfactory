from io import BytesIO

from unittest.mock import patch

from django.test import TestCase
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from ..utils import _get_nearby_factories, _upload_image

import requests


class MockResponse:
        def __init__(self, json_data):
            self.json_data = json_data

        def json(self):
            return self.json_data


class ViewsUtilsTestCase(TestCase):

    def test_get_nearby_factories_called_db_correctlly(self):
        lat = 25
        lng = 120
        radius = 2.  # km
        pnt = Point(x=lng, y=lat, srid=4326)
        pnt.transform(3857)
        d = D(km=radius)
        with patch("api.views.utils.Factory.objects.filter") as mock_filter:
            _get_nearby_factories(lat, lng, radius=radius)
            mock_filter.assert_called_once_with(point__distance_lte=(pnt, d))

    def test_upload_image(self):
        image_byte_content = b'1234567890'
        fake_image_file_handler = BytesIO(image_byte_content)
        mock_imgur_return = MockResponse({
            'data': {
                'link': 'https://ingur.fake/12i34uhoi2',
            }
        })
        fake_client_id = "1234"
        with patch("api.views.utils.requests.post", return_value=mock_imgur_return) as mock_post:
            path = _upload_image(fake_image_file_handler, fake_client_id)
            mock_post.assert_called_once_with(
                'https://api.imgur.com/3/upload',
                data={'image': image_byte_content},
                headers={'Authorization': f'Client-ID {fake_client_id}'},
            )
            self.assertEqual(path, mock_imgur_return.json()['data']['link'])
