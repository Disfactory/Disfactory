from django.test import TestCase
from django.db.models.functions.math import Radians, Cos, ACos, Sin

from api.models import Factory
from conftest import Unordered


class ModelsTestCase(TestCase):
    def test_migration_seed_data_correctly(self):
        longitude = 120.1
        latitude = 23.234
        radius_km = 1

        distance = 6371 * ACos(
            Cos(Radians(latitude)) * Cos(Radians("lat")) * Cos(Radians("lng") - Radians(longitude))
            + Sin(Radians(latitude)) * Sin(Radians("lat"))
        )

        factories = Factory.objects.annotate(distance=distance).filter(
            distance__lt=radius_km,
        )

        assert (
            list(factories.values_list('name', flat=True))
            == Unordered([
                "既有違章工廠 No.2",
                "既有違章工廠 No.3",
                "既有違章工廠 No.8",
                "既有違章工廠 No.9",
                "既有違章工廠 No.10",
                "既有違章工廠 No.11",
                "既有違章工廠 No.12",
                "既有違章工廠 No.13",
                "既有違章工廠 No.22",
            ])
        )
