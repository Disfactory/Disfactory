from unittest.mock import patch
from django.test import TestCase, Client


class GetNearbyOrCreateFactoriesViewTestCase(TestCase):

    def test_get_nearby_factory_wrong_params(self):
        cli = Client()

        # case 1: missing parameter
        resp = cli.get("/api/factories?lat=23")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, b"Missing query parameter: lng, range.")

        resp = cli.get("/api/factories?lng=121&range=0.2")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, b"Missing query parameter: lat.")

        # case 2: not querying Taiwan
        resp = cli.get("/api/factories?lat=39.9046126&lng=116.3977254&range=1")
        self.assertEqual(resp.status_code, 400)
        self.assertIn(b"The query position is not in the range of Taiwan.", resp.content)

        # case 3: wrong query radius
        resp = cli.get("/api/factories?lat=23&lng=121&range=10000")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, b"`range` should be within 0.01 to 100 km, but got 10000.0")

        resp = cli.get("/api/factories?lat=23&lng=121&range=0.001")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, b"`range` should be within 0.01 to 100 km, but got 0.001")

    def test_get_nearby_factory_called_util_func_correctly(self):
        cli = Client()

        with patch("api.views.factories_cr._get_nearby_factories") as mock_func:
            lat = 23.12
            lng = 121.5566
            r = 0.5
            cli.get(f"/api/factories?lat={lat}&lng={lng}&range={r}")

            mock_func.assert_called_once_with(
                latitude=lat,
                longitude=lng,
                radius=r,
            )

    def test_get_nearby_factory_called_on_test_data(self):
        cli = Client()

        # in sync with api/tests/test_models.py
        lat = 23.234
        lng = 120.1
        r = 1
        resp = cli.get(f"/api/factories?lat={lat}&lng={lng}&range={r}")
        self.assertEqual(resp.status_code, 200)

        factories = resp.json()
        self.assertEqual(len(factories), 9)
        self.assertCountEqual([f["name"] for f in factories], [
            "full-info: row_2",
            "full-info: row_3",
            "full-info: row_8",
            "full-info: row_9",
            "full-info: row_10",
            "full-info: row_11",
            "full-info: row_12",
            "full-info: row_13",
            "full-info: row_22",
        ])
