from api.utils import normalize_townname


def test_normalize_townname():
    assert normalize_townname("台南市善化區") == "臺南市善化區"
    assert normalize_townname("臺北市大安區") == "臺北市大安區"
    assert normalize_townname("高雄市苓雅區") == "高雄市苓雅區"
