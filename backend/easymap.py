#!/usr/bin/env python

import requests
import re

import towninfo

DEFAULT_TIMEOUT = 30 # 5 seconds

EASYMAP_BASE_URL = "https://easymap.land.moi.gov.tw"
PROXIES = {"https": "proxy:5566"}

class WebRequestError(RuntimeError):
    def __init__(self, message, status_code, response_body):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


def get_session(timeout=DEFAULT_TIMEOUT, proxies=PROXIES):
    easymap_url = EASYMAP_BASE_URL + "/Index"
    sess = requests.Session()
    if proxies:
        sess.proxies.update(PROXIES)
    # XXX don't need this?
    sess.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"})
    resp = sess.get(easymap_url, timeout=timeout)
    if "JSESSIONID" not in sess.cookies:
        raise WebRequestError("Failed getting session from easymap", resp.status_code, resp.text)
    return sess


def get_point_city(sess, x, y, timeout=DEFAULT_TIMEOUT):
    point_city_url = EASYMAP_BASE_URL + "/Query_json_getPointCity"
    data = {"wgs84x": x, "wgs84y": y}
    resp = sess.post(point_city_url, data=data, timeout=timeout)
    if resp.status_code != requests.codes.ok:
        raise WebRequestError(f"Failed getting city code status_code:{resp.status_code}, text:{resp.text}")
    try:
        return resp.json()["cityCode"]
    except Exception:
        raise WebRequestError(f"Failed parsing city code text:{resp.text}", resp.text)


def get_token(sess, timeout=DEFAULT_TIMEOUT):
    set_token_url = EASYMAP_BASE_URL + "/pages/setToken.jsp"
    token_re = re.compile('<input type="hidden" name="(.*?)" value="(.*?)" />')
    resp = sess.post(set_token_url, timeout=timeout)
    if resp.status_code != requests.codes.ok:
        raise WebRequestError("Failed getting token", resp.status_code, resp.text)
    token = dict([(m.group(1), m.group(2)) for m in token_re.finditer(resp.text)])
    if "token" not in token:
        raise WebRequestError("Failed parsing token", resp.status_code, resp.text)
    return token


def get_door_info(sess, x, y, cityCode, token, timeout=DEFAULT_TIMEOUT):
    get_door_info_url = EASYMAP_BASE_URL + "/Door_json_getDoorInfoByXY"
    data = {"city": cityCode, "coordX": x, "coordY": y, **token}

    resp = sess.post(get_door_info_url, data=data, timeout=timeout)
    if resp.status_code != requests.codes.ok:
        raise WebRequestError("Failed getting door info", resp.status_code, resp.text)
    try:
        return resp.json()
    except Exception:
        raise WebRequestError("Failed parsing door info", resp.status_code, resp.text)


def get_land_number(x, y, timeout=DEFAULT_TIMEOUT, proxies=PROXIES):
    """
    Get land number by WGS84 coordinates.

    since the easymap API doesn't provide townname, we then insert a townname field by looking up in xml files in ./towncode downloaded from https://api.nlsc.gov.tw/other/ListTown1/{A-Z}
    """
    sess = get_session(timeout=timeout, proxies=proxies)
    cityCode = get_point_city(sess, x=x, y=y, timeout=timeout)
    token = get_token(sess,timeout=timeout)
    land_number = get_door_info(sess, x=x, y=y, cityCode=cityCode, token=token, timeout=timeout)
    sess.close()
    land_number["townname"] = towninfo.code2name.get(land_number["towncode"], "")
    return land_number


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: easymap.py <wgs84x> <wgs84y>")
        sys.exit(-1)
    x, y = sys.argv[1:3]
    print(get_land_number(x=x, y=y, proxies=None))
