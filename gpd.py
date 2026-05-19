import xml.etree.cElementTree as ET
from beautiful_xml import indent


def get_process_name(data):
    if len(data) > 6 and data[6]:
        return str(data[6])
    return "result"


def generate_gpd(data):
    root = ET.Element("process-diagram", {
        "name": get_process_name(data),
        "notation": "bpmn",
        "rendered": "graphiti",
        "showActions": "false",
        "showGrid": "false",
        "width": "1274",
        "height": "653"
    })

    for task in data[3]:
        task_name, coordinates, lane_name, id = task
        x, y = coordinates

        ET.SubElement(root, "node", {
            "name": f"ID{id}",
            "x": str(x),
            "y": str(y),
            "width": "48",
            "height": "48"
        })

        for i in data[4]:
            if i[2] == f"ID{id}":
                ET.SubElement(root, "transition", {
                    "name": i[1]
                })

    for task in data[0]:
        task_name, coordinates, lane_name, id = task
        x, y = coordinates

        ET.SubElement(root, "node", {
            "name": f"ID{id}",
            "x": str(x),
            "y": str(y),
            "width": "174",
            "height": "94"
        })

        for i in data[4]:
            if i[2] == f"ID{id}":
                ET.SubElement(root, "transition", {
                    "name": i[1]
                })

    for task in data[1]:
        task_name, coordinates, id = task
        x, y = coordinates

        ET.SubElement(root, "node", {
            "name": f"ID{id}",
            "x": str(x),
            "y": str(y),
            "width": "174",
            "height": "94"
        })

        for i in data[4]:
            if i[2] == f"ID{id}":
                ET.SubElement(root, "transition", {
                    "name": i[1]
                })

    return root


def gpd_builder(data):
    filename = "gpd"
    root = generate_gpd(data)
    indent(root)
    xml_str = ET.tostring(root, encoding='unicode', method='xml')
    xml_str = xml_str.replace(' />', '/>')
    with open(f"./{filename}.xml", "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
        f.write(xml_str)
