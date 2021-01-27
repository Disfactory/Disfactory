from django.test import TestCase
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from api.models import Factory
from api.models


class ModelsTestCase(TestCase):
    def test_migration_seed_data_correctly(self):
        pnt = Point(x=120.1, y=23.234, srid=4326)
        pnt.transform(3857)
        factories = Factory.objects.filter(point__distance_lte=(pnt, D(km=1)))
        self.assertEqual(
            set([factory.name for factory in factories]),
            set(
                [
                    "既有違章工廠 No.2",
                    "既有違章工廠 No.3",
                    "既有違章工廠 No.8",
                    "既有違章工廠 No.9",
                    "既有違章工廠 No.10",
                    "既有違章工廠 No.11",
                    "既有違章工廠 No.12",
                    "既有違章工廠 No.13",
                    "既有違章工廠 No.22",
                ]
            ),
        )

    def test_get_nearby_factories(self):

        pass
