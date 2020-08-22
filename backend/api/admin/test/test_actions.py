from api.models.factory import Factory
from api.models.image import Image
import datetime

from django import forms
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.admin.options import (
    HORIZONTAL,
    VERTICAL,
    ModelAdmin,
    TabularInline,
    get_content_type_for_model,
)
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.widgets import (
    AdminDateWidget,
    AdminRadioSelect,
    AutocompleteSelect,
    AutocompleteSelectMultiple,
)
from users.models import CustomUser as User
from django.db import models
from django.forms.widgets import Select
from django.test import SimpleTestCase, TestCase
from django.test.utils import isolate_apps

from django.urls import NoReverseMatch, resolve, reverse


class MockRequest:
    pass


class MockSuperUser:
    def has_perm(self, perm):
        return True


request = MockRequest()
request.user = MockSuperUser()

TEST_FACTORY_DATA = [
    {
        "name": "Test Factory 1",
        "factory_type": "2-3",
        "images": [
            "https://i.imgur.com/CSdR281.png",
            "https://i.imgur.com/aT5082y.png",
        ],
        "lat": 23.234,
        "lng": 120.1,
        "landcode": "03750000",
        "status_time": datetime.datetime.now(),
        "display_number": 666,
    }, {
        "name": "Test Factory 2",
        "factory_type": "2-1",
        "images": [
            "https://i.imgur.com/3XPyVuF.png",
            "https://i.imgur.com/eHQ8uWo.jpg",
        ],
        "lat": 23.123,
        "lng": 120.2,
        "landcode": "03750000",
        "status_time": datetime.datetime.now(),
        "display_number": 777,
    }
]


class ModelAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username='super', password='secret', email='super@example.com'
        )

        factories = []

        for data in TEST_FACTORY_DATA:
            # Insert images
            image_path_list = data.get('images', [])
            images = []
            for image_path in image_path_list:
                image = Image.objects.create(image_path=image_path)
                images.append(image)
            del data['images']

            # Create factory
            factory = Factory.objects.create(**data)
            factories.append(factory)

            # Update images
            for image in images:
                image.factory = factory
                image.save()

        cls.factories = factories

    def setUp(self):
        self.site = AdminSite()
        self.client.force_login(self.superuser)

    def test_modeladmin_str(self):
        ma = ModelAdmin(Factory, self.site)
        self.assertEqual(str(ma), 'api.ModelAdmin')

    def test_export_doc_action(self):
        data = {
            'action': 'export_as_docx',
            'select_across': 0,
            'index': 0,
            '_selected_action': self.factories[0].id
        }
        response = self.client.post('/admin/api/factory/', data)

        assert response.status_code == 200, f"status_code should be 200 but {response.status_code}"
        assert response[
            'Content-Type'
        ] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
