from . import code2name

from conftest import SuperSet


def test_code2name(self):
    assert code2name == SuperSet({
        "64000006": "高雄市兵役局",
        "10017006": "臺灣省基隆市民政處",
        "10017010": "臺灣省基隆市中正區",
        "C01": "臺灣省基隆市中正區",
    })
