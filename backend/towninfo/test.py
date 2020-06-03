from unittest import TestCase

from . import code2name


class TownInfoTestCase(TestCase):

    def test_code2name(self):
        self.assertEqual(code2name['64000006'], '高雄市兵役局')
        self.assertEqual(code2name['10017006'], '臺灣省基隆市民政處')
        self.assertEqual(code2name['10017010'], '臺灣省基隆市中正區')
        self.assertEqual(code2name['C01'], '臺灣省基隆市中正區')
