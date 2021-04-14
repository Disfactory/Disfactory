from .. import code2name

from conftest import SuperSet


def test_code2name():
    assert code2name == SuperSet({
        "10013270": "臺灣省屏東縣霧臺鄉",
        "67000250": "臺南市南化區",
        "10017010": "臺灣省基隆市中正區",
        "C01": "臺灣省基隆市中正區",
    })
