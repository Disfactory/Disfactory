#!/usr/bin/env python

import requests
import re

def get_session():
    easymap_url = "http://easymap.land.moi.gov.tw/P02/Index"
    sess = requests.Session()
    sess.headers.update({"User-Agent": "Mozilla/5.0"})
    del sess.headers["Accept-Encoding"]
    del sess.headers["Accept"]
    del sess.headers["Connection"]
    sess.get(easymap_url)
    return sess

def get_point_city(sess, x, y):
    point_city_url = "http://easymap.land.moi.gov.tw/P02/Query_json_getPointCity"
    # point_city_url = "http://localhost:1234"
    data = { "wgs84x": x, "wgs84y": y }
    r = sess.post(point_city_url, data=data)
    return r.json()

def get_token(sess):
    set_token_url = "http://easymap.land.moi.gov.tw/P02/pages/setToken.jsp"
    token_re = re.compile('<input type="hidden" name="(.*?)" value="(.*?)" />')
    r = sess.post(set_token_url)
    return dict([
        (m.group(1), m.group(2))
        for m in token_re.finditer(r.text)
        ])

def get_land_number(sess, x, y, city, token):
    get_door_json_url = "http://easymap.land.moi.gov.tw/P02/Door_json_getDoorInfoByXY"
    data = { "city": city["cityCode"], "coordX": x, "coordY": y, **token }
    resp = sess.post(get_door_json_url,
            data=data)
    return resp

def main(x, y):
    sess = get_session()
    city = get_point_city(sess, x=x, y=y)
    token = get_token(sess)
    r = get_land_number(sess, x=x, y=y, city=city, token=token)
    print(r.text)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: easymap.py <wgs84x> <wgs84y>")
        sys.exit(-1)
    x = sys.argv[1]
    y = sys.argv[2]
    main(x=x, y=y)
