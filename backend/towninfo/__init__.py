import pathlib
import xml.etree.ElementTree as ET

city_name = {
    'A': '臺北市',
    'B': '臺中市',
    'C': '臺灣省基隆市',
    'D': '臺南市',
    'E': '高雄市',
    'F': '新北市',
    'G': '臺灣省宜蘭縣',
    'H': '桃園市',
    'I': '臺灣省嘉義市',
    'J': '臺灣省新竹縣',
    'K': '臺灣省苗栗縣',
    'M': '臺灣省南投縣',
    'N': '臺灣省彰化縣',
    'O': '臺灣省新竹市',
    'P': '臺灣省雲林縣',
    'Q': '臺灣省嘉義縣',
    'T': '臺灣省屏東縣',
    'U': '臺灣省花蓮縣',
    'V': '臺灣省臺東縣',
    'W': '福建省金門縣',
    'X': '臺灣省澎湖縣',
    'Z': '福建省連江縣',
}

HERE = pathlib.Path(__file__).parent
code2name = {}
name2code = {}

for xml_path in HERE.glob("*.xml"):
    with xml_path.open("r") as f:
        tree = ET.fromstring(f.read())
        if tree is not None:
            for child in tree.getchildren():
                code = child.find("towncode").text
                code01 = child.find("towncode01").text
                name = city_name[code01[:1]] + child.find("townname").text
                code2name[code] = name
                name2code[name] = code

                code01_node = child.find("towncode01")
                if code01_node is not None:
                    code01 = code01_node.text
                    code2name[code01] = name
                    name2code[name] = code01

print(code2name)
