import xml.etree.cElementTree as ET
from beautiful_xml import indent


def get_process_name(data):
    if len(data) > 6 and data[6]:
        return str(data[6])
    return "result"


def generate_bpmn_process(data):
    user_data = data[0]
    script_data = data[1]
    lane_data = data[2]
    events = data[3]
    flows = data[4]

    root = ET.Element('definitions', {
        'xmlns': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
        'xmlns:bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
        'xmlns:omgdc': 'http://www.omg.org/spec/DD/20100524/DC',
        'xmlns:omgdi': 'http://www.omg.org/spec/DD/20100524/DI',
        'xmlns:runa': 'http://runa.ru/wfe/xml',
        'targetNamespace': 'http://runa.ru/wfe/xml'
    })

    process = ET.SubElement(root, 'process', {'name': get_process_name(data), 'isExecutable': 'false'})

    ext = ET.SubElement(process, 'extensionElements')
    ET.SubElement(ext, 'runa:property', {'name': 'showSwimlane', 'value': 'none'})
    ET.SubElement(ext, 'runa:property', {'name': 'accessType', 'value': 'Process'})
    ET.SubElement(ext, 'runa:property', {'name': 'version', 'value': '4.6.0'})

    if lane_data:
        lane_set = ET.SubElement(process, 'laneSet', {'id': 'laneSet1'})
        for lane in lane_data:
            lane_name = str(lane[0])
            lane_id = "ID" + str(lane[1])
            lane_elem = ET.SubElement(lane_set, 'lane', {'id': lane_id, 'name': lane_name})
            lane_ext = ET.SubElement(lane_elem, 'extensionElements')
            ET.SubElement(lane_ext, 'runa:property', {
                'name': 'class',
                'value': 'ru.runa.wfe.extension.assign.DoNothingTaskHandler'
            })
            ET.SubElement(lane_ext, 'runa:property', {'name': 'config', 'value': ''})
    else:
        ET.SubElement(process, 'laneSet')

    for event in events:
        event_name = str(event[0])
        event_id = "ID" + str(event[3])
        if 'начало' in event_name.lower() or 'start' in event_name.lower():
            ET.SubElement(process, 'startEvent', {'id': event_id, 'name': event_name})
        else:
            evt = ET.SubElement(process, 'endEvent', {'id': event_id, 'name': event_name})
            evt_ext = ET.SubElement(evt, 'extensionElements')
            ET.SubElement(evt_ext, 'runa:property', {'name': 'token', 'value': 'true'})

    for task in user_data:
        task_name = str(task[0])
        lane_name = str(task[2])
        task_id = "ID" + str(task[3])
        task_elem = ET.SubElement(process, 'userTask', {'id': task_id, 'name': task_name})
        task_ext = ET.SubElement(task_elem, 'extensionElements')
        ET.SubElement(task_ext, 'runa:property', {'name': 'lane', 'value': lane_name})

    for script in script_data:
        script_name = str(script[0])
        script_id = "ID" + str(script[2])
        script_elem = ET.SubElement(process, 'scriptTask', {'id': script_id, 'name': script_name})
        script_ext = ET.SubElement(script_elem, 'extensionElements')
        ET.SubElement(script_ext, 'runa:property', {
            'name': 'class',
            'value': 'ru.runa.wfe.service.handler.DoNothingTaskHandler'
        })
        ET.SubElement(script_ext, 'runa:property', {'name': 'config', 'value': ''})

    for flow in flows:
        ET.SubElement(process, 'sequenceFlow', {
            'id': flow[0],
            'name': flow[1],
            'sourceRef': flow[2],
            'targetRef': flow[3]
        })

    return root


def process_definition_builder(data):
    filename = "processdefinition"
    root = generate_bpmn_process(data)
    indent(root)
    xml_str = ET.tostring(root, encoding='unicode', method='xml')
    xml_str = xml_str.replace(' />', '/>')
    with open(f"./{filename}.xml", "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
        f.write(xml_str)
