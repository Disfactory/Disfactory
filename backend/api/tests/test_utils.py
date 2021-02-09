from django.test import TestCase

from api.utils import normalize_townname


class UtilsTestCase(TestCase):

    def test_normalize_townname(self):
        assert normalize_townname("台南市善化區") == "臺南市善化區"
        assert normalize_townname("臺北市大安區") == "臺北市大安區"
        assert normalize_townname("高雄市苓雅區") == "高雄市苓雅區"
