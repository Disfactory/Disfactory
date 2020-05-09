from unittest.mock import patch

from django.test import TestCase
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
import requests

from ..utils import _get_nearby_factories


class ViewsUtilsTestCase(TestCase):

    def test_get_nearby_factories_called_db_correctlly(self):
        lat = 25
        lng = 120
        radius = 2.  # km
        pnt = Point(x=lng, y=lat, srid=4326)
        pnt.transform(3857)
        d = D(km=radius)
        # with patch("api.views.utils.Factory.objects.filter") as mock_filter:
        #     _get_nearby_factories(lat, lng, radius=radius)
        #     mock_filter.assert_called_once_with(point__distance_lte=(pnt, d))
