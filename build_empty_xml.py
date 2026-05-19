import xml.etree.cElementTree as ET
from beautiful_xml import indent

def empty_builder(filename, text):
    root = ET.Element(text)
    tree = ET.ElementTree(root)
    indent(root)
    xml_str = ET.tostring(tree.getroot(), encoding='unicode', method='xml')
    xml_str = xml_str.replace(' />', '/>')
    with open(f"./{filename}.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
        f.write(xml_str)
        f.write('\n')
        f.close()