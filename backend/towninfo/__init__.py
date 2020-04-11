import pathlib
import xml.etree.ElementTree as ET


HERE = pathlib.Path(__file__).home()
code2name = {}
name2code = {}

for xml_path in HERE.glob('*.xml'):
    with xml_path.open('r') as f:
        tree = ET.fromstring(f.read())
        if tree:
            for child in tree.getchildren():
                code = child[1].text
                name = child[2].text
                code2name[code] = name
                name2code[name] = code


