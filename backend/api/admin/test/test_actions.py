from api.models.factory import Factory
from api.models.document import Document
from api.models.image import Image
import datetime

from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import AdminSite
from users.models import CustomUser as User
from django.test import TestCase


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
        "townname": "新北市三峽路中山區",
    },
    {
        "name": "Test Factory 2",
        "factory_type": "2-1",
        "images": [
            "https://i.imgur.com/3XPyVuF.png",
            # python-docx can't parse this image correctly
            # https://github.com/python-openxml/python-docx/issues/187
            "https://i.imgur.com/Q3fplPG.jpg",
            "https://i.imgur.com/eHQ8uWo.jpg",
            "https://i.imgur.com/4AiXzf8.jpg",
            "https://i.imgur.com/Jvh1OQm.jpg",
        ],
        "lat": 23.123,
        "lng": 120.2,
        "landcode": "03750000",
        "status_time": datetime.datetime.now(),
        "display_number": 777,
        "townname": "新北市三峽路中山區",
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
            images = [
                Image.objects.create(image_path=image_path)
                for image_path in data.pop('images', [])
            ]

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
        # Remove all document models
        Document.objects.all().delete()

        # Generate document model for factory
        document_request = {
            'action': 'generate_docs',
            'select_across': 0,
            'index': 0,
            '_selected_action': str(self.factories[0].id)
        }

        print(document_request)
        response = self.client.post('/admin/api/factory/', document_request)
        assert response.status_code == 302, f"status_code of generate_docs action should be 302 but {response.status_code}"

        # Generate docx for document
        document_model_list = Document.objects.all()
        data = {
            'action': 'export_as_docx',
            'select_across': 0,
            'index': 0,
            '_selected_action': document_model_list[0].id
        }

        response = self.client.post('/admin/api/document/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )

    def test_python_docx_workaround(self):
        # Remove all document models
        Document.objects.all().delete()

        # Generate document model for factory
        create_document_request = {
            'action': 'generate_docs',
            'select_across': 0,
            'index': 0,
            '_selected_action': self.factories[1].id
        }
        response = self.client.post('/admin/api/factory/', create_document_request)
        assert response.status_code == 302, f"status_code of generate_docs action should be 302 but {response.status_code}"

        document_model_list = Document.objects.all()
        # python-docx can't parse some jpeg image correctly
        # https://github.com/python-openxml/python-docx/issues/187
        # So we use PIL to format the JPEG file to workaround this.
        data = {
            'action': 'export_as_docx',
            'select_across': 0,
            'index': 0,
            '_selected_action': document_model_list[0].id
        }
        response = self.client.post('/admin/api/document/', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
