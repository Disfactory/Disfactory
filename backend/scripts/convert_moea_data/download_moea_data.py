import os
import re
import requests

CURRENT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(CURRENT_DIR, "moea_data")

LIST_PAGE_URL = "https://www.cto.moea.gov.tw/FactoryMCLA/web/information/list.php?cid=1"
LIST_NAME_PATTERN = r"([\d]+查處名單\.xlsx)"
DOWNLOAD_URL_TEMPLATE = "https://www.cto.moea.gov.tw/FactoryMCLA/upload/information_upload/{}"

def download_list():
    resp = requests.get(LIST_PAGE_URL)
    content = resp.content.decode('utf-8')

    items = set(re.findall(LIST_NAME_PATTERN, content))
    for item in items:
        data_file_path = os.path.join(DATA_DIR, item)
        download_url = DOWNLOAD_URL_TEMPLATE.format(item)
        if os.path.exists(data_file_path):
            continue

        print(f"Downloading {item}...")
        resp = requests.get(download_url)
        with open(data_file_path, "wb") as fp:
            fp.write(resp.content)

if __name__ == "__main__":
    download_list()

