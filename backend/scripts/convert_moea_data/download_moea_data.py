import os
import re
import requests

CURRENT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(CURRENT_DIR, "moea_data")

LIST_PAGE_URL = "https://www.cto.moea.gov.tw/FactoryMCLA/web/information/list.php?cid=1"
DOWNLOAD_URL_TEMPLATE = "https://www.cto.moea.gov.tw/FactoryMCLA/upload/information_upload/{}"

def download_list(list_name_pattern):
    resp = requests.get(LIST_PAGE_URL)
    content = resp.content.decode('utf-8')

    items = set(re.findall(list_name_pattern, content))
    for item in items:
        data_file_path = os.path.join(DATA_DIR, item)
        download_url = DOWNLOAD_URL_TEMPLATE.format(item)
        if os.path.exists(data_file_path):
            continue

        print(f"Downloading {item}...")
        resp = requests.get(download_url)
        os.makedirs(os.path.dirname(data_file_path), exist_ok=True)
        with open(data_file_path, "wb") as fp:
            fp.write(resp.content)

if __name__ == "__main__":
    print(f"Start downloading the list earlier than 11101")
    download_list(r"(1[0-1][0|9]\d\d查處名單\.xlsx)")

    print(f"Start downloading the list later than 11101")
    download_list(r"(\d\d[1-9]\d\d內政部違反土地使用查處名單\.xlsx)")
