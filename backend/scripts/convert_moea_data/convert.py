import os
import string

from os import listdir
from collections import namedtuple

from openpyxl import load_workbook
from sectname import convert_address_to_sectcode

ROOT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(ROOT_DIR, "moea_data")
"""
Columns:
    0. No
    1. 工廠名稱或違章建築 (請寫名稱或貼照片)
    2. 縣市
    3. 地號
    4. 地址
    5. 縣市政府會勘情形
    6. 是否裝設AMI監控
"""


class FactoryData:
    def __init__(self,
                 no,
                 name,
                 city,
                 sectstr,
                 address,
                 status,
                 ami,
                 sect_list=None) -> None:
        self.no = no
        self.name = name
        self.city = city
        self.sectstr = sectstr
        self.address = address
        self.status = status
        self.ami = ami
        self.sect_list = sect_list


class MoeaSheet:
    def __init__(self, name, sheet):
        self.name = name
        self.sheet = sheet
        self._images = {}

        self._load_images()

    def _load_images(self):
        sheet_images = self.sheet._images
        for image in sheet_images:
            row = image.anchor._from.row + 1
            col = string.ascii_uppercase[image.anchor._from.col]
            self._images[f'{col}{row}'] = image._data

    def get_data(self):
        data = []
        for index, row in enumerate(self.sheet, start=1):
            try:
                cell_number = f"B{index}"
                if self._images.get(cell_number):
                    name = self._images[cell_number]
                else:
                    name = row[1].value

                data.append(
                    FactoryData(
                        row[0].value,
                        name,
                        row[2].value,
                        row[3].value,
                        row[4].value,
                        row[5].value,
                        row[6].value,
                        None,
                    ))
            except Exception as e:
                #print(f"Can't parse data {row}")
                continue

        return data


class Moea:
    def __init__(self, file_path):
        self.file_path = file_path
        self.wb = load_workbook(filename=file_path)
        self.sheet_names = self.wb.sheetnames
        self.unknown_sectstr = []

    def get_target_sheets(self):
        sheets = []

        for sheet_name in self.wb.sheetnames:
            if "名單" in sheet_name:
                sheets.append(MoeaSheet(sheet_name, self.wb[sheet_name]))

        return sheets

    def convert_data(self):
        moea_sheets = self.get_target_sheets()

        for sheet in moea_sheets:
            data = sheet.get_data()
            for item in data:
                if item.sectstr is None:
                    continue

                full_list, simple_list = convert_address_to_sectcode(
                    item.sectstr)
                result = list(map(lambda item: str(item), full_list))
                if not result:
                    self.unknown_sectstr.append(item)
                else:
                    item.sect_list = result

        return data


def list_moea_files():
    files = [
        os.path.join(DATA_DIR, f) for f in listdir(DATA_DIR)
        if os.path.isfile(os.path.join(DATA_DIR, f))
    ]

    return list(map(lambda item: Moea(item), files))


if __name__ == "__main__":
    #open_xlsx(os.path.join(ROOT_DIR, "11001.xlsx"))
    moea_files = list_moea_files()
    print("Convert data")
    for item in moea_files:
        data = item.convert_data()
        print(data)
        for item in data:
            print(item.sect_list)
