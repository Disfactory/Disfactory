import pathlib
import xml.etree.ElementTree as ET


HERE = pathlib.Path(__file__).parent
code2name = {}
name2code = {}

for xml_path in HERE.glob("*.xml"):
    with xml_path.open("r") as f:
        tree = ET.fromstring(f.read())
        if tree is not None:
            for child in tree.getchildren():
                code = child.find("towncode").text
                name = child.find("townname").text
                code2name[code] = name
                name2code[name] = code

                code01_node = child.find("towncode01")
                if code01_node is not None:
                    code01 = code01_node.text
                    code2name[code01] = name
                    name2code[name] = code01
