from unittest.mock import patch
from django.test import TestCase, Client


class PutUpdateFactoryAttribute(TestCase):

    def test_put_update_factory_attribute(self):
        cli = Client()

        # case 1: update lat=1
        resp = cli.get("/api/factories/82850aa4-9413-461f-b30e-ec8c0a3783c8")#?lat=1")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, b"82850aa4-9413-461f-b30e-ec8c0a3783c8")

        # case 2: update lng=2
