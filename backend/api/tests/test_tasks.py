from unittest.mock import patch
from tempfile import NamedTemporaryFile

from django.test import TestCase

from ..models import Image
from ..tasks import _upload_image_to_imgur, upload_image


FAKE_IMAGE_URI = "https://ingur.fake/12i34uhoi2"

class MockResponse:
        def __init__(self, json_data):
            self.json_data = json_data

        def json(self):
            return self.json_data


class TasksTestCase(TestCase):

    def test_upload_image_to_imgur(self):
        image_byte_content = b'1234567890'
        mock_imgur_return = MockResponse({
            'data': {
                'link': FAKE_IMAGE_URI,
            }
        })
        fake_client_id = "1234"
        with patch("api.tasks.requests.post", return_value=mock_imgur_return) as mock_post:
            path = _upload_image_to_imgur(image_byte_content, fake_client_id)
            mock_post.assert_called_once_with(
                'https://api.imgur.com/3/upload',
                data={'image': image_byte_content},
                headers={'Authorization': f'Client-ID {fake_client_id}'},
            )
            self.assertEqual(path, mock_imgur_return.json()['data']['link'])

    @patch("api.tasks._upload_image_to_imgur", return_value=FAKE_IMAGE_URI)
    def test_upload_image(self, _):
        img = Image.objects.create(image_path="")
        with NamedTemporaryFile(delete=False) as f:
            upload_image(f.name, 'some_client_id', img.id)

        new_img = Image.objects.get(pk=img.id)
        self.assertEqual(new_img.image_path, FAKE_IMAGE_URI)
