from lxml import etree as ET
from par.beautiful_xml import indent

def generate_bpmn_process(data):
    user_tasks = data['user_tasks']
    script_tasks = data['script_tasks']
    lanes = data['lanes']
    events = data['events']
    flows = data['flows']
    process_name = data['process_name']
    gateways = data['gateways']

    # Корень
    NS = {'runa': 'http://runa.ru/wfe/xml'}
    NSMAP = {'runa': NS['runa']}
    root = ET.Element('definitions', nsmap=NSMAP)

    # Process
    process = ET.SubElement(root, 'process', name=process_name)

    # ExtensionElements процесса
    ext = ET.SubElement(process, 'extensionElements')
    ET.SubElement(ext, f"{{{NS['runa']}}}property", {'name': 'showSwimlane', 'value': 'none'})
    ET.SubElement(ext, f"{{{NS['runa']}}}property", {'name': 'accessType', 'value': 'Process'})
    ET.SubElement(ext, f"{{{NS['runa']}}}property", {'name': 'version', 'value': '4.6.0'})

    # LaneSet
    if lanes:
        lane_set = ET.SubElement(process, 'laneSet', {'id': 'laneSet1'})
        for lane in lanes:
            lane_elem = ET.SubElement(
                lane_set, 
                'lane', 
                {'id': f'ID{lane['id']}', 'name': lane['name']}
            )
            lane_ext = ET.SubElement(lane_elem, 'extensionElements')
            ET.SubElement(lane_ext, f"{{{NS['runa']}}}property",
                          name='class', 
                          value='ru.runa.wfe.extension.assign.DefaultAssignmentHandler')
            config = ET.SubElement(lane_ext, f"{{{NS['runa']}}}property", name='config')
            config.text = ET.CDATA("")
    else:
        ET.SubElement(process, 'laneSet')

    # gateways
    for gtw in gateways:
        gateway = ET.SubElement(
            process, 
            f"{gtw['type']}Gateway", 
            {'id': f"ID{gtw['id']}", 'name': gtw['name']}
        )
        if gtw.get('conditions'):
            gtw_ext = ET.SubElement(gateway, 'extensionElements')
            ET.SubElement(gtw_ext, f"{{{NS['runa']}}}property",
                          name='class', 
                          value='ru.runa.wfe.extension.decision.GroovyDecisionHandler')
            config = ET.SubElement(gtw_ext, f"{{{NS['runa']}}}property", name='config')
            config.text = ET.CDATA(gtw['conditions'])

    # events
    for event in events:
        if event['type'] == "start":
            if event['lane'] == "":
                event['lane'] = lanes[0]['name']
            evt = ET.SubElement(
                process, 
                'startEvent', 
                {'id': f"ID{event['id']}", 'name': event['name']}
            )
            evt_ext = ET.SubElement(evt, 'extensionElements')
            ET.SubElement(evt_ext, f"{{{NS['runa']}}}property", name='lane', value=event['lane'])
        else:
            evt = ET.SubElement(process, 'endEvent', {'id': f"ID{event['id']}", 'name': event['name']})

    # UserTasks
    for task in user_tasks:
        task_elem = ET.SubElement(
            process, 
            'userTask', 
            {'id': f"ID{task['id']}", 'name': task['name']}
        )
        task_ext = ET.SubElement(task_elem, 'extensionElements')
        ET.SubElement(task_ext, f"{{{NS['runa']}}}property", {'name': 'lane', 'value': task['lane']})

    # ScriptTasks
    for script in script_tasks:
        script_elem = ET.SubElement(
            process, 
            'scriptTask', 
            {'id': f"ID{script['id']}", 'name': script['name']}
        )
        script_ext = ET.SubElement(script_elem, 'extensionElements')
        ET.SubElement(
            script_ext, 
            f"{{{NS['runa']}}}property",
            {'name': 'class', 'value': 'ru.runa.wfe.service.handler.DoNothingTaskHandler'} 
        )
        config = ET.SubElement(script_ext, f"{{{NS['runa']}}}property", name='config')
        config.text = ET.CDATA("")

    # sequenceFlow
    for flow in flows:
        ET.SubElement(process, 'sequenceFlow', {
            'id': f"ID{flow['id']}",
            'name': flow['name'],
            'sourceRef': f"ID{flow['sourceRef']}",
            'targetRef': f"ID{flow['targetRef']}"
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