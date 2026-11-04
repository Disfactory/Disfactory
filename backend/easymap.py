#!/usr/bin/env python

import json
import requests

DEFAULT_TIMEOUT = 30  # 5 seconds

EASYMAP_BASE_URL = "https://easymap.code-life.info"


def get_land_number(lat, lng, timeout=DEFAULT_TIMEOUT, proxies=None):
    url = EASYMAP_BASE_URL + "/api/query/by-coord-db"
    params = {"lat": lat, "lng": lng}
    try:
        result = requests.get(url, params=params, timeout=timeout, proxies=proxies)
        if result.status_code != 200:
            return {
                "landno": "",
                "sectno": "",
                "sectname": "",
                "towncode": "",
                "townname": "",
            }

        data = result.json()
        if data is None:
            return {
                "landno": "",
                "sectno": "",
                "sectname": "",
                "towncode": "",
                "townname": "",
            }

        return {
            "landno": data.get("land_number", ""),
            "sectno": data.get("section_id", ""),
            "sectname": data.get("section_name", ""),
            "towncode": data.get("town_code", ""),
            "townname": data.get("city_name", "") + data.get("town_name", ""),
        }
    except Exception as e:
        print("Error: {}".format(e))
        return {
            "landno": "",
            "sectno": "",
            "sectname": "",
            "towncode": "",
            "townname": "",
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: easymap.py lng lat")
        sys.exit(-1)
    lng, lat = sys.argv[1:3]
    print(json.dumps(get_land_number(lat=lat, lng=lng), ensure_ascii=False))
