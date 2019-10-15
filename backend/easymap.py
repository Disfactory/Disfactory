#!/usr/bin/env python

import requests
import re


class WebRequestError(RuntimeError):
    def __init__(self, message, status_code, response_body):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


def get_session():
    easymap_url = "http://easymap.land.moi.gov.tw/P02/Index"
    sess = requests.Session()
    # XXX don't need this?
    # sess.headers.update({"User-Agent": "Mozilla/5.0"})
    sess.get(easymap_url)
    if not "JSESSIONID" in sess.cookies:
        raise RuntimeError("Failed getting session from easymap")
    return sess


def get_point_city(sess, x, y):
    point_city_url = "http://easymap.land.moi.gov.tw/P02/Query_json_getPointCity"
    data = {"wgs84x": x, "wgs84y": y}
    resp = sess.post(point_city_url, data=data)
    if resp.status_code != requests.codes.ok:
        raise WebRequestError("Failed getting city code", resp.status_code, resp.text)
    return resp.json()


def get_token(sess):
    set_token_url = "http://easymap.land.moi.gov.tw/P02/pages/setToken.jsp"
    token_re = re.compile('<input type="hidden" name="(.*?)" value="(.*?)" />')
    resp = sess.post(set_token_url)
    if resp.status_code != requests.codes.ok:
        raise WebRequestError("Failed getting token", resp.status_code, resp.text)
    token = dict([(m.group(1), m.group(2)) for m in token_re.finditer(resp.text)])
    if not "token" in token:
        raise WebRequestError("Failed parsing token", resp.status_code, resp.text)
    return token


def get_door_info(sess, x, y, city, token):
    get_door_info_url = "http://easymap.land.moi.gov.tw/P02/Door_json_getDoorInfoByXY"
    data = {"city": city["cityCode"], "coordX": x, "coordY": y, **token}
    resp = sess.post(get_door_info_url, data=data)
    if resp.status_code != requests.codes.ok:
        raise WebRequestError("Failed getting door info", resp.status_code, resp.text)
    try:
        return resp.json()
    except:
        raise WebRequestError("Failed parsing door info", resp.status_code, resp.text)


def get_land_number(x, y):
    """
    Get land number by WGS84 coordinates.
    """
    sess = get_session()
    city = get_point_city(sess, x=x, y=y)
    token = get_token(sess)
    land_number = get_door_info(sess, x=x, y=y, city=city, token=token)
    return land_number


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: easymap.py <wgs84x> <wgs84y>")
        sys.exit(-1)
    x, y = sys.argv[1:3]
    print(get_land_number(x=x, y=y))
