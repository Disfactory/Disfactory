from django.test import TestCase
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from api.models import Factory


class ModelsTestCase(TestCase):

    def test_migration_seed_data_correctly(self):
        pnt = Point(x=120.1, y=23.234, srid=4326)
        pnt.transform(3857)
        factories = Factory.objects.filter(point__distance_lte=(pnt, D(km=1)))
        self.assertEqual(set([factory.name for factory in factories]), set([
            "full-info: row_2",
            "full-info: row_3",
            "full-info: row_8",
            "full-info: row_9",
            "full-info: row_10",
            "full-info: row_11",
            "full-info: row_12",
            "full-info: row_13",
            "full-info: row_22",
        ]))
