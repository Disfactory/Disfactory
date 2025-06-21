#!/usr/bin/env python

import requests
import re

DEFAULT_TIMEOUT = 5  # 5 seconds

EASYMAP_BASE_URL = "http://oracle.code-life.info:3000"


class SectLandInfo:

    def __init__(self, sectname, sectcode, landcode):
        self.sectname = sectname
        self.sectcode = sectcode
        self.landcode = landcode


class TownInfo:

    def __init__(self, cityname, townname, towncode):
        self.cityname = cityname
        self.townname = townname
        self.towncode = towncode


def get_town_info(lat, lng):
    url = EASYMAP_BASE_URL + "/api/town"
    params = {"lat": lat, "lng": lng}
    try:
        result = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if result.status_code == 200:
            data = result.json()
            return TownInfo(data.get("cityname"), data.get("townname"),
                            data.get("towncode"))
    except Exception as e:
        print("Error: {}".format(e))
        return TownInfo("", "", "")


def get_sectland_info(lat, lng):
    url = EASYMAP_BASE_URL + "/api/sectland"
    params = {"lat": lat, "lng": lng}
    try:
        result = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if result.status_code != 200:
            return SectLandInfo("", "", "")

        data = result.json()
        if data.get("features") is None or len(data.get("features")) == 0:
            return SectLandInfo("", "", "")

        feature = data.get("features")[0]
        properties = feature.get("properties")
        section = properties.get("section")
        # e.g. section = (0410)鹽埔段
        m = re.match(r"\((\d+)\)(.*)", section)
        if m is None:
            return SectLandInfo("", "", "")

        sectcode = m.group(1)
        sectname = m.group(2)
        landcode = properties.get("land_number")
        return SectLandInfo(sectname, sectcode, landcode)
    except Exception as e:
        print("Error: {}".format(e))
        return SectLandInfo("", "", "")


def get_land_number(lat, lng, timeout=DEFAULT_TIMEOUT):
    town_info = get_town_info(lat, lng)
    sectland_info = get_sectland_info(lat, lng)

    return {
        "landno": sectland_info.landcode,
        "sectno": sectland_info.sectcode,
        "sectname": sectland_info.sectname,
        "townno": town_info.towncode,
        "townname": town_info.cityname + town_info.townname,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: easymap.py lng lat")
        sys.exit(-1)
    lng, lat = sys.argv[1:3]
    print(get_land_number(lat=lat, lng=lng))
