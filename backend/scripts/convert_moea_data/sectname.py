import requests
import re
import os
import json
import xml.etree.ElementTree as ET

from string import ascii_uppercase

ROOT_DIR = os.path.dirname(__file__)

COUNTY_CODE_API = "https://api.nlsc.gov.tw/other/ListCounty"
COUNTY_FILE_PATH = os.path.join(ROOT_DIR, "county.json")

TOWN_CODE_API = "https://api.nlsc.gov.tw/other/ListTown/{city}"
TOWN_FILE_PATH = os.path.join(ROOT_DIR, "town.json")

LAND_SECTION_API = "https://api.nlsc.gov.tw/other/ListLandSection/{city}/{town}"
LAND_SECTION_FILE_PATH = os.path.join(ROOT_DIR, "land_section_file.json")

class SectInfo:
    def __init__(self, sectcode, landcode):
        self.sectcode = sectcode
        self.landcode = landcode

    def __str__(self):
        return json.dumps({
            "sectcode": self.sectcode,
            "landcode": self.landcode
        })

class CityTownItem:
    def __init__(self, city_code, city_name, town_code, town_name):
        self.city_code = city_code
        self.city_name = city_name
        self.town_code = town_code
        self.town_name = town_name

    def __str__(self):
        return f"{self.city_code} {self.city_name} {self.town_code} {self.town_name}"

    def to_dict(self):
        return {
            "city_code": self.city_code,
            "city_name": self.city_name,
            "town_code": self.town_code,
            "town_name": self.town_name,
        }


def get_list_county():
    if os.path.exists(COUNTY_FILE_PATH):
        with open(COUNTY_FILE_PATH, "r") as fp:
            return json.loads(fp.read())

    resp = requests.get(COUNTY_CODE_API)
    root = ET.fromstring(resp.text)

    result = {}
    for countyItem in root:
        countyJson = {}
        for item in countyItem:
            countyJson[item.tag] = item.text

        result[countyJson["countycode"]] = countyJson["countyname"]

    with open(COUNTY_FILE_PATH, "w") as fp:
        fp.write(json.dumps(result))

    return result


def get_list_town():
    if os.path.exists(TOWN_FILE_PATH):
        with open(TOWN_FILE_PATH, "r") as fp:
            return json.loads(fp.read())

    county_list = get_list_county()

    result = {}
    for code, name in county_list.items():
        url = TOWN_CODE_API.format(city=code)
        resp = requests.get(url)

        root = ET.fromstring(resp.text)
        for townItem in root:
            townJson = {}
            for item in townItem:
                townJson[item.tag] = item.text

            result[townJson["towncode"]] = townJson["townname"]

    with open(TOWN_FILE_PATH, "w") as fp:
        fp.write(json.dumps(result))

    return result


def get_city_town_data():
    cities = get_list_county()
    towns = get_list_town()

    data_list = []
    for town_code, town_name in towns.items():
        city_code = town_code[:1]
        city_name = cities[city_code]
        data_list.append(
            CityTownItem(city_code, city_name, town_code, town_name))

    return data_list


def get_list_land_section():
    if os.path.exists(LAND_SECTION_FILE_PATH):
        with open(LAND_SECTION_FILE_PATH, "r") as fp:
            return json.loads(fp.read())

    data_list = get_city_town_data()

    result = []
    for item in data_list:
        url = LAND_SECTION_API.format(city=item.city_code, town=item.town_code)
        print(f"Requesting {item.town_name}({item.town_code}) - {url}")
        resp = requests.get(url)
        root = ET.fromstring(resp.text)

        for sectItem in root:
            sectJson = {}
            for sectField in sectItem:
                sectJson[sectField.tag] = sectField.text

            sectJson.update(item.to_dict())
            result.append(sectJson)

    with open(LAND_SECTION_FILE_PATH, "w") as fp:
        fp.write(json.dumps(result))

    return result

def update_metadata():
    """
        Get county, town and land code number from moea open data
    """
    get_list_county()
    get_list_county()
    get_list_land_section()


def search_by_address(address):
    data = get_list_land_section()

    result = []
    for item in data:
        if item['sectstr'] in address and item['town_name'] in address:
            result.append(item)

    return result


def get_numbers(address):
    rx = re.compile(r'([\d-]+)')
    numbers = rx.findall(address)

    return numbers


def format_number(number):
    return "{:04d}".format(int(number))


def format_landcode_to_full(simple_code):
    if len(simple_code) == 8:
        return simple_code

    tokens = simple_code.split("-")
    if len(tokens) == 1:
        tokens.append("0")

    return f"{format_number(tokens[0])}{format_number(tokens[1])}"


def format_landcode_to_simple(full_code):
    if "-" in full_code:
        return full_code

    code = full_code[:4]
    subcode = full_code[4:]

    if not subcode:
        return str(int(code))
    else:
        return f"{int(code)}-{int(subcode)}"


def convert_address_to_sectcode(address):
    address = address.replace("號之", "-")

    sect_data_list = search_by_address(address)
    sect_code_list = list(
        map(lambda sect_data: sect_data['sectcode'], sect_data_list))

    numbers = get_numbers(address)

    full_landcode_list = list(
        map(lambda number: format_landcode_to_full(number), numbers))
    simple_landcode_list = list(
        map(lambda number: format_landcode_to_simple(number), numbers))

    full_list = []
    simple_list = []
    for sectcode in sect_code_list:
        for landcode in full_landcode_list:
            full_list.append(SectInfo(sectcode, landcode))

        for landcode in simple_landcode_list:
            simple_list.append(SectInfo(sectcode, landcode))

    return full_list, simple_list


if __name__ == "__main__":
    address = "新莊區海山頭段石龜小段82號之18"
    print(address)
    print(search_by_address(address))

    full_list, simple_list = convert_address_to_sectcode(address)
    for item in full_list:
        print(item)

    for item in simple_list:
        print(item)
