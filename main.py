import os
import xml.etree.cElementTree as ET
import zipfile
from pathlib import Path

from variables_builder import variables_builder, gather_variables_data


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i



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

def generate_gpd(data):
    root = ET.Element("process-diagram", {
        "name": "result",
        "notation": "bpmn",
        "rendered": "graphiti",
        "showActions": "false",
        "showGrid": "false",
        "width": "1274",
        "height": "653"
    })

    # cоздание нод начала и конца
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

    # создание нод usertask
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


    # создание нод scripttask
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
    tree = ET.ElementTree(root)
    indent(root)
    xml_str = ET.tostring(tree.getroot(), encoding='unicode', method='xml')
    xml_str = xml_str.replace(' />', '/>')
    with open(f"./{filename}.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
        f.write(xml_str)
        f.close()


def generate_bpmn_process(data):
    user_data = []
    script_data = []
    lane_data = []
    flows = []
    user_data = data[0]
    script_data = data[1]
    lane_data = data[2]
    events = data[3]
    flows = data[4]

    # Корень
    root = ET.Element('definitions', {
        'xmlns': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
        'xmlns:bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
        'xmlns:omgdc': 'http://www.omg.org/spec/DD/20100524/DC',
        'xmlns:omgdi': 'http://www.omg.org/spec/DD/20100524/DI',
        'xmlns:runa': 'http://runa.ru/wfe/xml',
        'targetNamespace': 'http://runa.ru/wfe/xml'
    })

    # Process
    process = ET.SubElement(root, 'process', {'name': 'result', 'isExecutable': 'false'})

    # ExtensionElements процесса
    ext = ET.SubElement(process, 'extensionElements')
    ET.SubElement(ext, 'runa:property', {'name': 'showSwimlane', 'value': 'none'})
    ET.SubElement(ext, 'runa:property', {'name': 'accessType', 'value': 'Process'})
    ET.SubElement(ext, 'runa:property', {'name': 'version', 'value': '4.6.0'})

    # LaneSet
    if lane_data:
        lane_set = ET.SubElement(process, 'laneSet', {'id': 'laneSet1'})
        for lane in lane_data:
            lane_name = str(lane[0])
            lane_id = "ID" + str(lane[1])
            lane_elem = ET.SubElement(lane_set, 'lane', {'id': lane_id, 'name': lane_name})
            lane_ext = ET.SubElement(lane_elem, 'extensionElements')
            ET.SubElement(lane_ext, 'runa:property',
                          {'name': 'class', 'value': 'ru.runa.wfe.extension.assign.DoNothingTaskHandler'})
            config = ET.SubElement(lane_ext, 'runa:property', {'name': 'config', 'value': ''})
    else:
        ET.SubElement(process, 'laneSet')

    # start, end
    for event in events:
        event_name = str(event[0])
        event_id = "ID" + str(event[3])
        if 'начало' in event_name.lower() or 'start' in event_name.lower():
            ET.SubElement(process, 'startEvent', {'id': event_id, 'name': event_name})
        else:
            evt = ET.SubElement(process, 'endEvent', {'id': event_id, 'name': event_name})
            evt_ext = ET.SubElement(evt, 'extensionElements')
            ET.SubElement(evt_ext, 'runa:property', {'name': 'token', 'value': 'true'})

    # UserTasks
    for task in user_data:
        task_name = str(task[0])
        lane_name = str(task[2])
        task_id = "ID" + str(task[3])
        task_elem = ET.SubElement(process, 'userTask', {'id': task_id, 'name': task_name})
        task_ext = ET.SubElement(task_elem, 'extensionElements')
        ET.SubElement(task_ext, 'runa:property', {'name': 'lane', 'value': lane_name})

    # ScriptTasks
    for script in script_data:
        script_name = str(script[0])
        script_id = "ID" + str(script[2])
        script_elem = ET.SubElement(process, 'scriptTask', {'id': script_id, 'name': script_name})
        script_ext = ET.SubElement(script_elem, 'extensionElements')
        ET.SubElement(script_ext, 'runa:property',
                      {'name': 'class', 'value': 'ru.runa.wfe.service.handler.DoNothingTaskHandler'})
        config = ET.SubElement(script_ext, 'runa:property', {'name': 'config'})

    # flows_element = ET.SubElement(process_root, "flows")
    for flow in flows:
        # flow ожидается в формате: ["ID111112", "tr111112", "ID1", "ID3"]
        flow_id = flow[0]
        flow_name = flow[1]
        flow_ref = flow[2]
        flow_target = flow[3]
        ET.SubElement(process, 'sequenceFlow', {
            'id': flow_id,
            'name': flow_name,
            'sourceRef': flow_ref,
            'targetRef': flow_target
        })

    return root

def process_definition_builder(data):
    filename = "processdefinition"
    root = generate_bpmn_process(data)
    tree = ET.ElementTree(root)
    indent(root)
    xml_str = ET.tostring(tree.getroot(), encoding='unicode', method='xml')
    xml_str = xml_str.replace(' />', '/>')
    with open(f"./{filename}.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
        f.write(xml_str)
        f.close()

def gather_data():
    print(f"Введите количество usertask")
    usertask = int(input())

    print(f"Введите количество scripttask")
    scripttask = int(input())

    events = [["startEvent", [48, 48], '' ,1], ["endEvent", [48, 48], '', 2]]
    user_data = []
    script_data = []
    lane_data = []
    flows = []
    data = [user_data, script_data, lane_data, events, flows]
    id = 3

    for i in range(usertask):
        data[0].append([])
        print(f"введите название элемента usertask {i + 1}")
        name = str(input())
        data[0][-1].append(name)

        coords = []
        print(f"введите X координату элемента {name}")
        coords.append(int(input()))
        print(f"введите Y координату элемента {name}")
        coords.append(int(input()))
        data[0][-1].append(coords)

        print(f"введите название lane для элемента {name}")
        lane = str(input())
        data[0][-1].append(lane)
        data[0][-1].append(id)
        id+=1
        lane_data.append([lane, usertask+scripttask+3+len(lane_data)])

    for i in range(scripttask):
        data[1].append([])
        print(f"введите название элемента scripttask {i + 1}")
        name = str(input())
        data[1][-1].append(name)

        coords = []
        print(f"введите X координату элемента {name}")
        coords.append(int(input()))
        print(f"введите Y координату элемента {name}")
        coords.append(int(input()))
        data[1][-1].append(coords)
        data[1][-1].append(id)
        id+=1

    print(f"описываем flow процессы")
    print(f"формат ввода '1 2' задача 1 переходит в задачу 2")
    print(f"чтобы завершить запись переходов введите 'done'")
    print(f"список возможных точек перехода и их айди")
    # add ID to id
    id = "111112"
    # add tr to name
    name = "111112"
    print("StartNode", " " , 1)
    print("EndNode", " " , 2)
    for i in data[0]:
        print(i[0], "  ", i[3])
    for i in data[1]:
        print(i[0], "  ", i[2])
    while True:
        word = str(input()).split()
        if len(word) == 1:
            break

        sourceRef = word[0]
        targetRef = word[1]
        flows.append(["ID" + id,"tr" + name,"ID" + sourceRef, "ID" + targetRef])
        id = str(int(id) + 1)
        name = str(int(name) + 1)

    return data

def create_zip_with_par_extension(file_list, output_name):
    temp_zip = f"{output_name}.zip"
    final_par = f"{output_name}.par"

    try:
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_list:
                if os.path.exists(file_path):
                    zipf.write(file_path, arcname=os.path.basename(file_path))
                    print(f"Added: {file_path}")
                else:
                    print(f"Warning: File not found - {file_path}")

        print(f"\nCreated temporary zip: {temp_zip}")

        if os.path.exists(final_par):
            os.remove(final_par)
        os.rename(temp_zip, final_par)
        print(f"Renamed to: {final_par}")

        return final_par

    except Exception as e:
        print(f"Error: {e}")
        if os.path.exists(temp_zip):
            os.remove(temp_zip)
        return None

def main():
    empty_builder("comments", "versions")
    empty_builder("forms", "forms")

    data = gather_data()
    variables_data = gather_variables_data()

    gpd_builder(data)
    process_definition_builder(data)
    variables_builder(variables_data)

    print(data)

    files_to_archive = [
        "gpd.xml",
        "processdefinition.xml",
        "comments.xml",
        "forms.xml",
        "variables.xml"
    ]

    result = create_zip_with_par_extension(
        file_list=files_to_archive,
        output_name="result"
    )
    if result:
        print(f"\nSuccessfully created: {result}")
        for i in files_to_archive:
            os.remove(i)

        import zipfile

        try:
            with zipfile.ZipFile(result, 'r') as zipf:
                print(f"\nContents of {result}:")
                for file_info in zipf.infolist():
                    print(f"  {file_info.filename} ({file_info.file_size} bytes)")
        except zipfile.BadZipFile:
            print(f"\nWarning: {result} is not a valid zip file!")

main()

# 1
# 1
# UserTaskName1
# 200
# 48
# UserTaskLaneName1
# ScriptTaskName1
# 400
# 48
# 1 3
# 3 4
# 4 2
# done
