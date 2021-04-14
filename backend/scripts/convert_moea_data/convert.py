from openpyxl import load_workbook
import string
import os
from collections import namedtuple

from sectname import convert_address_to_sectcode

ROOT_DIR = os.path.dirname(__file__)
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

FactoryData = namedtuple("FactoryData",
                         "no, name, city, sectstr, address, status, ami")


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
                ))

        return data


class Moea:
    def __init__(self, file_path):
        self.file_path = file_path
        self.wb = load_workbook(filename=file_path)
        self.sheet_names = self.wb.sheetnames

    def get_target_sheets(self):
        sheets = []

        for sheet_name in self.wb.sheetnames:
            if "名單" in sheet_name:
                sheets.append(MoeaSheet(sheet_name, self.wb[sheet_name]))

        return sheets


def open_xlsx(file_path):
    moea = Moea(file_path)
    moea_sheets = moea.get_target_sheets()
    for sheet in moea_sheets:
        data = sheet.get_data()
        for item in data[3:]:
            if item.sectstr is None:
                continue

            full_list, simple_list = convert_address_to_sectcode(item.sectstr)
            result = list(map(lambda item: str(item), full_list))
            print(f"{item}{result}")


if __name__ == "__main__":
    open_xlsx(os.path.join(ROOT_DIR, "11001.xlsx"))
